import os
import traceback
from typing import List

try:
    # Prefer the actively maintained fork
    from pypdf import PdfReader  # type: ignore
except Exception:  # pragma: no cover
    # Fallback for environments that still use PyPDF2
    from PyPDF2 import PdfReader  # type: ignore

from langchain_text_splitters import RecursiveCharacterTextSplitter

class DocumentService:
    """Service to handle document parsing and text manipulation."""
    
    @staticmethod
    def extract_text_from_pdf(filepath: str) -> str:
        """Extracts all raw text from a PDF file."""
        text = ""
        try:
            with open(filepath, "rb") as file:
                reader = PdfReader(file)
                for page in reader.pages:
                    page_text = page.extract_text() or ""
                    text += page_text + "\n"
        except Exception as e:
            print(f"Error extracting text from {filepath}: {e}")
            traceback.print_exc()
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
