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
