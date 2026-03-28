import os
from typing import List
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
