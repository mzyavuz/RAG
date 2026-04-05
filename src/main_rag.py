from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings, OllamaLLM
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
import os

CHROMA_PATH = os.path.join(os.path.dirname(__file__), "../data/chroma")

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

def get_rag_chain():
    """
    Sets up the RAG pipeline using LCEL: Database -> Retriever -> Prompt -> LLM.
    """
    print("Loading Chroma database...")
    # 1. Load the database with the exact same embedding model you used to create it
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embeddings)

    # Configure the retriever to fetch the top 3 most relevant chunks
    retriever = db.as_retriever(search_kwargs={"k": 5})

    

    # 2. Initialize the local LLM
    print("Initializing Llama 3.1 (8B) model via Ollama...")
    llm = OllamaLLM(model="llama3.1:8b")

    # 3. Create a custom prompt template
    # This forces the LLM to only use the retrieved context and prevents hallucinations
    prompt_template = """You are a helpful AI assistant for a software engineering student.
    Use the following pieces of retrieved context to answer the question at the end.
    If you don't know the answer based on the context, just say that you don't know, don't try to make up an answer.

    Context:
    {context}

    Question: {question}

    Helpful Answer:"""

    prompt = PromptTemplate(
        template=prompt_template, input_variables=["context", "question"]
    )

    # 4. Build the chain using LCEL (LangChain Expression Language)
    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    return rag_chain, retriever

if __name__ == "__main__":
    # Initialize the system
    rag_chain, retriever = get_rag_chain()

    print("\n" + "="*50)
    print("RAG System Ready!")
    print("  - Type 'test' to run the hardcoded test.")
    print("  - Type 'exit' to quit.")
    print("  - Or just type your question directly!")
    print("="*50 + "\n")

    # Create an infinite loop to ask multiple questions
    while True:
        user_input = input("\nYour Input: ").strip()

        # 1. Check if the user wants to exit
        if user_input.lower() in ['exit', 'quit']:
            print("Exiting system... Goodbye!")
            break

        # 2. Check if the user wants to run the hardcoded test
        if user_input.lower() == 'test':
            print("\nRUNNING HARDCODED TEST...")
            query = "What is the Model Context Protocol and how does it handle security?"
            print(f"Asking: '{query}'")

        # 3. Otherwise, treat the input as a direct question
        else:
            if not user_input:
                continue  # Skip if the user just pressed Enter by mistake
            query = user_input

        print("\nThinking...\n")

        # Retrieve source docs separately for display
        source_docs = retriever.invoke(query)

        # Run the query through the chain
        result = rag_chain.invoke(query)

        # Print the AI's generated answer
        print("--- ANSWER ---")
        print(result)

        # Print the source documents it used
        print("\n--- SOURCES USED ---")
        for doc in source_docs:
            print(f"- {doc.metadata.get('source', 'Unknown')} (Page {doc.metadata.get('page', 'Unknown')})")
        print("-" * 20)