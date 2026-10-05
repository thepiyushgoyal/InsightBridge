# InsightBridge - Analytics Knowledge Copilot

InsightBridge is a beginner-friendly, resume-presentable Streamlit RAG application for answering analytics and SQL questions from a small internal knowledge base.

The fictional knowledge base represents an e-commerce analytics team and includes a data dictionary, KPI definitions, dashboard guidance, SQL examples, data-quality rules, and a small product catalog.

## What It Does

- Loads local Markdown, TXT, CSV, SQL, and optional PDF documents.
- Splits documents into chunks with LangChain.
- Creates OpenAI embeddings.
- Stores embeddings in a local FAISS vector index.
- Lets users ask natural-language analytics questions.
- Supports Similarity and MMR retrieval.
- Generates grounded answers with source citations.
- Refuses to invent unsupported schemas, metrics, business rules, or unsafe SQL.
- Can execute generated read-only SQLite `SELECT` queries against a local sample database and display the result table.

## Architecture Flow

```text
data/knowledge_base/
        |
        v
Document Loaders
        |
        v
RecursiveCharacterTextSplitter
        |
        v
OpenAI Embeddings
        |
        v
FAISS Local Vector Store
        |
        v
Retriever: Similarity or MMR
        |
        v
Grounded Prompt + OpenAI Chat Model
        |
        v
Streamlit Answer + Source Citations
        |
        v
Optional SQL Guardrails + SQLite Query Result
```

## Tech Stack

- Python
- Streamlit
- LangChain
- OpenAI embeddings and chat models
- FAISS local vector database
- python-dotenv

The Streamlit sidebar defaults to `gpt-5.6-terra`, which is intended as a balanced OpenAI model choice. You can change the model name from the UI.

## Setup

Use Python 3.10 or newer.

```powershell
cd C:\Coding\InsightBridge
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `.env` and set your OpenAI API key:

```text
OPENAI_API_KEY=your_real_api_key
```

## Run

```powershell
streamlit run app.py
```

In the app:

1. Click **Build / Rebuild Knowledge Base** in the sidebar.
2. Click **Create / Refresh Sample Database** in the sidebar.
3. Choose **Similarity** or **MMR** retrieval.
4. Keep **Run generated SELECT SQL** turned on if you want executable SQL output.
5. Ask a question from the main chat input.

You can also create the sample SQLite database from PowerShell:

```powershell
python -c "from src.database import initialize_sample_database; print(initialize_sample_database())"
```

## No-API Smoke Test

After installing dependencies, run:

```powershell
python evaluation/smoke_test.py
```

This validates local document loading and chunking without calling OpenAI.

## Example Questions

- What is the difference between Revenue and Net Revenue?
- Which tables do I join to analyze product revenue?
- Write a SQL query for monthly net revenue.
- What data-quality rules should I apply before calculating refund rate?
- Can you generate SQL for Conversion Rate?
- Show monthly active customers by month.
- Show the top products by units sold.

## Limitations

- The knowledge base is intentionally small and fictional.
- The FAISS index is local and rebuilt manually from the sidebar.
- SQL safety uses simple read-only guardrails and a read-only SQLite connection, not a full SQL parser.
- Conversion Rate cannot be queried from the documented schema because no sessions table is provided.
- No authentication, database connection, cloud deployment, or document scheduler is included.

## Resume-Ready Project Description

Built **InsightBridge**, a Streamlit-based Retrieval-Augmented Generation application that answers analytics and SQL questions from a fictional e-commerce knowledge base. Implemented document loading, chunking, OpenAI embeddings, FAISS vector search, Similarity/MMR retrieval, grounded answer generation, source citations, read-only SQL validation, SQLite query execution, and tabular result display. Designed the knowledge base with data dictionaries, KPI definitions, SQL examples, dashboard guidance, and data-quality rules to demonstrate practical analytics and ML engineering skills.

## Suggested Next Upgrades

- Add automated RAG evaluation with expected-answer checks.
- Add stronger SQL validation using a SQL parser.
- Add document upload from the Streamlit UI.
- Add metadata filters by document type.
- Add a lightweight evaluation dashboard for retrieval quality.
