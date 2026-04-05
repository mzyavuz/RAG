"""
run_experiments.py
------------------
Runs 10 RAG experiments across different chunking and retrieval configurations,
evaluated against the LangSmith dataset "SWE580_MCP_Evaluation".

Before running:
  1. Set your LangSmith API key:
       export LANGCHAIN_API_KEY="ls-..."
       export LANGCHAIN_TRACING_V2="true"
       export LANGCHAIN_PROJECT="SWE580-RAG"
  2. Make sure Ollama is running with nomic-embed-text and llama3.1:8b pulled.
  3. Run from the project root:
       python3 src/run_experiments.py
"""

import os
import sys

# Add src/ to path so local module imports (database, document_processor) work
sys.path.insert(0, os.path.dirname(__file__))

from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings, OllamaLLM  # OllamaLLM used inside build_predict_fn
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langsmith import Client
from langsmith.evaluation import evaluate

from document_processor import load_and_chunk_documents
from database import save_to_chroma
from evaluate import correctness_evaluator, relevance_evaluator, hallucination_evaluator

DATA_DIR = os.path.join(os.path.dirname(__file__), "../data")

# ---------------------------------------------------------------------------
# Experiment configurations
# ---------------------------------------------------------------------------

experiments = [
    # Group 1: Baseline & Top-K Scaling (testing context starvation)
    {"size": 800,  "overlap": 150, "k": 5},   # 1. Baseline (control group)
    {"size": 800,  "overlap": 150, "k": 10},  # 2. High context — double the retrieval
    {"size": 800,  "overlap": 150, "k": 3},   # 3. Low context — verify k=5 was needed

    # Group 2: The "Big Picture" approach (testing text fragmentation)
    {"size": 1500, "overlap": 200, "k": 5},   # 4. Large chunks — better for complex logic
    {"size": 1500, "overlap": 200, "k": 8},   # 5. Large chunks + high k — massive context
    {"size": 2500, "overlap": 400, "k": 3},   # 6. Massive chunks — whole pages at a time

    # Group 3: The "Sniper" approach (testing highly specific retrieval)
    {"size": 400,  "overlap": 50,  "k": 5},   # 7. Small chunks — expected to fail on complex Qs
    {"size": 400,  "overlap": 50,  "k": 15},  # 8. Small chunks + high k — stitching puzzle pieces

    # Group 4: The Overlap Fix
    {"size": 800,  "overlap": 400, "k": 5},   # 9. Heavy overlap — prevents definitions being split

    # Group 5: The "Goldilocks" estimate
    {"size": 1200, "overlap": 250, "k": 7},   # 10. Sweet spot — moderate increase across all vars
]

# ---------------------------------------------------------------------------
# Prompt (shared across all experiments)
# ---------------------------------------------------------------------------

PROMPT_TEMPLATE = """You are a helpful AI assistant for a software engineering student.
Use the following pieces of retrieved context to answer the question at the end.
If you don't know the answer based on the context, just say that you don't know, don't try to make up an answer.

Context:
{context}

Question: {question}

Helpful Answer:"""

PROMPT = PromptTemplate(
    template=PROMPT_TEMPLATE, input_variables=["context", "question"]
)

# Evaluators are imported from evaluate.py
evaluators = [correctness_evaluator, relevance_evaluator, hallucination_evaluator]

# ---------------------------------------------------------------------------
# Per-experiment RAG chain factory
# ---------------------------------------------------------------------------

def build_predict_fn(chroma_path: str, k: int):
    """
    Returns a predict function closed over the given path and k value.
    Each experiment passes its own isolated directory so there are no
    file-lock conflicts when the next experiment rebuilds the DB.
    """
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    db = Chroma(persist_directory=chroma_path, embedding_function=embeddings)
    retriever = db.as_retriever(search_kwargs={"k": k})
    llm = OllamaLLM(model="llama3.1:8b")

    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | PROMPT
        | llm
        | StrOutputParser()
    )

    def predict(inputs: dict) -> dict:
        question = inputs["question"]
        answer = chain.invoke(question)
        # Also capture which source pages were used
        source_docs = retriever.invoke(question)
        sources = [
            f"{os.path.basename(d.metadata.get('source', 'unknown'))} p{d.metadata.get('page', '?')}"
            for d in source_docs
        ]
        return {"answer": answer, "context": " | ".join(sources)}

    return predict

# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    client = Client()

    for i, config in enumerate(experiments, start=1):
        size    = config["size"]
        overlap = config["overlap"]
        k       = config["k"]

        print(f"\n{'='*60}")
        print(f"  Experiment {i}/10 — size={size}, overlap={overlap}, k={k}")
        print(f"{'='*60}")

        # Each experiment gets its own isolated directory — no deletion needed,
        # no file-lock conflicts with the previous experiment's open DB handle.
        chroma_path = os.path.join(DATA_DIR, f"chroma_exp_{i:02d}")

        # 1. Build the vector DB for this experiment's chunk settings
        print("  [1/3] Rebuilding Chroma database...")
        chunks = load_and_chunk_documents(chunk_size=size, chunk_overlap=overlap)
        save_to_chroma(chunks, path=chroma_path)
        print(f"        {len(chunks)} chunks indexed.")

        # 2. Build the predict function pointed at this experiment's DB
        print("  [2/3] Building RAG chain...")
        predict_fn = build_predict_fn(chroma_path=chroma_path, k=k)

        # 3. Run LangSmith evaluation
        experiment_name = f"Exp_{+i:02d}_Size{size}_Over{overlap}_K{k}"
        print(f"  [3/3] Running evaluation: {experiment_name}")

        results = evaluate(
            predict_fn,
            data="SWE580_MCP_Evaluation",
            evaluators=evaluators,
            experiment_prefix=experiment_name,
            max_concurrency=1,   # Sequential to avoid Ollama overload
        )

        print(f"  Done. Results logged to LangSmith under '{experiment_name}'.")

    print("\nAll 10 experiments complete.")
