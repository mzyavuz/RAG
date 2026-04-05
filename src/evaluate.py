from langsmith import Client, evaluate
from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate
from main_rag import get_rag_chain  # Importing your existing RAG system!

# 1. Initialize our Judge LLM
# We use the same local model to act as the grader
judge_llm = OllamaLLM(model="llama3.1:8b", temperature=0)

def predict_rag_answer(inputs: dict) -> dict:
    """
    This is the target function LangSmith will call for each question in the dataset.
    """
    # 1. Unpack the tuple properly!
    rag_chain, retriever = get_rag_chain()
    
    # Extract the question string
    question = inputs["question"]
    
    # 2. Invoke the LCEL chain (pass the question string directly)
    answer = rag_chain.invoke(question)
    
    # 3. Use the retriever manually to get the context for the Hallucination Evaluator
    source_docs = retriever.invoke(question)
    context_used = "\n\n".join([doc.page_content for doc in source_docs])
    
    return {
        "answer": answer,
        "context": context_used
    }
# --- CUSTOM EVALUATORS ---

def correctness_evaluator(run, example) -> dict:
    """Grades if the AI's answer matches the expected expected answer."""
    student_answer = run.outputs["answer"]
    expected_answer = example.outputs["expected_answer"]
    
    prompt = f"""
    You are a strict teacher grading a test.
    Expected Answer: {expected_answer}
    Student Answer: {student_answer}
    
    Does the student's answer correctly state the core facts of the expected answer? 
    Respond ONLY with "1" for Yes, or "0" for No. Do not say anything else.
    """
    score_str = judge_llm.invoke(prompt).strip()
    score = 1 if "1" in score_str else 0
    
    return {"key": "Correctness", "score": score}

def relevance_evaluator(run, example) -> dict:
    """Grades if the AI actually answered the prompt, or went off on a tangent."""
    question = example.inputs["question"]
    student_answer = run.outputs["answer"]
    
    prompt = f"""
    Question: {question}
    Answer: {student_answer}
    
    Does the answer directly address the question asked? If they said "I don't know", score it 0.
    Respond ONLY with "1" for Yes, or "0" for No.
    """
    score_str = judge_llm.invoke(prompt).strip()
    score = 1 if "1" in score_str else 0
    
    return {"key": "Relevance", "score": score}

def hallucination_evaluator(run, example) -> dict:
    """Grades if the AI made up facts not found in the retrieved context."""
    student_answer = run.outputs["answer"]
    retrieved_context = run.outputs["context"]
    
    # If the AI safely refused to answer, it didn't hallucinate!
    if "I don't know" in student_answer or "I do not know" in student_answer:
        return {"key": "Hallucination_Free", "score": 1}
        
    prompt = f"""
    Context: {retrieved_context}
    Answer: {student_answer}
    
    Is every factual statement in the Answer explicitly supported by the Context?
    Respond ONLY with "1" for Yes (No hallucinations), or "0" for No (It hallucinated).
    """
    score_str = judge_llm.invoke(prompt).strip()
    score = 1 if "1" in score_str else 0
    
    return {"key": "Hallucination_Free", "score": score}

# --- RUN THE PIPELINE ---

if __name__ == "__main__":
    client = Client()
    
    print("🚀 Starting LangSmith Evaluation Pipeline...")
    print("This will take a few minutes as Llama 3.1 processes all 20 questions and grades them.")
    
    experiment_results = evaluate(
        predict_rag_answer, # The function that runs your RAG
        data="SWE580_MCP_Evaluation", # The dataset we uploaded earlier
        evaluators=[correctness_evaluator, relevance_evaluator, hallucination_evaluator],
        experiment_prefix="Baseline_RAG_Test",
    )
    
    print("\n✅ Evaluation complete! Check your LangSmith dashboard to see the metrics.")