import os
from typing import List

import chromadb
from langchain_google_genai import GoogleGenerativeAIEmbeddings

class VectorDBService:
    """Service to handle vector database operations (ChromaDB + Gemini Embeddings)."""

    def __init__(self):
        # Gemini API key is read from environment variable GOOGLE_API_KEY
        # (load_dotenv() is called in main.py)
        self.embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")

        # Local persistent Chroma database
        self.chroma_client = chromadb.PersistentClient(path="./chroma_db")
        self.collection_name = "architectural_docs"

        self.collection = self.chroma_client.get_or_create_collection(name=self.collection_name)

    def add_chunks(self, chunks: List[str], filename: str) -> None:
        """Embeds and uploads text chunks to ChromaDB."""
        if not chunks:
            return

        ids = [f"{filename}_chunk_{i}" for i in range(len(chunks))]
        metadatas = [{"source": filename, "chunk_index": i} for i in range(len(chunks))]

        embedded_docs = self.embeddings.embed_documents(chunks)

        self.collection.add(
            embeddings=embedded_docs,
            documents=chunks,
            metadatas=metadatas,
            ids=ids,
        )
        print(f"Successfully added {len(chunks)} chunks to vector database for {filename}.")

    def get_all_documents(self) -> List[str]:
        """Retrieves a list of unique document filenames stored in the vector database."""
        try:
            results = self.collection.get(include=["metadatas"])
            metadatas = results.get("metadatas", [])

            unique_sources = set()
            for metadata in metadatas:
                if metadata and "source" in metadata:
                    unique_sources.add(metadata["source"])

            return list(unique_sources)
        except Exception as e:
            print(f"Error retrieving documents from vector database: {e}")
            return []

    def delete_document(self, filename: str) -> bool:
        """Deletes all chunks associated with a specific document filename."""
        try:
            self.collection.delete(where={"source": filename})
            print(f"Successfully deleted document '{filename}' from vector database.")
            return True
        except Exception as e:
            print(f"Error deleting document '{filename}': {e}")
            return False
