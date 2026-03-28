from fastapi import FastAPI, UploadFile, File, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
import shutil
import time

app = FastAPI(title="BuildSight RAG API", description="API for architectural documents RAG system")

# Define CORS to allow Next.js frontend to communicate
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update this to specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Welcome to BuildSight RAG API"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}

async def process_document(file_path: str, filename: str):
    # This is a stub for the heavy background processing task
    print(f"Starting to process {filename}...")
    # Simulate processing time
    time.sleep(2)  
    print(f"Finished processing {filename}. Vector embeddings created.")

@app.post("/api/documents/upload")
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
        
    try:
        # Ensure uploads dir exists
        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)
        
        file_path = os.path.join(upload_dir, file.filename)
        
        # Save file asynchronously
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Add processing to background tasks
        background_tasks.add_task(process_document, file_path, file.filename)
        
        return {
            "message": "File uploaded successfully. Processing started in the background.",
            "filename": file.filename
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
