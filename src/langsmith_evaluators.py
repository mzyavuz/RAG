"""
langsmith_evaluators.py
-----------------------
Custom evaluator functions for the LangSmith UI.

HOW TO USE IN LANGSMITH UI:
  1. Go to LangSmith → your project → Evaluators
  2. Create a new Python evaluator for each of the three functions below
  3. For each evaluator, paste only the body of the corresponding perform_eval function
     (LangSmith wraps it in its own function — do NOT include the def line)

Note: The LangSmith UI uses dict-style access (run['outputs']), which differs from
      the SDK-style attribute access (run.outputs) used in evaluate.py.
"""


# ---------------------------------------------------------------------------
# Evaluator 1: Correctness
# Checks whether the answer contains the key facts from the reference answer.
# ---------------------------------------------------------------------------

def correctness_evaluator():
    def perform_eval(run, example):
        answer = run['outputs'].get('answer', '')
        reference = example['outputs'].get('expected_answer', '')

        if not reference:
            return {"score": 0.5, "comment": "No reference answer provided"}

        ref_words = set(reference.lower().split())
        ans_words = set(answer.lower().split())

        # Remove stopwords
        stopwords = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'it',
                     'in', 'on', 'at', 'to', 'for', 'of', 'and', 'or', 'but',
                     'with', 'that', 'this', 'from', 'be', 'by', 'as', 'not'}
        ref_words -= stopwords
        ans_words -= stopwords

        if not ref_words:
            return {"score": 0.5}

        overlap = len(ref_words & ans_words) / len(ref_words)

        if overlap >= 0.6:
            score = 1.0
        elif overlap >= 0.3:
            score = 0.5
        else:
            score = 0.0

        return {"score": score, "comment": f"Keyword overlap: {overlap:.0%}"}

    return perform_eval


# ---------------------------------------------------------------------------
# Evaluator 2: Relevance
# Checks whether the answer actually addresses the question.
# ---------------------------------------------------------------------------

def relevance_evaluator():
    def perform_eval(run, example):
        answer = run['outputs'].get('answer', '').lower()
        question = example['inputs'].get('question', '').lower()

        # Safe refusal — relevant by definition
        if "i don't know" in answer or "i do not know" in answer:
            return {"score": 0.5, "comment": "Safe refusal — partially relevant"}

        # Off-topic or empty
        if len(answer.strip()) < 20:
            return {"score": 0.0, "comment": "Answer too short"}

        # Check if any meaningful question words appear in the answer
        question_words = set(question.split()) - {
            'what', 'how', 'why', 'when', 'where', 'which', 'is', 'are',
            'the', 'a', 'an', 'does', 'do', 'did', 'can', 'could', 'should',
            'would', 'will', 'be', 'been', 'being', 'have', 'has', 'had',
            'it', 'in', 'on', 'at', 'to', 'for', 'of', 'and', 'or'
        }

        if not question_words:
            return {"score": 0.5}

        match_count = sum(1 for w in question_words if w in answer)
        relevance = match_count / len(question_words)

        if relevance >= 0.4:
            score = 1.0
        elif relevance >= 0.2:
            score = 0.5
        else:
            score = 0.0

        return {"score": score, "comment": f"Question term coverage: {relevance:.0%}"}

    return perform_eval


# ---------------------------------------------------------------------------
# Evaluator 3: Hallucination_Free
# Checks whether the answer stays within the retrieved context.
# ---------------------------------------------------------------------------

def hallucination_evaluator():
    def perform_eval(run, example):
        answer = run['outputs'].get('answer', '').lower()
        context = run['outputs'].get('context', '').lower()

        # Safe refusals don't hallucinate
        if "i don't know" in answer or "i do not know" in answer:
            return {"score": 1.0, "comment": "Safe refusal — no hallucination"}

        if not context:
            return {"score": 0.5, "comment": "No context available to check against"}

        # Check that key facts from the answer appear somewhere in the context
        answer_words = set(answer.split()) - {
            'the', 'a', 'an', 'is', 'are', 'was', 'were', 'it', 'in',
            'on', 'at', 'to', 'for', 'of', 'and', 'or', 'but', 'with',
            'that', 'this', 'from', 'be', 'by', 'as', 'not', 'its', 'their'
        }

        if not answer_words:
            return {"score": 0.5}

        grounded_count = sum(1 for w in answer_words if w in context)
        grounding_ratio = grounded_count / len(answer_words)

        if grounding_ratio >= 0.5:
            score = 1.0
        elif grounding_ratio >= 0.25:
            score = 0.5
        else:
            score = 0.0

        return {"score": score, "comment": f"Context grounding: {grounding_ratio:.0%}"}

    return perform_eval
