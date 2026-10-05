from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

from src.ingestion import DEFAULT_INDEX_DIR, load_vector_index
from src.prompts import GROUNDED_ANSWER_PROMPT
from src.sql_runner import extract_sql_query


@dataclass
class RetrievedSource:
    source: str
    reference: str
    preview: str


@dataclass
class RAGResponse:
    answer: str
    sources: list[RetrievedSource]
    sql_query: str | None = None


def answer_question(
    question: str,
    model_name: str = "gpt-5.5",
    retriever_method: str = "Similarity",
    top_k: int = 4,
    index_dir: Path = DEFAULT_INDEX_DIR,
) -> RAGResponse:
    """Retrieve relevant chunks and generate a grounded answer."""
    vector_store = load_vector_index(index_dir)
    retriever = _create_retriever(vector_store, retriever_method, top_k)
    docs = retriever.invoke(question)

    context = _format_context(docs)
    llm = ChatOpenAI(model=model_name, temperature=0)
    chain = GROUNDED_ANSWER_PROMPT | llm | StrOutputParser()
    answer = chain.invoke({"context": context, "question": question})

    return RAGResponse(
        answer=answer,
        sources=_format_sources(docs),
        sql_query=extract_sql_query(answer),
    )


def _create_retriever(vector_store, retriever_method: str, top_k: int):
    search_kwargs = {"k": top_k}
    if retriever_method == "MMR":
        search_kwargs = {"k": top_k, "fetch_k": max(20, top_k * 4), "lambda_mult": 0.5}
        return vector_store.as_retriever(search_type="mmr", search_kwargs=search_kwargs)

    return vector_store.as_retriever(search_type="similarity", search_kwargs=search_kwargs)


def _format_context(docs: list[Document]) -> str:
    blocks = []
    for doc in docs:
        source = doc.metadata.get("source", "unknown")
        chunk_id = doc.metadata.get("chunk_id", "unknown")
        page = doc.metadata.get("page")
        reference = f"page {page + 1}" if isinstance(page, int) else f"chunk {chunk_id}"
        blocks.append(
            f"Source: {source} ({reference})\n"
            f"Content:\n{doc.page_content.strip()}"
        )
    return "\n\n---\n\n".join(blocks)


def _format_sources(docs: list[Document]) -> list[RetrievedSource]:
    sources: list[RetrievedSource] = []
    for doc in docs:
        source = doc.metadata.get("source", "unknown")
        chunk_id = doc.metadata.get("chunk_id", "unknown")
        page = doc.metadata.get("page")
        reference = f"page {page + 1}" if isinstance(page, int) else f"chunk {chunk_id}"
        preview = " ".join(doc.page_content.strip().split())
        sources.append(
            RetrievedSource(
                source=source,
                reference=reference,
                preview=preview[:350] + ("..." if len(preview) > 350 else ""),
            )
        )
    return sources
