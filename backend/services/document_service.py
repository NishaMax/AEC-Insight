import fitz  # PyMuPDF
from typing import List
from langchain.text_splitter import RecursiveCharacterTextSplitter

class DocumentService:
    """Service to handle document parsing and text manipulation."""
    
    @staticmethod
    def extract_text_from_pdf(filepath: str) -> str:
        """Extracts all raw text from a PDF file."""
        text = ""
        try:
            with fitz.open(filepath) as doc:
                for page in doc:
                    text += page.get_text("text") + "\n"
        except Exception as e:
            print(f"Error extracting text from {filepath}: {e}")
            raise
        return text

    @staticmethod
    def chunk_text(text: str, chunk_size: int = 1500, chunk_overlap: int = 200) -> List[str]:
        """Splits raw text into conceptually relevant chunks safely."""
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ".", " ", ""],
            length_function=len,
        )
        chunks = text_splitter.split_text(text)
        return chunks
