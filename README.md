# InsightBridge

InsightBridge is a Streamlit-based Retrieval-Augmented Generation (RAG) analytics knowledge copilot for a fictional e-commerce team. It answers questions about metric definitions, data quality, schemas, SQL patterns, and dashboard guidance using the checked-in local knowledge base.

## Problem statement

Analytics definitions and SQL guidance are often spread across several documents. InsightBridge provides a small, grounded interface for finding relevant documentation and, when appropriate, generating and running a read-only query against a local SQLite sample database.

## Features

- Loads Markdown, TXT, CSV, SQL, and PDF files from `data/knowledge_base/`.
- Chunks documents and creates OpenAI `text-embedding-3-small` embeddings.
- Stores embeddings in a local FAISS index at `data/faiss_index/`.
- Supports Similarity and MMR retrieval with configurable top-k results.
- Generates grounded answers with retrieved source filenames and references.
- Generates SQLite-compatible SQL for supported questions.
- Validates and executes only read-only `SELECT`/`WITH` SQL against the sample database.
- Runs locally and on Heroku with the OpenAI key supplied through the environment.

## Architecture

```text
Knowledge-base files
        |
        v
Document loaders -> text chunks -> OpenAI embeddings -> local FAISS index
                                                     |
                                                     v
Question -> Similarity/MMR retriever -> grounded OpenAI chat prompt
                                                     |
                                                     v
                                      Answer, citations, optional SQL
                                                     |
                                                     v
                                      Read-only SQLite result table
```

## Tech stack

- Python 3.12
- Streamlit
- LangChain
- OpenAI embeddings and chat model
- FAISS CPU
- Pandas
- PyPDF
- SQLite
- `python-dotenv`

## Project structure

```text
InsightBridge/
├── app.py
├── Procfile
├── .env.example
├── .python-version
├── requirements.txt
├── data/
│   ├── knowledge_base/       # Source documents used by RAG
│   └── sample_database/      # SQLite demo database
├── docs/                     # Project explanation
├── evaluation/               # Smoke test and evaluation questions
└── src/
    ├── database.py
    ├── ingestion.py
    ├── loaders.py
    ├── prompts.py
    ├── rag_chain.py
    └── sql_runner.py
```

## Knowledge base and RAG workflow

The knowledge base contains a data dictionary, metric definitions, dashboard guidance, SQL examples, data-quality rules, SQLite execution notes, a product catalog, and a PDF reference. The application loads these files, splits them with `RecursiveCharacterTextSplitter`, embeds the chunks, and persists them in FAISS. Each question retrieves either similar or diverse relevant chunks, then passes those chunks to the grounded chat prompt.

The sidebar provides Similarity or MMR retrieval and a top-k control. Retrieved source filenames, page/chunk references, and previews are displayed with each answer.

## SQL safety

The prompt requests only one read-only query. Before execution, `src/sql_runner.py` normalizes SQLite compatibility details, rejects multiple statements, requires `SELECT` or `WITH`, blocks write/administrative keywords, and connects to SQLite in read-only mode. SQL execution can also be disabled from the sidebar. These are lightweight application guardrails, not a full SQL parser.

## Local installation

From the project root in PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `.env` locally and set your own key:

```env
OPENAI_API_KEY=your_real_api_key
```

Never commit `.env` or any real key.

## Environment variables

| Variable | Required for | Example |
| --- | --- | --- |
| `OPENAI_API_KEY` | Embeddings and chat responses | `your_openai_api_key_here` |

Local development loads `.env` with `python-dotenv`. Heroku uses a Config Var.

## Running locally

```powershell
streamlit run app.py
```

On first startup, if `data/faiss_index/` is absent, the app automatically builds the index from the checked-in knowledge base and saves it locally. The build is cached for the Streamlit process so reruns do not repeat the embedding operation. The sidebar still includes **Build / Rebuild Knowledge Base** for an intentional rebuild. The sample SQLite database is already included; the sidebar can also recreate it.

## Smoke test

The smoke test does not call OpenAI. It checks local knowledge-base loading and chunking:

```powershell
python evaluation/smoke_test.py
```

## GitHub setup

Run these commands from the project root after reviewing the files:

```bash
git init -b main
git add .
git commit -m "Initial commit - InsightBridge"
git remote add origin <YOUR_GITHUB_REPO_URL>
git push -u origin main
```

`.env`, `.venv/`, `data/faiss_index/`, and `.streamlit/secrets.toml` must not be committed. The knowledge base, source code, documentation, evaluation files, and SQLite sample database are intentionally kept in the repository.

## Heroku deployment

The root `Procfile` starts Streamlit on Heroku's assigned `$PORT` and listens on `0.0.0.0`:

```text
web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
```

Create and deploy the app with:

```bash
heroku login
heroku create <APP_NAME>
heroku config:set OPENAI_API_KEY="YOUR_API_KEY"
git push heroku main
heroku open
```

The OpenAI key must be a Heroku Config Var, not a GitHub file. Because FAISS is generated and ignored, a fresh Heroku dyno automatically creates `data/faiss_index/` during startup using the checked-in knowledge base. Heroku's filesystem is ephemeral, so the index may be rebuilt after a dyno restart or redeploy; embedding API usage can result.

## Limitations

- The knowledge base and SQLite data are small, local, and fictional.
- The FAISS store is local rather than a managed vector database.
- There is no authentication, monitoring, production database connection, document scheduler, or automated RAG evaluation.
- SQL validation uses application guardrails rather than a complete SQL parser.
- Answers depend on the configured OpenAI services and model name entered in the sidebar.

## Future improvements

- Add stronger SQL parsing and validation.
- Add document upload and refresh workflows.
- Add metadata filters and automated retrieval/answer evaluation.
- Move embeddings and application data to managed production services when needed.

## Author / contribution

InsightBridge is a portfolio project. Contributions are welcome through issues and pull requests, provided they preserve the read-only SQL design and do not add secrets or generated FAISS artifacts to version control.
