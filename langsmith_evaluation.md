
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
