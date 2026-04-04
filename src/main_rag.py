from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.llms import Ollama
from langchain_classic.chains import RetrievalQA
from langchain_classic.prompts import PromptTemplate

# Point this to where you saved your database in the previous step
CHROMA_PATH = "../data/chroma"

def get_rag_chain():
    """
    Sets up the RAG pipeline: Database -> Retriever -> Prompt -> LLM.
    """
    print("Loading Chroma database...")
    # 1. Load the database with the exact same embedding model you used to create it
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embeddings)
    
    # Configure the retriever to fetch the top 3 most relevant chunks
    retriever = db.as_retriever(search_kwargs={"k": 3})

    # 2. Initialize the local LLM
    print("Initializing Llama 3.1 (8B) model via Ollama...")
    llm = Ollama(model="llama3.1:8b")

    # 3. Create a custom prompt template
    # This forces the LLM to only use the retrieved context and prevents hallucinations
    prompt_template = """
    You are a helpful AI assistant for a software engineering student. 
    Use the following pieces of retrieved context to answer the question at the end. 
    If you don't know the answer based on the context, just say that you don't know, don't try to make up an answer.

    Context:
    {context}

    Question: {question}
    
    Helpful Answer:"""
    
    PROMPT = PromptTemplate(
        template=prompt_template, input_variables=["context", "question"]
    )

    # 4. Build the LangChain RetrievalQA chain
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff", # "stuff" means it stuffs all the retrieved chunks into the prompt
        retriever=retriever,
        return_source_documents=True, # Useful for debugging and verifying the source
        chain_type_kwargs={"prompt": PROMPT}
    )
    
    return qa_chain

if __name__ == "__main__":
    # Initialize the system
    rag_system = get_rag_chain()
    
    # Test it with a query! 
    # (Change this question to match the actual content of your MCP PDFs)
    test_question = "What is the Model Context Protocol and how does it handle security?"
    
    print(f"\nAsking: '{test_question}'\n")
    print("Thinking...\n")
    
    # Run the query through the chain
    response = rag_system.invoke({"query": test_question})
    
    # Print the AI's generated answer
    print("--- ANSWER ---")
    print(response["result"])
    
    # Optional: Print the source documents it used to get that answer
    print("\n--- SOURCES USED ---")
    for doc in response["source_documents"]:
        print(f"- {doc.metadata.get('source', 'Unknown')} (Page {doc.metadata.get('page', 'Unknown')})")