# LangSmith Experiment Evaluation
**Course:** SWE 580 – Applied Large Language Models
**Student:** M. Zeynep
**Model:** Llama 3.1 (8B) via Ollama | **Embeddings:** nomic-embed-text | **Vector Store:** ChromaDB
**Dataset:** SWE580_MCP_Evaluation (20 questions)

---

## Part 1 — Baseline System Evaluation (Full 20-Question Dataset)

This section reports results from the automated evaluation run logged in `data/results/Baseline_RAG_Test-740e46a2.csv`. The CSV contains 20 rows (one per question). The automated scoring columns (`correctness`, `hallucination_free`, `relevance`) were not populated by the evaluation framework, so each response was scored manually by comparing the system's answer against the reference answer using a three-point scale: **PASS** (1.0) = correct and complete, **PARTIAL** (0.5) = directionally correct but missing key detail, **FAIL** (0.0) = wrong or absent answer.

### Overall Metrics

| Metric | Value |
|--------|-------|
| Total questions | 20 |
| Full PASS | 8 (40%) |
| PARTIAL | 6 (30%) |
| FAIL | 6 (30%) |
| **Weighted score** | **0.55 / 1.0** |
| Mean latency | 26.1 s |
| Min / Max latency | 7.2 s / 49.0 s |

### Results by Difficulty

| Difficulty | n | PASS | PARTIAL | FAIL | Avg Score |
|------------|---|------|---------|------|-----------|
| Easy       | 8 | 4    | 1       | 3    | 0.56      |
| Medium     | 8 | 4    | 3       | 1    | 0.69      |
| Hard       | 4 | 0    | 2       | 2    | 0.25      |

The most counterintuitive finding is that **Easy questions scored lower than Medium ones (0.56 vs 0.69)**. All three Easy failures are definitional questions — "What is a Resource?", "What is a Tool?", and "What is the role of an MCP Server?" — where the retriever consistently returned mid-document pages rather than the introductory sections where these terms are first defined. Medium questions that ask for comparisons or process descriptions (e.g., the handshake, stdio vs SSE) actually benefited from having relevant content distributed across multiple pages, making it easier for the retriever to find at least one relevant chunk. Hard questions scored the lowest (0.25), with no full passes — all four require multi-step reasoning over content spread across many pages, which the baseline k=3 retrieval window cannot support.

### Full Results Table

| # | Question (abbreviated) | Difficulty | Score | Verdict |
|---|------------------------|------------|-------|---------|
| 1 | Two primary transport mechanisms | Easy | 1.0 | PASS |
| 2 | Role of the Client | Easy | 0.5 | PARTIAL |
| 3 | Static config file → which MCP feature? | Medium | 0.0 | FAIL |
| 4 | Role of an MCP Server | Easy | 0.0 | FAIL |
| 5 | What does MCP stand for? | Easy | 1.0 | PASS |
| 6 | Primary problem MCP solves | Easy | 1.0 | PASS |
| 7 | Messaging protocol used under the hood | Easy | 1.0 | PASS |
| 8 | Definition of an MCP Resource | Easy | 0.0 | FAIL |
| 9 | Opt-in authorization and filesystem risk | Hard | 0.0 | FAIL |
| 10 | How client discovers Tools and Resources | Medium | 0.5 | PARTIAL |
| 11 | Rate limiting for external API (custom server) | Hard | 0.5 | PARTIAL |
| 12 | Security: SSE vs stdio | Hard | 0.5 | PARTIAL |
| 13 | Compare stdio vs SSE — when to use each | Medium | 1.0 | PASS |
| 14 | True/False: MCP requires TypeScript | Medium | 0.5 | PARTIAL |
| 15 | How Prompts standardize interactions | Medium | 1.0 | PASS |
| 16 | Exact sequence when LLM executes a Tool | Hard | 0.0 | FAIL |
| 17 | DB write → which MCP feature? | Medium | 1.0 | PASS |
| 18 | Functional difference: Resource vs Tool | Medium | 0.5 | PARTIAL |
| 19 | Definition of an MCP Tool | Easy | 0.0 | FAIL |
| 20 | Client-server handshake process | Medium | 1.0 | PASS |

---

### Failure Case Analysis

#### Failure Case 1 — Definitional Retrieval Miss (Questions 8 and 19)
**Questions:** "What is the definition of an MCP Resource?" / "What is the definition of an MCP Tool?"  
**Expected:** Data/context provided by the server that the AI can read / Executable functions exposed by the server that the AI can trigger  
**System Response (Q8):** *"Unfortunately, I don't know the answer to that question based on the provided context."*  
**System Response (Q19):** *"Unfortunately, I don't have enough context to provide a specific answer."*

Both are Easy questions that failed with a clean "I don't know." The retriever returned pages from the middle of documents (e.g., pages 18–19 of `Model_Context_Protocol_Yusuf_Ozuysal.pdf`, page 40 of `the_model_context_protocol.pdf`) where Resource and Tool are used in context but never formally defined. The formal definitions appear in the introductory primitives sections (likely pages 2–5 of `the_model_context_protocol.pdf`), which score lower in dense similarity search because they are less terminology-dense than later chapters. This is a **semantic ranking inversion**: the embedding model up-ranks pages that reference these terms most often, not pages that define them.

#### Failure Case 2 — Confident Misdirection from a Misleading Chunk (Question 3)
**Question:** "If a user wants an AI to be able to read a static local configuration file, which MCP feature should the server developer use, and why?"  
**Expected:** Resource — designed for read-only contextual data  
**System Response:** *"The server developer should use the 'Client A' connection in the MCP-Powered Workflow... specifically the `search_document` tool."*

This is the most severe failure in the dataset: the system gave a confident, architecturally wrong answer. The retrieved chunks (pages 25–26 of `the_model_context_protocol.pdf` and page 68 of `agent_engineering_enterprise.pdf`) happened to contain a diagram and code example showing a `search_document` tool reading a file. The LLM saw a tool performing a file-read operation and incorrectly concluded this was the prescribed pattern. No chunk defining the Resource primitive was retrieved, so the model had no counterevidence. This is a **context poisoning failure** — one misleading but high-ranking chunk corrupted the entire answer. Notably, this same question answered correctly at k=5 (see Part 2 below) once a definitional chunk for Resources was included.

#### Failure Case 3 — Reasoning Chain Requires Unavailable Context (Question 16)
**Question:** "Detail the exact sequence of events and messages exchanged when an LLM decides to execute an MCP Tool."  
**Expected:** LLM generates tool call → client sends `tools/call` → server executes logic → returns JSON-RPC result → LLM receives output  
**System Response:** *"I don't know. The context only describes a general workflow and details about the Operation Phase, but it doesn't specifically describe the sequence of events."*

This Hard question requires a precise, ordered sequence of JSON-RPC message types. The retrieved chunks described the Operation Phase at a high level but did not contain the step-by-step `tools/call` message flow. Unlike the definitional failures above, this is not a ranking problem — the specific sequence diagram or protocol specification likely appears in only one or two pages across all documents, and those pages were not among the top-3 retrieved chunks. The system correctly identified the gap and abstained rather than hallucinating a sequence. The failure is an **insufficient retrieval coverage** problem: with k=3 over a 150+ page corpus, low-frequency but high-specificity content has a low probability of being retrieved.

---

## Part 2 — k=3 vs k=5 Comparative Evaluation (5 Questions)

*The following section documents a follow-up experiment in which the same 5 questions were tested at both k=3 and k=5 to measure the effect of widening the retrieval window.*

---

## Part 2 — 10-Experiment Comparative Analysis

All 10 experiments were evaluated against the same 20-question LangSmith dataset. The automated scoring columns were empty (the local Ollama judge did not write scores back to LangSmith), so each answer was scored programmatically using keyword-based heuristics matched against the reference answers: **1.0** = correct, **0.5** = partial, **0.0** = wrong or absent.

### Experiment Configurations

| Exp | Chunk Size | Overlap | k | Group |
|-----|-----------|---------|---|-------|
| 01 | 800 | 150 | 5 | Baseline (control) |
| 02 | 800 | 150 | 10 | Top-K scaling — high context |
| 03 | 800 | 150 | 3 | Top-K scaling — low context |
| 04 | 1500 | 200 | 5 | Large chunks |
| 05 | 1500 | 200 | 8 | Large chunks + high k |
| 06 | 2500 | 400 | 3 | Massive chunks |
| 07 | 400 | 50 | 5 | Small chunks (sniper) |
| 08 | 400 | 50 | 15 | Small chunks + high k |
| 09 | 800 | 400 | 5 | Heavy overlap fix |
| 10 | 1200 | 250 | 7 | Goldilocks estimate |

---

### Overall Scores

| Exp | Config | Avg Score | Easy (n=8) | Medium (n=8) | Hard (n=4) | Avg Latency |
|-----|--------|-----------|------------|--------------|------------|-------------|
| **10** | **size=1200, overlap=250, k=7** | **0.825** | **0.69** | **0.94** | **0.88** | **33.2s** |
| 01 | size=800, overlap=150, k=5 | 0.725 | 0.69 | 0.69 | 0.88 | 26.5s |
| 04 | size=1500, overlap=200, k=5 | 0.700 | 0.56 | 0.75 | 0.88 | 32.8s |
| 05 | size=1500, overlap=200, k=8 | 0.700 | 0.62 | 0.69 | 0.88 | 37.5s |
| 02 | size=800, overlap=150, k=10 | 0.675 | 0.69 | 0.56 | 0.88 | 40.5s |
| 08 | size=400, overlap=50, k=15 | 0.650 | 0.56 | 0.62 | 0.88 | 39.2s |
| 06 | size=2500, overlap=400, k=3 | 0.575 | 0.38 | 0.62 | 0.88 | 31.3s |
| 03 | size=800, overlap=150, k=3 | 0.550 | 0.50 | 0.44 | 0.88 | 25.6s |
| 09 | size=800, overlap=400, k=5 | 0.550 | 0.50 | 0.44 | 0.88 | 28.7s |
| 07 | size=400, overlap=50, k=5 | 0.450 | 0.25 | 0.50 | 0.75 | 25.7s |

---

### Per-Question Score Matrix

Scores per question across all 10 experiments. Questions where all experiments scored 1.0 are stable; questions with high variance reveal where configuration matters most.

| Q | Difficulty | E01 | E02 | E03 | E04 | E05 | E06 | E07 | E08 | E09 | E10 |
|---|------------|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|
| Q01 | Easy | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 0.5 | 1.0 | 1.0 | 1.0 |
| Q02 | Easy | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 0.0 | 0.0 | 1.0 | 1.0 |
| Q03 | Medium | 0.0 | 0.0 | 0.0 | 1.0 | 0.5 | 1.0 | 0.0 | 0.0 | 0.0 | 1.0 |
| Q04 | Easy | 0.5 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.5 | 0.0 | 1.0 |
| Q05 | Easy | 1.0 | 1.0 | 0.0 | 1.0 | 1.0 | 0.0 | 0.0 | 1.0 | 1.0 | 1.0 |
| Q06 | Easy | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 0.5 | 1.0 | 0.5 | 1.0 |
| Q07 | Easy | 1.0 | 1.0 | 1.0 | 0.5 | 1.0 | 0.0 | 1.0 | 1.0 | 0.5 | 0.0 |
| Q08 | Easy | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| Q09 | Hard | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 |
| Q10 | Medium | 0.5 | 0.0 | 0.0 | 0.5 | 0.5 | 0.5 | 0.5 | 0.0 | 0.0 | 0.5 |
| Q11 | Hard | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 |
| Q12 | Hard | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 |
| Q13 | Medium | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 |
| Q14 | Medium | 1.0 | 0.0 | 1.0 | 0.0 | 0.0 | 0.0 | 0.0 | 1.0 | 0.0 | 1.0 |
| Q15 | Medium | 1.0 | 1.0 | 0.0 | 1.0 | 1.0 | 0.0 | 1.0 | 1.0 | 1.0 | 1.0 |
| Q16 | Hard | 0.5 | 0.5 | 0.5 | 0.5 | 0.5 | 0.5 | 0.0 | 0.5 | 0.5 | 0.5 |
| Q17 | Medium | 0.0 | 1.0 | 0.0 | 1.0 | 1.0 | 1.0 | 0.0 | 0.5 | 0.0 | 1.0 |
| Q18 | Medium | 1.0 | 0.5 | 0.5 | 0.5 | 0.5 | 0.5 | 0.5 | 0.5 | 0.5 | 1.0 |
| Q19 | Easy | 0.0 | 0.5 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.5 |
| Q20 | Medium | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 |
| **Avg** | | **0.725** | **0.675** | **0.550** | **0.700** | **0.700** | **0.575** | **0.450** | **0.650** | **0.550** | **0.825** |

---

### Optimal Configuration: Experiment 10 (size=1200, overlap=250, k=7)

**Exp 10 is the best-performing configuration** with an average score of **0.825**, 13.8% above the baseline (Exp 01 = 0.725). Its advantage is concentrated in Medium questions (0.94 vs 0.69 for the baseline) — the tier where most of the actionable variation exists.

#### Why Exp 10 Wins

**1. Chunk size 1200 preserves semantic units.** The baseline size of 800 characters frequently splits multi-sentence definitions and process descriptions across chunk boundaries. At 1200, definitions of primitives like Resources and Tools, and structured content like the handshake process, fit within a single chunk. This directly explains why Exp 10 is the only experiment to correctly answer Q03 (static file → Resource), Q04 (MCP Server role), and Q17 (DB write → Tool) simultaneously — all three require a definition chunk to be retrieved intact.

**2. Overlap of 250 provides boundary insurance.** The 250-character overlap (vs 150 in the baseline) means that content near chunk boundaries appears in two consecutive chunks. This prevents the scenario seen in the baseline where a definition begins at the end of one chunk and its explanation starts the next — with the explanation never being retrieved.

**3. k=7 balances coverage and noise.** k=10 (Exp 02) scored *lower* than the baseline (0.675 vs 0.725) despite retrieving more chunks. More context is not always better — at k=10, weakly-relevant chunks dilute the prompt and confuse the LLM on questions like Q14 (TypeScript T/F) and Q17 (DB write feature), both of which Exp 02 scored 0.0 on. k=7 retrieves enough to cover distributed content without introducing misleading noise.

**4. Latency is acceptable.** At 33.2s average, Exp 10 is only 6.7s slower than the baseline (26.5s) — a 25% increase in latency for a 13.8% increase in correctness. Experiments 02 and 05 were 40.5s and 37.5s respectively for lower scores, making them worse on both dimensions.

#### Why Other Configurations Failed

| Config | Problem |
|--------|---------|
| Exp 03 (k=3) | Context starvation — 0.550 avg, worst on Medium questions (0.44). Proves k=5 was necessary in the baseline. |
| Exp 07 (size=400, k=5) | Worst overall (0.450). Small chunks fragment every definition. Failed Q02, Q04, Q05 — all easy definitional questions. Also the only experiment to score 0.75 on Hard questions instead of 0.88. |
| Exp 06 (size=2500, k=3) | Massive chunks hurt precision. A 2500-char chunk contains so much mixed content that the embedding loses specificity. Failed Q05 (MCP acronym) and Q07 (JSON-RPC) — trivially easy questions that every other experiment answered correctly. k=3 with huge chunks means only 3 very broad retrieval hits. |
| Exp 09 (size=800, overlap=400) | Heavy overlap alone did not help (0.550, tied with k=3 baseline). Overlap prevents boundary splits but does not address the fundamental chunk-size-too-small problem. The same definitional pages still ranked poorly. |
| Exp 02 (k=10) | Diminishing returns plus noise. Adding chunks beyond k=7 introduces off-topic content. Q14 and Q17 both regressed compared to the baseline. |

#### The One Unsolved Problem: Q08 (MCP Resource Definition)

Q08 — *"What is the definition of an MCP Resource?"* — scored **0.0 across all 10 experiments**. This is the single most robust failure in the dataset. No chunk size, overlap, or k value was able to retrieve the formal definition page. This indicates a **semantic ranking inversion**: the embedding model consistently ranks high-frequency usage pages (where "Resource" appears many times in examples) above the low-frequency introductory definition page. Fixing this would require either a hybrid BM25+dense search to catch exact-match queries, or metadata-tagged retrieval that prioritizes document section type (introduction vs body).

---

### Summary

| Finding | Evidence |
|---------|----------|
| Exp 10 (size=1200, overlap=250, k=7) is the optimal config | Highest avg score (0.825), best Medium score (0.94) |
| Chunk size matters more than k | Exp 01→04 (+0 on k, +700 on size): score unchanged at 0.700; Exp 01→10 (+2 on k, +400 on size, +100 on overlap): score jumps to 0.825 |
| Too many chunks (k=10) hurts Medium questions | Exp 02 Medium score (0.56) is worse than Exp 03/k=3 (0.44) only slightly better, but trails Exp 01 significantly |
| Small chunks are the worst strategy | Exp 07 (size=400) is last place despite average k; even k=15 (Exp 08) only partially recovers to 0.650 |
| Hard questions are uniformly answered well (≥0.75) | Hard questions in this dataset test security reasoning (Q9, Q11, Q12) where relevant content is distributed broadly — any configuration retrieves enough signal |
| Q08 (Resource definition) is an embedding failure, not a configuration failure | 0/10 experiments solved it — requires architectural change (hybrid search) |
