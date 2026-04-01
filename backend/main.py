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
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"], 
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

# Simple in-memory storage for chat history by session/user
chat_histories = {}

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    query: str
    session_id: str = "default"  # Optional session ID to track history

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

@app.delete("/api/documents/{filename}")
async def delete_document(filename: str):
    """Delete a document and all its embedded chunks from the Vector DB."""
    success = vector_db_service.delete_document(filename=filename)
    if not success:
        raise HTTPException(status_code=500, detail=f"Failed to delete document {filename}")
    
    # Also clean up status dictionary if needed
    if filename in document_statuses:
        del document_statuses[filename]
        
    return {"message": f"Document {filename} successfully deleted."}

@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    """Search vector DB and formulate an answer using RAG with Conversation History."""
    try:
        session_id = request.session_id
        if session_id not in chat_histories:
            chat_histories[session_id] = []
        history = chat_histories[session_id]

        query_embedding = vector_db_service.embeddings.embed_query(request.query)
        results = vector_db_service.collection.query(
            query_embeddings=[query_embedding],
            n_results=5,
            include=["documents", "metadatas"],
        )

        docs = (results.get("documents") or [[]])[0]
        metas = (results.get("metadatas") or [[]])[0]
        if not docs:
            return {
                "role": "assistant",
                "content": "I don't have any uploaded documents to pull context from yet. Please upload a PDF first.",
            }

        # Build context with lightweight citations
        pairs = []
        for i, doc in enumerate(docs):
            src = None
            if i < len(metas) and metas[i] and isinstance(metas[i], dict):
                src = metas[i].get("source")
            label = f"Source: {src}" if src else "Source: unknown"
            pairs.append(f"[{i+1}] {label}\n{doc}")

        context = "\n\n".join(pairs)
        # Cap context to avoid overly large prompts
        context = context[:12000]

        from langchain_google_genai import ChatGoogleGenerativeAI
        from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

        llm = ChatGoogleGenerativeAI(model="models/gemini-flash-latest", temperature=0.3)
        system_prompt = (
            "You are an expert architectural and engineering AI assistant named BuildSight RAG. "
            "Answer using ONLY the provided context. "
            "When relevant, cite sources using bracket numbers like [1], [2]. "
            "If the answer cannot be found in the context, say so clearly."
        )

        messages = [SystemMessage(content=system_prompt)]
        for msg in history[-4:]:
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                messages.append(AIMessage(content=msg["content"]))

        messages.append(HumanMessage(content=f"Context:\n{context}\n\nQuestion: {request.query}"))
        response = llm.invoke(messages)

        chat_histories[session_id].append({"role": "user", "content": request.query})
        content = getattr(response, "content", str(response))
        chat_histories[session_id].append({"role": "assistant", "content": content})

        return {"role": "assistant", "content": content}
    except Exception as e:
        print(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
