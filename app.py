from __future__ import annotations

from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

from src.ingestion import (
    DEFAULT_INDEX_DIR,
    DEFAULT_KNOWLEDGE_BASE_DIR,
    build_vector_index,
    index_exists,
)
from src.database import DEFAULT_DATABASE_PATH, initialize_sample_database
from src.rag_chain import answer_question
from src.sql_runner import run_read_only_query


load_dotenv()

st.set_page_config(
    page_title="InsightBridge",
    page_icon=":bar_chart:",
    layout="wide",
)


SUGGESTED_QUESTIONS = [
    "What is the difference between Revenue and Net Revenue?",
    "Which tables do I join to analyze product revenue?",
    "Write a SQL query for monthly net revenue.",
    "Show monthly active customers by month.",
    "What data-quality rules should I apply before calculating refund rate?",
    "Show the top products by units sold.",
]


def main() -> None:
    index_ready = _initialize_index()

    st.title("InsightBridge")
    st.caption("Analytics Knowledge Copilot for e-commerce metrics, schema, SQL, and dashboard guidance.")

    with st.sidebar:
        st.header("Knowledge Base")
        st.write(f"Documents: `{DEFAULT_KNOWLEDGE_BASE_DIR.as_posix()}`")

        if st.button("Build / Rebuild Knowledge Base", use_container_width=True):
            _build_index()

        st.divider()
        retriever_method = st.radio("Retriever", ["Similarity", "MMR"], index=0)
        top_k = st.slider("Top-k results", min_value=2, max_value=8, value=4)
        model_name = st.text_input("OpenAI model", value="gpt-5.5")

        if index_exists(DEFAULT_INDEX_DIR):
            st.success("Vector index is ready.")
        else:
            st.info("Build the knowledge base before asking questions.")

        st.divider()
        st.header("SQL Demo Database")
        if st.button("Create / Refresh Sample Database", use_container_width=True):
            _initialize_database()
        run_sql = st.toggle("Run generated SELECT SQL", value=True)
        if DEFAULT_DATABASE_PATH.exists():
            st.success("Sample database is ready.")
        else:
            st.info("Create the sample database before running SQL.")

    st.subheader("Suggested Questions")
    selected_question = _question_buttons(SUGGESTED_QUESTIONS)

    question = st.chat_input("Ask an analytics or SQL question")
    if selected_question:
        question = selected_question

    if not index_ready:
        st.info("The vector index is not ready. Check the error above or use the sidebar button to retry.")
        return

    if question:
        _answer_question(question, model_name, retriever_method, top_k, run_sql)


@st.cache_resource(show_spinner=False)
def _ensure_index() -> None:
    """Build the ignored local FAISS index once when a fresh instance needs it."""
    if not index_exists(DEFAULT_INDEX_DIR):
        build_vector_index(
            knowledge_base_dir=DEFAULT_KNOWLEDGE_BASE_DIR,
            index_dir=DEFAULT_INDEX_DIR,
        )


def _initialize_index() -> bool:
    """Ensure a usable index exists without rebuilding it on every rerun."""
    if index_exists(DEFAULT_INDEX_DIR):
        return True

    try:
        with st.spinner("No FAISS index found. Building it from the knowledge base..."):
            _ensure_index()
        return index_exists(DEFAULT_INDEX_DIR)
    except Exception as exc:
        st.error(f"Unable to initialize the FAISS index: {exc}")
        return False


def _build_index() -> None:
    try:
        with st.spinner("Building FAISS index from knowledge base documents..."):
            chunk_count = build_vector_index(
                knowledge_base_dir=DEFAULT_KNOWLEDGE_BASE_DIR,
                index_dir=DEFAULT_INDEX_DIR,
            )
        st.success(f"Knowledge base rebuilt with {chunk_count} chunks.")
    except Exception as exc:
        st.error(str(exc))


def _initialize_database() -> None:
    try:
        db_path = initialize_sample_database(DEFAULT_DATABASE_PATH)
        st.success(f"Sample database ready: {db_path.as_posix()}")
    except Exception as exc:
        st.error(str(exc))


def _question_buttons(questions: list[str]) -> str | None:
    cols = st.columns(2)
    for index, question in enumerate(questions):
        if cols[index % 2].button(question, use_container_width=True):
            return question
    return None


def _answer_question(
    question: str,
    model_name: str,
    retriever_method: str,
    top_k: int,
    run_sql: bool,
) -> None:
    with st.chat_message("user"):
        st.write(question)

    try:
        with st.spinner("Retrieving context and generating a grounded answer..."):
            response = answer_question(
                question=question,
                model_name=model_name,
                retriever_method=retriever_method,
                top_k=top_k,
                index_dir=Path(DEFAULT_INDEX_DIR),
            )
    except Exception as exc:
        st.error(str(exc))
        return

    with st.chat_message("assistant"):
        st.markdown(response.answer)

    if response.sql_query:
        st.subheader("SQL Execution")
        st.code(response.sql_query, language="sql")

        if run_sql:
            try:
                result = run_read_only_query(response.sql_query, DEFAULT_DATABASE_PATH)
                st.dataframe(result.dataframe, use_container_width=True)
                st.caption(f"Returned {len(result.dataframe)} row(s).")
            except Exception as exc:
                st.warning(f"SQL was generated but not executed: {exc}")
        else:
            st.info("SQL execution is turned off in the sidebar.")

    with st.expander("Retrieved Sources", expanded=True):
        for idx, source in enumerate(response.sources, start=1):
            st.markdown(f"**{idx}. {source.source} - {source.reference}**")
            st.caption(source.preview)


if __name__ == "__main__":
    main()
