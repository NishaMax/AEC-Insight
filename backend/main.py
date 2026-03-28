from fastapi import FastAPI, UploadFile, File, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
import shutil
from dotenv import load_dotenv

# Import our new functional services
from services.document_service import DocumentService
from services.vector_db_service import VectorDBService

app = FastAPI(title="BuildSight RAG API", description="API for architectural documents RAG system")

# Define CORS to allow Next.js frontend to communicate
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update this to specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

load_dotenv() # Load environment variables like OPENAI_API_KEY from .env locally

@app.get("/")
async def root():
    return {"message": "Welcome to BuildSight RAG API"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}

# Initialize Services globally (or using FastAPI dependencies in larger apps)
vector_db_service = VectorDBService()

async def process_document(file_path: str, filename: str):
    """Heavy background task to process, chunk, and embed PDFs."""
    print(f"Starting to process {filename}...")
    try:
        # 1. Extract raw text from Document
        raw_text = DocumentService.extract_text_from_pdf(filepath=file_path)
        print(f"Extracted {len(raw_text)} characters from {filename}.")
        
        # 2. Chunk text semantically
        chunks = DocumentService.chunk_text(text=raw_text)
        print(f"Split document into {len(chunks)} chunks.")
        
        # 3. Embed elements and store in Vector DB
        vector_db_service.add_chunks(chunks=chunks, filename=filename)
        
        print(f"Finished processing {filename}. Vector embeddings created securely.")
        
    except Exception as e:
        print(f"Failed to process document {filename} due to error: {e}")

@app.post("/api/documents/upload")
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
    
    # Save uploaded file temporarily
    temp_file_path = f"temp_{file.filename}"
    with open(temp_file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Add the document processing to the background task
    background_tasks.add_task(process_document, temp_file_path, file.filename)
    
    return {"filename": file.filename, "message": "Upload successful. Processing in background."}
