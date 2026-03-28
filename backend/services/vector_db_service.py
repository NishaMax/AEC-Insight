import os
from typing import List, Dict, Any
import chromadb
from chromadb.config import Settings
from langchain_openai import OpenAIEmbeddings

class VectorDBService:
    """Service to handle vector database operations (ChromaDB + OpenAI Embeddings)."""
    
    def __init__(self):
        # We will dynamically pull the key from environment variables
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small"
        )
        
        # Local persistent Chroma database
        self.chroma_client = chromadb.PersistentClient(path="./chroma_db")
        self.collection_name = "architectural_docs"
        
        self.collection = self.chroma_client.get_or_create_collection(
            name=self.collection_name
        )
        
    def add_chunks(self, chunks: List[str], filename: str) -> None:
        """Embeds and uploads text chunks to ChromaDB."""
        if not chunks:
            return

        # Generate unique IDs for each chunk based on filename and index
        ids = [f"{filename}_chunk_{i}" for i in range(len(chunks))]
        metadatas = [{"source": filename, "chunk_index": i} for i in range(len(chunks))]
        
        # We explicitly embed using the specified OpenAI model 
        embedded_docs = self.embeddings.embed_documents(chunks)
        
        self.collection.add(
            embeddings=embedded_docs,
            documents=chunks,
            metadatas=metadatas,
            ids=ids
        )
        print(f"Successfully added {len(chunks)} chunks to vector database for {filename}.")

    def get_all_documents(self) -> List[str]:
        """Retrieves a list of unique document filenames stored in the vector database."""
        try:
            results = self.collection.get(include=["metadatas"])
            metadatas = results.get("metadatas", [])
            
            # Extract unique source filenames
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
            # Delete based on the metadata source property
            self.collection.delete(where={"source": filename})
            print(f"Successfully deleted document '{filename}' from vector database.")
            return True
        except Exception as e:
            print(f"Error deleting document '{filename}': {e}")
            return False
