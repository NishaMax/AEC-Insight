# AEC-Insight

<p align="center">
  <a href="http://13.206.83.220/" target="_blank" rel="noopener noreferrer">
    <strong>Live Demo — http://13.206.83.220/</strong>
  </a>
</p>

AEC-Insight repository for "BuildSight RAG".

## Overview

BuildSight RAG is a full-stack Retrieval-Augmented Generation (RAG) system. The goal is to allow users to upload dense, complex architectural documents (like building codes, MEP manuals, or zoning laws in PDF format) and chat with an AI to extract specific technical information.

## Tech Stack

- **Backend:** Python, FastAPI (Strictly async/await).
- **AI/ML Frameworks:** LangChain, OpenAI API.
- **Vector Database:** ChromaDB (Local).
- **Frontend:** Next.js (App Router), React, Tailwind CSS.

## Architecture

1.  **Document Ingestion:** Next.js frontend for PDF upload, received asynchronously by FastAPI.
2.  **Processing:** PyMuPDF/pdfplumber for text extraction, chunked via LangChain `RecursiveCharacterTextSplitter`.
3.  **Embedding:** Text chunks -> Vector embeddings (`text-embedding-3-small`) -> ChromaDB.
4.  **Querying:** User question -> Embedding -> Top 5 relevant chunks retrieved from DB to construct prompt.
5.  **Generation:** LLM generates a response based on architectural context, streamed to the frontend.

## Workflow Strategy

- **`main` Branch:** Production-ready code.
- **`develop` Branch:** Integration branch. Features merge here before going to main.
- **`feature/*` Branches:** Create for everyday tasks (e.g., `feature/backend-setup`), merge into `develop` when stable.

## Plan

### Phase 1: Project Setup & Foundation

- Setup Next.js Frontend.
- Setup FastAPI Backend.
- Configure Docker (optional but recommended for consistency).

### Phase 2: Document Ingestion Pipeline

- Frontend: PDF Upload UI.
- Backend: File receiving endpoint (async).
- Processing: Text extraction and chunking.
- Embedding: Store into ChromaDB using background tasks.

### Phase 3: Querying and RAG Pipeline

- Backend: Query endpoint, similarity search in ChromaDB.
- LLM Integration: Prompt construction and generating streamed responses.
- Frontend: Engineering-tailored chat interface (ChatGPT style).

### Phase 4: CI/CD & Deployment

- GitHub Actions for Linting/Testing.
- Deployment setup (Vercel for Frontend, Render/Koyeb for Backend).
