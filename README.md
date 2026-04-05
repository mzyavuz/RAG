# SWE 580 – RAG System over Model Context Protocol (MCP) Documents

**Course:** SWE 580 – Applied Large Language Models  
**Student:** M. Zeynep  

A fully local Retrieval-Augmented Generation (RAG) pipeline built with LangChain, ChromaDB, and Ollama, evaluated over 10 experimental configurations via LangSmith.

---

## Repository Structure

```
.
├── docs/                        # PDF knowledge base (5 MCP papers)
├── src/
│   ├── document_processor.py    # Step 1: Load PDFs, chunk, embed → ChromaDB
│   ├── database.py              # ChromaDB save/load helpers
│   ├── main_rag.py              # Step 2: LCEL RAG chain (query interface)
│   ├── evaluate.py              # LangSmith baseline evaluation pipeline
│   ├── run_experiments.py       # 10-experiment automated evaluation loop
│   ├── upload_dataset.py        # Upload Q&A dataset to LangSmith
│   └── langsmith_evaluators.py  # Custom evaluators for LangSmith UI
├── data/
│   └── results/                 # Raw CSV exports from LangSmith experiments
├── questions/
│   ├── 20_questions.txt         # Full evaluation dataset (Easy/Medium/Hard)
│   └── 5_questions.txt          # Subset used for manual evaluation
├── screenshots/                 # LangSmith dashboard screenshots
├── manual_evaluation.md         # Manual evaluation: 5 Qs at k=3 and k=5
├── langsmith_evaluation.md      # Automated evaluation: 10 experiments, 20 Qs
├── comparison.md                # Manual vs. automated evaluation comparison
└── README.md
```

---

## Dependencies

### System Requirements

- **Python 3.11+** (tested on 3.14)
- **Ollama** running locally with two models pulled:

```bash
ollama pull nomic-embed-text
ollama pull llama3.1:8b
```

### Python Packages

Create and activate a virtual environment, then install dependencies:

```bash
python3 -m venv src/venv
source src/venv/bin/activate
pip install langchain langchain-chroma langchain-ollama langchain-core \
            langchain-community langchain-text-splitters \
            langsmith chromadb pypdf
```

### LangSmith (for evaluation)

Create a free account at [smith.langchain.com](https://smith.langchain.com) and set environment variables:

```bash
export LANGCHAIN_API_KEY="ls-..."
export LANGCHAIN_TRACING_V2="true"
export LANGCHAIN_PROJECT="SWE580-RAG"
```

---

## Reproducing the Pipeline End-to-End

All commands are run from the project root with the virtual environment active.

### Step 1 — Build the Vector Database

Loads all PDFs from `docs/`, chunks them (chunk_size=800, overlap=150), embeds with `nomic-embed-text`, and persists to `data/chroma/`:

```bash
python3 src/document_processor.py
```

### Step 2 — Query the RAG System Interactively

Loads the vector store, builds a LangChain LCEL chain with `llama3.1:8b`, and opens a query loop:

```bash
python3 src/main_rag.py
```

Type any question, `test` to run the built-in test query, or `exit` to quit.

### Step 3 — Upload Evaluation Dataset to LangSmith

Uploads the 20-question Q&A dataset to LangSmith (only needed once):

```bash
python3 src/upload_dataset.py
```

### Step 4 — Run the Baseline Evaluation

Evaluates the default RAG chain (k=5, chunk_size=800) against the 20-question dataset using LLM-judge evaluators:

```bash
python3 src/evaluate.py
```

### Step 5 — Run All 10 Experiments

Tests 10 configurations varying chunk size, overlap, and k. Each experiment gets an isolated ChromaDB directory to avoid file-lock conflicts:

```bash
python3 src/run_experiments.py
```

This takes ~2–4 hours depending on hardware. Results are logged to LangSmith and exported as CSVs in `data/results/`.

---

## Experiment Configurations

| Exp | Chunk Size | Overlap | k  | Group |
|-----|-----------|---------|-----|-------|
| 01  | 800       | 150     | 5  | Baseline |
| 02  | 800       | 150     | 10 | High context |
| 03  | 800       | 150     | 3  | Low context |
| 04  | 1500      | 200     | 5  | Large chunks |
| 05  | 1500      | 200     | 8  | Large chunks + high k |
| 06  | 2500      | 400     | 3  | Massive chunks |
| 07  | 400       | 50      | 5  | Small chunks |
| 08  | 400       | 50      | 15 | Small chunks + high k |
| 09  | 800       | 400     | 5  | Heavy overlap |
| 10  | 1200      | 250     | 7  | **Optimal ("Goldilocks")** |

**Best configuration: Exp 10** (size=1200, overlap=250, k=7) — average score 0.825 across 20 questions.

---

## Custom LangSmith Evaluators

Three custom evaluators are defined in `src/langsmith_evaluators.py`:

| Evaluator | What it measures |
|-----------|-----------------|
| **Correctness** | Keyword overlap between answer and reference (≥60% → 1.0, ≥30% → 0.5) |
| **Relevance** | Whether the answer addresses the question (question-term coverage) |
| **Hallucination_Free** | Whether all facts in the answer are grounded in retrieved context |

To use these in the LangSmith UI: create a Python evaluator for each and paste the `perform_eval` function body from `langsmith_evaluators.py`.

---

## Key Findings

- **Retrieval failures, not generation failures** — all incorrect answers traced to the wrong chunks being retrieved, not the LLM fabricating content.
- **Q08 (MCP Resource definition) failed all 10 experiments** — embedding ranking inversion; the term "resource" is overloaded across documents and semantic search consistently retrieves the wrong passage.
- **k=10 (Exp 02) added 14s latency while scoring *lower* than k=5** — more context is not always better.
- **Manual vs automated evaluation**: 6/10 scores agreed on 5 overlapping questions. Automated scoring is more lenient (0.40 vs 0.10 at k=3) because keyword presence doesn't capture grounding violations or completeness.

See [`langsmith_evaluation.md`](langsmith_evaluation.md) and [`comparison.md`](comparison.md) for full analysis.

---

## LangSmith Screenshots

Screenshots from the LangSmith dashboard are in the `screenshots/` directory:

| File | Contents |
|------|----------|
| `Screenshot 2026-03-31 at 23.33.08.png` | Dataset view — 20 Q&A examples |
| `Screenshot 2026-04-04 at 23.51.47.png` | Experiment traces overview |
| `Screenshot 2026-04-04 at 23.51.54.png` | Per-question score breakdown |
| `Screenshot 2026-04-04 at 23.52.02.png` | Evaluator output detail |
| `Screenshot 2026-04-05 at 22.25.54.png` | 10-experiment comparison table |
| `Screenshot 2026-04-05 at 22.26.09.png` | Score distribution across configurations |
| `Screenshot 2026-04-05 at 22.26.27.png` | Custom evaluator results |
| `Screenshot 2026-04-05 at 22.48.08.png` | Optimal experiment (Exp 10) trace |

---

## Architecture

```
docs/*.pdf
    │
    ▼  PyPDFDirectoryLoader + RecursiveCharacterTextSplitter
chunks (Document objects)
    │
    ▼  OllamaEmbeddings (nomic-embed-text)
data/chroma/  ──── ChromaDB vector store
    │
    ▼  as_retriever(k=N)
top-N chunks
    │
    ▼  PromptTemplate + OllamaLLM (llama3.1:8b)
answer + source metadata
```

All inference runs locally — no OpenAI API calls, no cloud GPU.
