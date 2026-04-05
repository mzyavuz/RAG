from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
import os
import shutil

# This is where Chroma will save its database files
CHROMA_PATH = os.path.join(os.path.dirname(__file__), "../data/chroma") 

def save_to_chroma(chunks, path=CHROMA_PATH):
    """
    Takes document chunks, embeds them, and saves them to a local Chroma database.
    Accepts an optional path so experiments can each use an isolated directory.
    """
    if os.path.exists(path):
        shutil.rmtree(path)

    print("Embedding chunks and building Chroma database...")
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    Chroma.from_documents(chunks, embeddings, persist_directory=path)
    print(f"Successfully saved {len(chunks)} chunks to {path}.")

# Optional: Add a function to load the database later
def get_chroma_db():
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    return Chroma(persist_directory=CHROMA_PATH, embedding_function=embeddings)