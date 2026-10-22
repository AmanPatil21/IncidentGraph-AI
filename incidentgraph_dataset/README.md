# IncidentGraph AI — Synthetic RAG Starter Dataset

**Entirely fictional.** No real customer data or internal company documents.

## Contents
- `incidents/`: 10 Markdown incident reports
- `runbooks/`: 10 Markdown troubleshooting guides
- `postmortems/`: 10 Markdown incident postmortems
- `structured/`: incident index, job dependencies, service logs, deployments (CSV)
- `evaluation/qa_ground_truth.jsonl`: 30 question/answer examples with expected source paths

## Quick start
1. Install `pip install langchain-community langchain-text-splitters langchain-chroma langchain-ollama` and install/run Ollama with an embedding model such as `nomic-embed-text`.
2. Run `ollama pull nomic-embed-text` (Ollama must be installed and running).
3. Run `python starter_ingest.py` from the dataset root to build a local Chroma index.
4. Implement a FastAPI `/ask` endpoint using `Chroma(persist_directory="./chroma_db", embedding_function=OllamaEmbeddings(model="nomic-embed-text"))` and `similarity_search(question, k=4)`.
5. Test the questions in `evaluation/qa_ground_truth.jsonl`; check both answer quality and source citations.

## Suggested questions
- What caused INC-001?
- Which runbook applies to DB_CONNECTION_POOL_EXHAUSTED?
- What happened before JOB-553 was blocked?
- Which deployment preceded the payment authorization timeout incident?

## Caveats
- Data is intentionally synthetic and highly structured; retrieval performance on it does not predict performance on real enterprise data.
- All ten incidents have known root causes. Add ambiguous/negative cases before claiming robust root-cause identification.
- Structured CSVs are for later SQL/graph exercises; starter ingestion indexes only Markdown files.
- Source metadata points to local relative files.
