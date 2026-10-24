# IncidentGraph AI — Phase 1 Evaluation Report

**Evaluation scope:** Local, synthetic incident-investigation benchmark; 10 incidents, 30 questions (three per incident).
**Implementation:** LangChain, ChromaDB, Ollama (`llama3.2:1b` for generation and rewriting; `nomic-embed-text` for embeddings), FastAPI.
**Status:** Phase 1 backend evaluated; Streamlit frontend deferred.

## Executive summary

The retrieval pipeline achieved **Hit@3 = 100%, Recall@3 = 100%, and MRR@3 = 100%** on the 30-question synthetic benchmark in the previously completed retrieval evaluation. All 30 answer-generation requests completed without errors. In the latest provided answer evaluation (`answer_result(1).csv`), mean measured generation-pipeline latency was **1.57 seconds per question**. A prior manual review provisionally rated **27/30 answers (90%)** as broadly correct; this is **not** a formally adjudicated accuracy or faithfulness score.

Six FastAPI regression tests passed in **18.74 seconds**. These results support a functional local MVP, but not production-level reliability or generalization.

## Dataset and evaluation protocol

- **Corpus:** Incident reports, postmortems, and operational runbooks for ten synthetic incidents (INC-001 through INC-010).
- **Question set:** 30 synthetic questions, comprising one root-cause, one runbook-identification, and one job/error-code question per incident.
- **Ground truth:** Expected answers and expected source documents from the dataset's QA benchmark.
- **Retrieval:** Chroma semantic similarity search with up to 20 candidates, optional document-type metadata filtering, incident-ID text filtering, and a final maximum of three retrieved chunks.
- **Generation:** Evidence-grounded prompt with local Ollama `llama3.2:1b`, configured at `temperature=0`.
- **Answer evaluation:** Generated answers inspected against expected answers. The CSV columns `correctness` and `faithfulness` are unpopulated, so there is no independently validated faithfulness score.

## Results

| Metric | Observed result | Interpretation |
|---|---:|---|
| Retrieval Hit@3 | 100% | Every benchmark question retrieved at least one expected source in the recorded retrieval run. |
| Retrieval Recall@3 | 100% | All expected sources were covered within the top three in that run, under the evaluation script's matching logic. |
| Retrieval MRR@3 | 100% | The first expected source was ranked first for each question in that run, under the evaluation script's matching logic. |
| Answer requests completed | 30/30 | No generation errors recorded in the latest CSV. |
| Mean answer latency | 1.57 s | Arithmetic mean of `latency_seconds` in the latest 30-row CSV; environment-dependent. |
| Provisional answer correctness | 27/30 (90%) | Prior manual, answer-level review; not a blind or independently adjudicated score. |
| API regression tests | 6/6 passed | Completed in 18.74 s on the user's local Windows environment. |

**Important:** The retrieval percentages were reported from the separately executed retrieval evaluation; they were not recomputed from the answer CSV. High retrieval scores do not imply equivalent generation correctness.

## Qualitative error analysis

The latest answer evaluation includes these notable failures or weaknesses:

1. **INC-001 runbook misidentification:** The assistant answered `RB-PAY-002.md` for the `DB_CONNECTION_POOL_EXHAUSTED` question; the expected runbook is `RB-DB-001`.
2. **INC-006 root-cause omission:** The assistant stated that the cause could not be determined, rather than identifying the missing/unpublished model artifact path described by the benchmark.
3. **INC-008 primary-job confusion:** The assistant answered `JOB-552`, the failed upstream prerequisite, when the expected incident primary job is `JOB-553`. The error code `UPSTREAM_DEPENDENCY_FAILED` was identified correctly.
4. **Answer clarity and attribution:** Some responses are verbose or hedge unnecessarily. The API's `source` field lists retrieved documents, not claim-level verified citations; a retrieved source may not directly support the generated claim.

These are illustrative known issues, not a complete independent faithfulness audit. Some answers that contain the expected identifier may still include misleading wording.

## API regression tests

`evaluation/test_api.py` exercised the real FastAPI application through `TestClient`:

| Test | Result |
|---|---|
| `GET /health` returns healthy status | Passed |
| Empty question rejected with HTTP 422 | Passed |
| `/ask` response contains required fields | Passed |
| Incident-specific query returns incident-related sources | Passed |
| Follow-up question preserves incident context | Passed |
| Unknown incident returns insufficient-evidence response | Passed |

**Observed execution:** `6 passed in 18.74s` using Python 3.13.3 and pytest 9.1.1 on Windows. These are smoke/regression tests, not load, security, or exhaustive correctness tests.

## Limitations and threats to validity

- **Small, synthetic benchmark:** Ten incidents and 30 questions cannot establish real-world generalization.
- **Evaluation-set tuning:** Retrieval and prompt decisions were refined while inspecting benchmark examples; scores may be optimistic. A held-out test set is needed.
- **Chunk-level incident matching:** Filtering by incident ID in chunk text can discard relevant chunks that omit the identifier.
- **Weak entity-role disambiguation:** The 1B model sometimes confuses primary jobs with causal upstream jobs.
- **Source attribution:** Retrieved document paths are not evidence-span citations or guarantees of factual support.
- **Session storage:** Conversation history is in process memory, with no persistence, authentication, or multi-worker coordination.
- **Reproducibility:** `temperature=0` reduces randomness but does not guarantee identical local LLM outputs across environments or runs.
- **Latency:** The observed average is from a single local evaluation run; no percentile latency, throughput, or load measurements were collected.

## Planned experiments beyond Phase 1

**Phase 2 — Graph-enhanced retrieval:** Extract incident, job, service, deployment, and error-code entities; encode relationships such as `PRIMARY_JOB`, `DEPENDS_ON`, and `CAUSED_BY`; compare vector-only, structured-field, and graph-plus-vector retrieval on a new held-out, multi-hop benchmark. Report answer correctness, relation accuracy, evidence support, and latency.

**Phase 3 — Read-only agentic investigation:** Add bounded investigation tools and traceable multi-step workflows; evaluate tool-use correctness, evidence coverage, latency, and failure handling. Production actions would require explicit operator approval.

## Reproducing the checks

From the repository root, with the Chroma store populated and Ollama running with the required models:

```powershell
python evaluation/evaluate_retrieval.py
python evaluation/evaluate_answers.py
python -m pytest evaluation/test_api.py -v
```

The answer-evaluation script writes `evaluation/answer_result.csv`. Review its answers against ground truth rather than interpreting successful execution as correctness. Record hardware, Ollama/model versions, dataset revision, and evaluation script revision when publishing new benchmark runs.

---

*This report records observed MVP measurements and clearly separates provisional manual judgments from independently validated metrics.*
