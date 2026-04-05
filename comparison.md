# Manual vs. Automated Evaluation Comparison
**Course:** SWE 580 – Applied Large Language Models
**Student:** M. Zeynep

This document compares the findings from two evaluation methods applied to the same RAG system:

- **Manual evaluation** (`manual_evaluation.md`) — 5 questions tested at k=3 and k=5, answers read and scored by hand
- **Automated evaluation** (`langsmith_evaluation.md`) — all 20 questions tested across 10 configurations, scored programmatically via keyword heuristics against reference answers logged in LangSmith

---

## 1. Scope Comparison

| Dimension | Manual Evaluation | Automated Evaluation |
|-----------|------------------|----------------------|
| Questions evaluated | 5 of 20 | 20 of 20 |
| Configurations tested | 2 (k=3, k=5, fixed chunk=800) | 10 (varying size, overlap, k) |
| Scoring method | Human judgment (Pass / Partial / Fail) | Keyword heuristics against reference answers |
| Granularity of scoring | 3-point (0, 0.5, 1.0) | 3-point (0, 0.5, 1.0) |
| Source documents recorded | Yes (filename + page) | No (context not stored) |
| Latency recorded | No | Yes |

---

## 2. Score Agreement on the 5 Overlapping Questions

Both evaluations covered the same 5 questions at k=3 and k=5 (chunk size 800 in both). The table below aligns scores side by side.

| Q | Question | Manual k=3 | Auto k=3 (Exp03) | Manual k=5 | Auto k=5 (Exp01) |
|---|----------|-----------|-----------------|-----------|-----------------|
| E1 | What does MCP stand for? | 0.0 FAIL | 0.0 | 0.0 FAIL | 1.0 |
| M1 | Role of an MCP Server? | 0.0 FAIL | 0.0 | 0.5 PARTIAL | 0.5 |
| M2 | Client-server handshake | 0.5 PARTIAL | 1.0 | 1.0 PASS | 1.0 |
| M3 | Resource vs Tool (static file) | 0.0 FAIL (wrong) | 0.0 | 1.0 PASS | 0.0 |
| H1 | Opt-in auth & filesystem risk | 0.0 FAIL | 1.0 | 1.0 PASS | 1.0 |

**Agreement rate: 6/10 scores match exactly. 4/10 diverge.**

---

## 3. Where the Two Methods Agree

### Q: Role of an MCP Server (both k=3 and k=5)
Both methods gave 0.0 at k=3 and 0.5 at k=5. This is the strongest point of agreement: the manual reviewer saw a vague, hedged answer that cited chapter titles without defining the server's role, and the keyword heuristic correctly penalized it because neither "expose" nor the full "data + tools" combination appeared in the k=3 response. At k=5, both methods converged on 0.5 — a partial answer that names the three components but describes the server role at a generic request/response level.

### Q: Client-server handshake (k=3 and k=5)
Both methods scored k=5 as 1.0. The answer contained "initialize," "capabilities," and a structured step list — triggering full score in both the human reader and the keyword check. At k=3, the manual reviewer gave 0.5 (partial answer, missing shutdown) while the automated heuristic gave 1.0 (found "initialize" + "request"). This is the one case where the automated scorer was *more lenient* than the human — the heuristic only checked for two keywords, not for completeness.

### Q: Opt-in auth and filesystem risk (k=3 → k=5 improvement)
Both methods recorded 0.0 at k=3 and 1.0 at k=5. The manual reviewer found the k=3 answer was a clean "I don't know," and the automated heuristic agreed (no authorization keywords present). At k=5, the answer mentioned "permission," "fine-grained," and "per-tool scopes" — triggering full score in both evaluations. This question shows the cleanest agreement: k=3 fails, k=5 passes, both methods see it the same way.

---

## 4. Where the Two Methods Diverge

### Divergence 1 — Q: What does MCP stand for? (k=5)
- **Manual: 0.0 FAIL** — the response said "I don't see an explicit explanation" and speculated about what MCP "appears to be." The human judge correctly identified this as a grounding violation (the model guessed instead of abstaining).
- **Automated: 1.0 PASS** — the keyword heuristic searched for "model context protocol" in the answer. The k=5 response happened to contain that string in passing context ("...it appears to be related to a protocol...Model Context Protocol") and the heuristic matched it.

**Lesson:** The automated heuristic rewarded surface-level keyword presence. The manual evaluator penalized a response that found the answer by inference rather than retrieval — a meaningful distinction the keyword approach cannot capture. The manual score is more accurate here.

### Divergence 2 — Q: Resource vs Tool for static file (k=5)
- **Manual: 1.0 PASS** — the k=5 response correctly recommended Resource, citing the Inspector UI description that "Resources lists available resources with MIME types and metadata, and supports content inspection."
- **Automated Exp01 (k=5): 0.0 FAIL** — the heuristic scored this as fail because it counted occurrences of "resource" vs "tool" in the answer, and the response discussed both primitives before giving the final recommendation. The count-based approach misfired because the explanation of *why Tool is wrong* required mentioning "tool" multiple times.

**Lesson:** Comparative reasoning questions ("which of A or B?") are poorly suited to count-based heuristics. The manual evaluator understood the structure of the argument; the automated scorer read the word frequency and drew the wrong conclusion. Manual evaluation is more reliable for this question type.

### Divergence 3 — Q: Client-server handshake (k=3)
- **Manual: 0.5 PARTIAL** — the human reviewer penalized the k=3 answer for missing the shutdown phase and being vague on the `initialized` notification sequence.
- **Automated: 1.0 PASS** — the heuristic found "initialize" and "request" in the answer and scored it fully correct.

**Lesson:** The automated heuristic had no way to check for *completeness* — it only checked for presence of key terms. A partially correct answer that mentions the right words scores identically to a complete answer. Manual evaluation captures this distinction.

---

## 5. Overall Score Comparison at k=3 and k=5

Averaging across the 5 shared questions:

| Configuration | Manual Avg | Automated Avg |
|---------------|-----------|---------------|
| k=3, size=800 | 0.10 | 0.40 |
| k=5, size=800 | 0.70 | 0.70 |

The automated scorer is **significantly more lenient at k=3** (0.40 vs 0.10). This is because at k=3, the system frequently produced vague, hedged responses that still contained enough relevant keywords to trigger partial or full scores in the heuristic — but which a human reader would recognize as insufficient. At k=5, the two methods converge (0.70 each) because the answers were substantive enough that keyword presence reliably correlated with answer quality.

---

## 6. What the Automated Evaluation Added Beyond Manual

The automated evaluation revealed findings that the 5-question manual test could not:

**Cross-configuration trends invisible at 5 questions:**
- Exp 07 (size=400) collapsed on Easy definitional questions (Q02, Q04, Q05) — a finding that requires testing across all 20 questions to see clearly.
- Q08 (Resource definition) failed in **all 10 experiments**, confirming it is a structural embedding problem rather than a configuration-sensitive one. The manual evaluation tested Q08 indirectly via Q03 (static file question), which masked this pattern.
- Q14 (TypeScript True/False) was highly sensitive to chunk size — passing in Exp 01, 03, 08, 10 and failing in 02, 04, 05, 06, 07, 09. Manual testing did not include this question.

**Latency data:**
The manual evaluation recorded no latency. The automated runs showed that k=10 (Exp 02) added 14 seconds of average latency over the baseline while scoring *lower* — a cost/benefit trade-off only visible with instrumented runs.

**The Goldilocks finding:**
The manually tested range was only k=3 vs k=5 at fixed chunk size 800. The automated experiments showed that the real optimum is at size=1200, overlap=250, k=7 (Exp 10, score=0.825) — a configuration that the manual evaluation's design space did not include and could not have discovered.

---

## 7. Reliability Assessment

| Criterion | Manual | Automated |
|-----------|--------|-----------|
| Handles nuanced/comparative answers | ✓ High | ✗ Low |
| Detects grounding violations (speculation) | ✓ High | ✗ Low |
| Checks answer completeness | ✓ High | ✗ Low |
| Scalable to many configurations | ✗ Low | ✓ High |
| Reproducible / consistent | ✗ Varies by reviewer | ✓ Deterministic |
| Sensitive to answer structure vs keywords | ✓ | ✗ |
| Captures latency | ✗ | ✓ |

**Conclusion:** The two methods are complementary. Manual evaluation is more accurate per question — it catches grounding violations, rewards completeness, and correctly scores comparative reasoning. Automated evaluation is more scalable — it enables testing 200 question-answer pairs across 10 configurations in a single pipeline run, which is necessary to identify parameter trends and the optimal configuration. For this assignment, the manual evaluation provided ground truth for 5 critical questions; the automated evaluation extended coverage to all 20 questions and 10 configurations. The ideal evaluation pipeline uses automated scoring for breadth and manual review for depth on the highest-variance and highest-stakes questions.
