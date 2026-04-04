from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaEmbeddings
import os
import shutil

# This is where Chroma will save its database files
CHROMA_PATH = os.path.join(os.path.dirname(__file__), "../data/chroma") 

def save_to_chroma(chunks):
    """
    Takes document chunks, embeds them, and saves them to a local Chroma database.
    """
    # Clear out the database first if you want to start fresh 
    # (Useful when you are tweaking chunk sizes later!)
    if os.path.exists(CHROMA_PATH):
        shutil.rmtree(CHROMA_PATH)

    print("Embedding chunks and building Chroma database...")
    
    # Initialize the Ollama embedding model
    embeddings = OllamaEmbeddings(model="nomic-embed-text")

    # Create the vector store
    db = Chroma.from_documents(
        chunks, 
        embeddings, 
        persist_directory=CHROMA_PATH
    )
    
    # Save it to disk
    db.persist()
    print(f"Successfully saved {len(chunks)} chunks to {CHROMA_PATH}.")

# Optional: Add a function to load the database later
def get_chroma_db():
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    return Chroma(persist_directory=CHROMA_PATH, embedding_function=embeddings)