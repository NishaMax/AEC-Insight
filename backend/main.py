from fastapi import FastAPI, UploadFile, File, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
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

# Dictionary to keep track of document processing status
document_statuses = {}

class ChatRequest(BaseModel):
    query: str

async def process_document(file_path: str, filename: str):
    """Heavy background task to process, chunk, and embed PDFs."""
    print(f"Starting to process {filename}...")
    document_statuses[filename] = "processing"
    try:
        # 1. Extract raw text from Document
        raw_text = DocumentService.extract_text_from_pdf(filepath=file_path)
        print(f"Extracted {len(raw_text)} characters from {filename}.")
        
        # 2. Chunk text semantically
        chunks = DocumentService.chunk_text(text=raw_text)
        print(f"Split document into {len(chunks)} chunks.")
        
        # 3. Embed elements and store in Vector DB
        document_statuses[filename] = "embedding"
        vector_db_service.add_chunks(chunks=chunks, filename=filename)
        
        print(f"Finished processing {filename}. Vector embeddings created securely.")
        document_statuses[filename] = "completed"
    except Exception as e:
        print(f"Failed to process document {filename} due to error: {e}")
        document_statuses[filename] = "failed"
    finally:
        # Cleanup temp file
        if os.path.exists(file_path):
            os.remove(file_path)

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
        
    document_statuses[file.filename] = "uploading"
    
    # Add the document processing to the background task
    background_tasks.add_task(process_document, temp_file_path, file.filename)
    return {"filename": file.filename, "message": "Upload successful. Processing in background.", "task_id": file.filename}

@app.get("/api/documents/status/{task_id}")
async def get_document_status(task_id: str):
    status = document_statuses.get(task_id, "unknown")
    return {"task_id": task_id, "status": status}

@app.get("/api/documents")
async def list_documents():
    """Retrieve all uniquely uploaded and vectorized document filenames."""
    try:
        documents = vector_db_service.get_all_documents()
        return {"documents": documents}
    except Exception as e:
        print(f"Failed to fetch documents list: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch documents.")

@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    """Search vector DB and formulate an answer using RAG"""
    try:
        # Basic implementation: We will just grab chunks and let OpenAI generate a response here
        docs = vector_db_service.db.similarity_search(request.query, k=5)
        
        if not docs:
            return {"role": "assistant", "content": "I don't have any uploaded documents to pull context from yet. Please upload a PDF first."}

        context = "\n\n".join([doc.page_content for doc in docs])

        from langchain_openai import ChatOpenAI
        from langchain_core.messages import SystemMessage, HumanMessage

        llm = ChatOpenAI(temperature=0.3, model="gpt-3.5-turbo")
        
        system_prompt = (
            "You are an expert architectural and engineering AI assistant named BuildSight RAG. "
            "Use the provided document context to answer the user's question accurately and professionally. "
            "If the answer cannot be found in the context, state that clearly."
        )

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"Context:\n{context}\n\nQuestion: {request.query}")
        ]

        response = llm(messages)
        
        return {"role": "assistant", "content": response.content}
        
    except Exception as e:
        print(e)
        return {"role": "assistant", "content": "I encountered an error trying to process your request."}
