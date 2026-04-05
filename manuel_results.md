# RAG System Manuel Evaluation Report
**Course:** SWE 580 – Applied Large Language Models  
**Assignment:** RAG Pipeline Evaluation  
**Student:** M. Zeynep  
**Model:** Llama 3.1 (8B) via Ollama | **Embeddings:** nomic-embed-text | **Vector Store:** ChromaDB  
**Chunk Size:** 800 | **Chunk Overlap:** 150

---

## Evaluation Dataset — 20 Question-Answer Pairs

The following Q&A pairs were derived from the five course PDF materials on the Model Context Protocol (MCP).

### Easy (8 Questions)

| # | Question | Expected Answer |
|---|----------|-----------------|
| E1 | What does MCP stand for? | Model Context Protocol |
| E2 | What is the primary purpose of MCP? | To standardize how AI models (LLMs) connect to and interact with external tools, data sources, and services |
| E3 | What are the three primitive types exposed by an MCP server? | Resources, Tools, and Prompts |
| E4 | What transport protocols does MCP support? | stdio (standard input/output) and HTTP with Server-Sent Events (SSE) |
| E5 | Which company developed the Model Context Protocol? | Anthropic |
| E6 | What role does the MCP Host play? | The Host is the application (e.g., Claude Desktop) that manages MCP client connections and mediates access to servers |
| E7 | What is a Resource in MCP? | A Resource exposes static or dynamic data (files, database records, etc.) that provides context to the LLM without side effects |
| E8 | What is a Tool in MCP? | A Tool is a callable function that allows the LLM to perform actions with side effects, such as querying an API or writing to a database |

---

### Medium (8 Questions)

| # | Question | Expected Answer |
|---|----------|-----------------|
| M1 | In the MCP architecture, what is the role of an MCP Server? | The MCP Server exposes capabilities (Tools, Resources, Prompts) to clients. It handles client requests, processes them, and sends back responses. It is one of the three core architectural components alongside the Host and the Client |
| M2 | Describe the client-server handshake process when an MCP connection is first initialized. | The client sends an `initialize` request; the server responds with available tools, resources, and prompts; the connection is established; continuous notifications maintain synchronization between client and server |
| M3 | What is the difference between a Tool and a Resource in MCP, and when should each be used? | Resources expose read-only contextual data (no side effects); Tools execute actions with potential side effects. A static config file should be a Resource; an API call should be a Tool |
| M4 | What security threat does "tool poisoning" refer to in MCP? | An attack where a malicious MCP server provides a tool with a misleading description that tricks the LLM into performing unintended or harmful actions |
| M5 | What is "prompt injection" in the context of MCP, and how can it occur? | Malicious content embedded in data retrieved by the LLM (e.g., from a Resource or tool output) contains hidden instructions that manipulate the model's behavior |
| M6 | What is the "confused deputy" problem in MCP security? | A trusted MCP client is manipulated into making requests to a server on behalf of an attacker, leveraging the client's existing permissions to perform unauthorized actions |
| M7 | How does MCP differ from a traditional REST API integration? | MCP provides a standardized, model-aware protocol with built-in capability negotiation, structured tool/resource primitives, and a defined lifecycle, whereas REST APIs require custom integration code per service |
| M8 | What is the purpose of the `sampling` capability in MCP? | Sampling allows MCP servers to request the host to perform LLM completions on their behalf, enabling agentic loops without direct API access |

---

### Hard (4 Questions)

| # | Question | Expected Answer |
|---|----------|-----------------|
| H1 | In an enterprise agentic system, what are the key architectural considerations when deploying multiple MCP servers, and what failure modes must be accounted for? | Key considerations: server isolation and trust boundaries, capability scoping per agent role, graceful partial failure handling, preventing cross-server prompt injection, audit logging for tool invocations. Failure modes: server unavailability, capability drift, cascading tool errors |
| H2 | How do the security threat models for MCP differ between local (stdio) and remote (SSE/HTTP) deployments? | Local stdio: threats from malicious installed servers (supply chain) and local privilege escalation. Remote HTTP/SSE: adds MITM attacks, auth failures, DNS rebinding, server impersonation. Remote deployments require TLS, token-based auth, and origin validation |
| H3 | What mitigations can be implemented at the Host layer to defend against a compromised MCP server attempting tool poisoning or data exfiltration? | Human-in-the-loop tool confirmation, sandboxing tool execution, validating tool outputs before passing to LLM, restricting network access for tool processes, allowlisting approved MCP servers |
| H4 | How would you design a RAG pipeline over MCP documents to maximize retrieval accuracy for questions about security threat taxonomies, given the limitations of fixed-size chunking? | Semantic/paragraph-level chunking, metadata tags for threat categories, larger k with MMR to reduce redundancy, a re-ranker model on retrieved chunks, hybrid search (dense + sparse/BM25) |

---

## Manual Test Results

The same five questions were submitted to the RAG system under two configurations: **k=3** (baseline) and **k=5** (extended retrieval). All other parameters were held constant (chunk_size=800, chunk_overlap=150). Responses were recorded verbatim.

---

### Test 1 — E1: "What does the acronym 'MCP' stand for in the context of AI engineering?"
**Difficulty:** Easy  
**Expected:** Model Context Protocol

#### k=3
**System Response:**
> "Unfortunately, I don't know what 'MCP' stands for based on the provided context. The text mentions 'The use of MCP isn't just a concept; it's already a reality...' but doesn't explicitly define what MCP is."

**Retrieved Sources:** `Model_Context_Protocol_Yusuf_Ozuysal.pdf` (Pages 18, 19), `the_model_context_protocol.pdf` (Page 40)

**Result:** FAIL

#### k=5
**System Response:**
> "Based on the provided context, I don't see an explicit explanation of what 'MCP' stands for. However, from the usage and description, it appears to be related to a protocol or interface for accessing tools and resources in an AI-powered coding environment."

**Retrieved Sources:** `Model_Context_Protocol_Yusuf_Ozuysal.pdf` (Pages 18, 19), `the_model_context_protocol.pdf` (Pages 40, 44), `MCP_landscape_security_threats.pdf` (Page 2)

**Result:** FAIL

**Analysis:** Neither configuration retrieved the introductory pages where the acronym is defined. The retriever consistently returned mid-document pages (pages 18–19 of `Yusuf_Ozuysal.pdf` and page 40 of `the_model_context_protocol.pdf`) that use the acronym without defining it. Increasing k from 3 to 5 added pages 44 and 2, which still did not contain the definition. Notably, the k=5 response was *less disciplined* — instead of saying "I don't know," the model speculated about what MCP "appears to be," which is a mild grounding violation. The k=3 response was technically more correct in its abstention.

---

### Test 2 — M1: "In the MCP architecture, what is the role of an 'MCP Server'?"
**Difficulty:** Medium  
**Expected:** The MCP Server exposes capabilities (Tools, Resources, Prompts) to clients and handles request processing

#### k=3
**System Response:**
> "Based on the provided context, I do not see any information about the role of an 'MCP Server' in the MCP architecture. The only information provided is about the MCP Client and its role as a communicator. [...] I do not know."

**Retrieved Sources:** `Model_Context_Protocol_Yusuf_Ozuysal.pdf` (Pages 18, 19), `the_model_context_protocol.pdf` (Page 4)

**Result:** FAIL

#### k=5
**System Response:**
> "Based on the context provided, the MCP architecture has three main components: the MCP Client, the Host, and the Server. An MCP Server's role in the Model Context Protocol architecture is to process requests from the MCP Client and send responses back. It is explicitly stated that an MCP Server is a critical component in building functional and secure integrations."

**Retrieved Sources:** `Model_Context_Protocol_Yusuf_Ozuysal.pdf` (Pages 18, 19), `the_model_context_protocol.pdf` (Pages 4, 11, 18)

**Result:** PARTIAL PASS

**Analysis:** Adding two more chunks from `the_model_context_protocol.pdf` (pages 11 and 18) gave the model enough context to name all three architectural components and describe the server's role at a high level. The k=3 response was a complete failure; k=5 produced a meaningful partial answer. This is a clear demonstration that the definition was spread across pages 4, 11, and 18 — all three were needed, and only k=5 retrieved enough of them.

---

### Test 3 — M2: "Describe the client-server handshake process. What happens when an MCP connection is first initialized?"
**Difficulty:** Medium  
**Expected:** Client sends `initialize` request → server responds with capabilities → `initialized` notification → ongoing sync

#### k=3
**System Response:**
> "The communication between the MCP client and server follows a structured process. When an MCP connection is first initialized, the client sends an initial request to query the server's functionalities. The server responds with an initial response listing the available tools, resources, and prompts that the client can leverage. After this exchange, the system maintains a continuous exchange of notifications between the client and server."

**Retrieved Sources:** `agent_engineering_enterprise.pdf` (Pages 83, 72), `MCP_landscape_security_threats.pdf` (Page 6)

**Result:** PARTIAL PASS

#### k=5
**System Response:**
> "The client-server handshake process in MCP begins with an initial request from the client to query the server's functionalities. Upon receiving this request, the server responds with an initial response listing available tools, resources, and prompts. Once the connection is established, the system maintains a continuous exchange of notifications. In other words: (1) The client sends an initial request. (2) The server responds with available tools, resources, and prompts. (3) A connection is established. (4) A continuous exchange of notifications begins."

**Retrieved Sources:** `agent_engineering_enterprise.pdf` (Pages 83, 72, 64), `MCP_landscape_security_threats.pdf` (Pages 6, 2)

**Result:** PASS

**Analysis:** Both configurations retrieved relevant pages and produced usable answers. The k=5 response is structurally superior — it enumerates the four steps explicitly, making the answer clearer and more complete. The additional pages (64 from `agent_engineering_enterprise.pdf` and page 2 from `MCP_landscape_security_threats.pdf`) reinforced the existing context. This is the only question where both k=3 and k=5 succeeded, suggesting the handshake information is well-distributed across the corpus.

---

### Test 4 — M3: "If a user wants an AI to be able to read a static local configuration file, which MCP feature (Resource, Tool, or Prompt) should the server developer use, and why?"
**Difficulty:** Medium  
**Expected:** Resource — it is designed for read-only contextual data with no side effects

#### k=3
**System Response:**
> "Based on the context, if a user wants an AI to be able to read a static local configuration file, I would recommend using the 'Tool' feature. The context shows that Client A connects to a local filesystem MCP Server, which allows the Host to read the content of a highlighted function from the local file. This is an example of a tool (in this case, the `search_document` tool) being used to retrieve file content."

**Retrieved Sources:** `the_model_context_protocol.pdf` (Pages 25, 26), `agent_engineering_enterprise.pdf` (Page 68)

**Result:** FAIL (Confidently Incorrect)

#### k=5
**System Response:**
> "Based on the context, if a user wants an AI to be able to read a static local configuration file, I would recommend using the 'Resource' feature. According to the text, the Resources tab lists available resources with MIME types and metadata, and supports content inspection. This suggests that the Resource feature is designed for reading and inspecting data from local or remote sources. The Tool feature is used for executing tools with custom inputs, which doesn't seem directly related to reading a configuration file."

**Retrieved Sources:** `the_model_context_protocol.pdf` (Pages 25, 26, 44, 5), `agent_engineering_enterprise.pdf` (Page 68)

**Result:** PASS

**Analysis:** This is the most dramatic result in the evaluation. k=3 produced a confidently wrong answer; k=5 produced the correct answer. The difference is two additional chunks from `the_model_context_protocol.pdf` (pages 44 and 5). Page 5 likely contains the canonical definition of Resources, which directly contradicted the misleading `search_document` tool example on page 68 of `agent_engineering_enterprise.pdf`. With k=3, the misleading chunk dominated; with k=5, the definitional chunks outweighed it. This demonstrates that a single misleading chunk can corrupt the LLM's reasoning when the retrieval window is too narrow.

---

### Test 5 — H2: "How does MCP's user-controlled, opt-in authorization model mitigate the security risks of granting an LLM access to a local filesystem?"
**Difficulty:** Hard  
**Expected:** Opt-in authorization limits scope of LLM access; per-tool permissions, RBAC, and user confirmation gates prevent unauthorized filesystem operations

#### k=3
**System Response:**
> "Based on the provided context, I don't know how MCP's user-controlled, opt-in authorization model mitigates the security risks of granting a Large Language Model access to a local filesystem. The provided text only mentions operational recommendations and measures to reduce unauthorized access, but it doesn't specifically address the authorization model's impact on file-system access."

**Retrieved Sources:** `agent_engineering_enterprise.pdf` (Page 65), `MCP_landscape_security_threats.pdf` (Pages 24, 23)

**Result:** FAIL

#### k=5
**System Response:**
> "MCP's user-controlled, opt-in authorization model mitigates the security risks by implementing: requiring authentication for every connection, limiting network bindings to trusted local clients, and using HTTPS to serve file-system access points. Furthermore, by applying fine-grained permissioning — including per-tool scopes, role-based access control, and temporal policies — MCP ensures that sensitive data remains hidden from standard users while being disclosed to authorized IT operators as needed."

**Retrieved Sources:** `agent_engineering_enterprise.pdf` (Pages 65, 65, 98), `MCP_landscape_security_threats.pdf` (Pages 24, 23)

**Result:** PASS

**Analysis:** The same three source pages were retrieved at both k values, but k=5 added page 98 of `agent_engineering_enterprise.pdf` and a second chunk from page 65. The additional chunk from page 98 appears to contain the specific authorization mechanism details (per-tool scopes, RBAC, temporal policies) that allowed the model to construct a complete answer. This is a case of intra-document context dependency: the full answer required two non-adjacent chunks from the same document, which k=3 could not capture simultaneously.

---

## Results Summary

| Test | Question | Difficulty | k=3 Result | k=5 Result |
|------|----------|------------|------------|------------|
| 1 | What does MCP stand for? | Easy | FAIL | FAIL |
| 2 | Role of an MCP Server? | Medium | FAIL | PARTIAL PASS |
| 3 | Client-server handshake process | Medium | PARTIAL PASS | PASS |
| 4 | Resource vs Tool for static file? | Medium | FAIL (wrong) | PASS |
| 5 | Opt-in auth model and filesystem risk | Hard | FAIL | PASS |

| Configuration | Full Pass | Partial Pass | Fail |
|---------------|-----------|--------------|------|
| k=3 | 0/5 (0%) | 1/5 (20%) | 4/5 (80%) |
| k=5 | 3/5 (60%) | 1/5 (20%) | 1/5 (20%) |

---

## Analysis

### The Generator vs. Retriever Split

Across all ten runs (5 questions × 2 configurations), the Llama 3.1 (8B) generator followed the grounding prompt correctly in 9 of 10 cases — refusing to hallucinate when context was insufficient. The one exception was Test 1 at k=5, where the model speculated about the MCP acronym rather than abstaining. All failures at k=3 were retrieval failures, not generation failures.

### Why k=5 Improved Three Out of Four Failing Tests

The three tests that flipped from FAIL to PASS (Tests 2, 4, 5) all shared the same underlying cause: the answer required content from more than three non-adjacent document pages. In each case, the decisive chunks were pages that k=3 did not retrieve:

- **Test 2:** Pages 11 and 18 of `the_model_context_protocol.pdf` were needed alongside page 4.
- **Test 4:** Page 5 of `the_model_context_protocol.pdf` provided the Resource definition that neutralized the misleading tool example on page 68.
- **Test 5:** Page 98 of `agent_engineering_enterprise.pdf` contained the specific per-tool scoping details absent from pages 23–24 and 65.

### Why Test 1 Still Failed at k=5

The MCP acronym definition is almost certainly in the first one or two pages of each document. Both k=3 and k=5 consistently retrieved mid- and late-document pages (pages 18–19, 40, 44) with high MCP co-occurrence but no definition. This is an embedding alignment failure: the query "What does MCP stand for?" semantically matched pages that discuss MCP heavily, not the introductory pages where it is first defined. Fixing this requires either metadata-aware retrieval or a hybrid sparse search (BM25) that would match the literal string "MCP stands for."

### Root Causes

1. **Insufficient retrieval window (k=3).** With ~150+ pages across 5 documents and answers distributed across non-adjacent pages, k=3 is statistically unlikely to capture all necessary context.
2. **Fixed-size chunk boundary fragmentation.** The 800-character limit splits multi-paragraph definitions. Only one fragment is retrieved, missing the explanatory continuation.
3. **Dense-only retrieval bias.** The `nomic-embed-text` embedding model matches on semantic similarity, causing it to retrieve heavily-annotated mid-document pages over lightly-annotated introductory definition pages.

### Proposed Improvements

| Improvement | Addresses |
|---|---|
| Increase k to 6–8 | Retrieval window too narrow |
| Increase chunk_size to 1,200–1,500 | Definition fragmentation |
| Add hybrid BM25 + dense search | Embedding bias on acronym/exact-term queries |
| Use MMR (`search_type="mmr"`) | Redundant chunk retrieval (Test 5 retrieved page 65 twice at k=5) |
| Add page-range metadata filtering | Prioritize introductory sections for definitional queries |
