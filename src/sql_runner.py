from __future__ import annotations

import re
import sqlite3
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from src.database import DEFAULT_DATABASE_PATH


FORBIDDEN_SQL_KEYWORDS = {
    "alter",
    "attach",
    "create",
    "delete",
    "detach",
    "drop",
    "insert",
    "merge",
    "pragma",
    "replace",
    "truncate",
    "update",
    "vacuum",
}


@dataclass
class SQLExecutionResult:
    sql: str
    dataframe: pd.DataFrame


def extract_sql_query(text: str) -> str | None:
    """Extract the first SQL query from a model answer."""
    fenced_match = re.search(r"```(?:sql)?\s*(.*?)```", text, flags=re.IGNORECASE | re.DOTALL)
    if fenced_match:
        return fenced_match.group(1).strip()

    query_match = re.search(r"\b(WITH|SELECT)\b[\s\S]*", text, flags=re.IGNORECASE)
    if query_match:
        return query_match.group(0).strip()

    return None


def run_read_only_query(
    sql: str,
    db_path: Path = DEFAULT_DATABASE_PATH,
    max_rows: int = 100,
) -> SQLExecutionResult:
    """Validate and execute a read-only SQLite query."""
    if not db_path.exists():
        raise FileNotFoundError(
            f"Sample database not found at {db_path}. Create it from the sidebar first."
        )

    normalized_sql = normalize_sql_for_sqlite(sql)
    validate_read_only_sql(normalized_sql)

    connection_uri = f"file:{db_path.as_posix()}?mode=ro"
    with sqlite3.connect(connection_uri, uri=True) as conn:
        dataframe = pd.read_sql_query(normalized_sql, conn)

    if len(dataframe) > max_rows:
        dataframe = dataframe.head(max_rows)

    return SQLExecutionResult(sql=normalized_sql, dataframe=dataframe)


def normalize_sql_for_sqlite(sql: str) -> str:
    """Apply small compatibility fixes for local SQLite execution."""
    cleaned = sql.strip()
    cleaned = re.sub(r"```(?:sql)?", "", cleaned, flags=re.IGNORECASE).replace("```", "")
    cleaned = re.sub(r"\banalytics\.", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(
        r"DATE_TRUNC\(\s*['\"]month['\"]\s*,\s*([^)]+?)\s*\)",
        r"strftime('%Y-%m', \1)",
        cleaned,
        flags=re.IGNORECASE,
    )
    return cleaned.strip().rstrip(";")


def validate_read_only_sql(sql: str) -> None:
    """Allow only a single read-only SELECT or WITH query."""
    compact_sql = _remove_sql_comments(sql).strip()
    if not compact_sql:
        raise ValueError("No SQL query was found to execute.")

    if ";" in compact_sql:
        raise ValueError("Only one SQL statement is allowed.")

    first_token = compact_sql.split(None, 1)[0].lower()
    if first_token not in {"select", "with"}:
        raise ValueError("Only read-only SELECT queries are allowed.")

    tokens = set(re.findall(r"\b[a-zA-Z_]+\b", compact_sql.lower()))
    forbidden = sorted(tokens.intersection(FORBIDDEN_SQL_KEYWORDS))
    if forbidden:
        raise ValueError(f"Unsafe SQL keyword found: {', '.join(forbidden)}")


def _remove_sql_comments(sql: str) -> str:
    without_block_comments = re.sub(r"/\*.*?\*/", "", sql, flags=re.DOTALL)
    return re.sub(r"--.*?$", "", without_block_comments, flags=re.MULTILINE)
