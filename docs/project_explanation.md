# InsightBridge Project Explanation

InsightBridge is a small Retrieval-Augmented Generation application. In simple terms, it lets a user ask questions about a fictional e-commerce analytics knowledge base, retrieves the most relevant documentation, and asks an OpenAI chat model to answer only from that retrieved context.

## Component Walkthrough

### Document Loaders

The loaders in `src/loaders.py` read files from `data/knowledge_base/`. The project supports Markdown, TXT, SQL, CSV, and PDF files. Markdown, TXT, and SQL files are loaded as plain text. CSV files are loaded row by row. PDF support is included through `PyPDFLoader` so a user can add PDF documentation later.

The important idea: before a model can answer from documents, the documents need to be converted into text objects with metadata such as the source filename.

### Chunking

The ingestion code uses `RecursiveCharacterTextSplitter`. Instead of embedding an entire long document at once, the app splits documents into smaller overlapping chunks.

Chunks make retrieval more precise. If a user asks about Refund Rate, the retriever can bring back the specific Refund Rate definition instead of the entire KPI document.

### Embeddings

Embeddings turn text into numeric vectors. Text with similar meaning should have vectors that are close together. InsightBridge uses OpenAI embeddings through `langchain-openai`.

For example, the question "How do I calculate AOV?" should be close to the chunk that defines Average Order Value.

### FAISS

FAISS is the local vector database. During ingestion, the app stores document chunk embeddings in `data/faiss_index/`. This folder is ignored by Git because it can be rebuilt from the source documents.

FAISS lets the app quickly find chunks whose embeddings are close to the user's question.

### Sample SQLite Database

The file `src/database.py` creates a small local database at `data/sample_database/ecommerce.db`. It has the same fictional business tables as the documentation: `customers`, `orders`, `order_items`, `products`, `payments`, and `refunds`.

This gives the project a realistic second half. The app does not only generate SQL; it can also run safe `SELECT` queries and show the result as a table.

### Retriever

The retriever is the search layer over FAISS. The app supports two retrieval modes:

- Similarity search returns the chunks most similar to the question.
- MMR retrieval tries to balance relevance and diversity, which can help when several chunks are very similar.

The `top-k` sidebar control decides how many chunks are returned.

### Prompt Grounding

The prompt in `src/prompts.py` tells the model to use only the retrieved context. It also tells the model not to invent table names, column names, metric definitions, or business rules.

For SQL questions, the prompt allows only read-only `SELECT` statements. If the schema does not support a requested query, the model should say it cannot produce a supported query.

For runnable SQL, the prompt asks the model to use SQLite-compatible syntax. That means using table names like `orders` instead of `analytics.orders`, and using `strftime('%Y-%m', order_date)` for monthly grouping instead of warehouse functions like `DATE_TRUNC`.

### SQL Guardrails and Execution

The SQL execution logic is in `src/sql_runner.py`.

It does four things:

1. Extracts the first SQL query from the model answer.
2. Normalizes small differences, such as removing the `analytics.` prefix.
3. Blocks unsafe statements like `DELETE`, `UPDATE`, `DROP`, `ALTER`, and `INSERT`.
4. Executes the query against SQLite using a read-only connection.

If the generated SQL is valid, Streamlit displays the result with `st.dataframe`. If the SQL is unsafe or unsupported, the app shows a warning instead of running it.

### Citations

The app displays retrieved sources below every answer. Each source includes:

- source filename
- chunk or page reference
- a short preview of the retrieved text

This makes the answer easier to trust and easier to debug.

### Streamlit Flow

The Streamlit app has one main flow:

1. Load the `.env` file.
2. Let the user build or rebuild the FAISS index from the sidebar.
3. Let the user choose Similarity or MMR retrieval.
4. Accept a natural-language analytics or SQL question.
5. Retrieve relevant chunks.
6. Generate a grounded answer.
7. Extract a SQL query if the answer contains one.
8. Validate and run the query if SQL execution is enabled.
9. Show the result table and citations.

## Interview-Friendly Presentation

Here is a concise way to describe the project:

"InsightBridge is a Streamlit RAG application for analytics documentation. I created a small fictional e-commerce knowledge base with schema docs, KPI definitions, SQL examples, dashboard guidance, and data-quality rules. The app loads those files, chunks them with LangChain, embeds them with OpenAI embeddings, stores the vectors in a local FAISS index, and retrieves relevant chunks when a user asks a question. The answer prompt is grounded so the model must cite the retrieved sources and avoid inventing unsupported SQL or metric definitions. For SQL questions, the app can validate and run read-only SQLite queries against a local sample database and display the results."

If asked why this is useful, say:

"Analytics teams often have scattered definitions for metrics and schema rules. A small RAG assistant can help analysts quickly find trusted definitions and SQL patterns while reducing the risk of inconsistent dashboard logic."

If asked about limitations, say:

"This is an MVP. It uses a small local FAISS index, does not include access control, and uses lightweight SQL guardrails rather than a full SQL parser. A production version would need stronger query validation, evaluation automation, document refresh workflows, and observability."
