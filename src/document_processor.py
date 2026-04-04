from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from database import save_to_chroma

def load_and_chunk_documents(directory_path="../docs", chunk_size=1000, chunk_overlap=200):
    """
    Loads PDFs from a directory and splits them into configurable chunks.
    """
    print(f"Loading documents from {directory_path}...")
    loader = PyPDFDirectoryLoader(directory_path)
    documents = loader.load()
    print(f"Loaded {len(documents)} pages.")

    print(f"Splitting text with chunk_size={chunk_size} and overlap={chunk_overlap}...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        is_separator_regex=False,
    )
    
    chunks = text_splitter.split_documents(documents)
    print(f"Created {len(chunks)} document chunks.")
    
    return chunks

# Test the function to see it in action
# if __name__ == "__main__":
#     # Ensure you have a 'docs' folder with your 5 MCP PDFs inside!
#     my_chunks = load_and_chunk_documents(chunk_size=800, chunk_overlap=150)
    
#     # Print the first chunk to verify it worked
#     if my_chunks:
#         print("\n--- First Chunk Sample ---")
#         print(my_chunks[0].page_content)


if __name__ == "__main__":
    # 1. Load and chunk the PDFs
    my_chunks = load_and_chunk_documents(directory_path="../docs", chunk_size=800, chunk_overlap=150)
    
    # 2. Save them to the database
    if my_chunks:
        save_to_chroma(my_chunks)