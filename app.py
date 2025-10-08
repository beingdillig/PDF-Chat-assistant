"""Main FastAPI application for PDF RAG system."""
import os
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uuid
from datetime import datetime

from database import init_db, get_db, Document, ChatMessage
from qdrantservice import QdrantService
from pdfservice import PDFService
from llm import LLMService

app = FastAPI(title="PDF RAG API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
qdrant = QdrantService()
pdf_service = PDFService()
llm_service = LLMService()

# Request/Response models
class QueryRequest(BaseModel):
    query: str
    session_id: str
    top_k: int = 5

class QueryResponse(BaseModel):
    answer: str
    sources: List[dict]
    session_id: str


@app.on_event("startup")
async def startup():
    """Initialize database on startup."""
    init_db()


@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...), session_id: str = "default", db=Depends(get_db)):
    """Upload and process a PDF file."""
    if not file.filename.endswith('.pdf'):
        raise HTTPException(400, "Only PDF files allowed")
    
    # Save file
    os.makedirs("uploads", exist_ok=True)
    file_path = f"uploads/{uuid.uuid4()}_{file.filename}"
    with open(file_path, "wb") as f:
        f.write(await file.read())
    
    try:
        # Process PDF
        chunks = pdf_service.process_pdf(file_path)
        print("chunking done")
        
        # Save to database
        # db = next(get_db())
        # print("step1")
        doc = Document(
            session_id=session_id,
            filename=file.filename,
            filepath=file_path,
            page_count=pdf_service.get_page_count(file_path),
            chunk_count=len(chunks),
            status="completed"
        )

        db.add(doc)
        db.commit()
        db.refresh(doc)

        
        # Store embeddings
        texts = [c["text"] for c in chunks]
        metadata = [{"doc_id": doc.id, "page": c["page"], "filename": file.filename} for c in chunks]
        qdrant.add_documents(texts, metadata)
        
        return {"message": "PDF processed", "doc_id": doc.id, "chunks": len(chunks)}
    
    except Exception as e:
        raise HTTPException(500, f"Processing failed: {str(e)}")


@app.post("/query", response_model=QueryResponse)
async def query(req: QueryRequest, db=Depends(get_db)):
    """Query the RAG system."""
    try:
        # Search vectors
        results = qdrant.search(req.query, req.top_k)
        
        # Generate answer
        answer = llm_service.generate_answer(req.query, results)
        
        # Save to database
        # db = next(get_db())
        msg = ChatMessage(
            session_id=req.session_id,
            role="user",
            content=req.query
        )
        db.add(msg)
        
        msg_response = ChatMessage(
            session_id=req.session_id,
            role="assistant",
            content=answer
        )
        db.add(msg_response)
        db.commit()
        
        sources = [{"filename": r["filename"], "page": r["page"], "text": r["text"][:200]} 
                   for r in results]
        
        return QueryResponse(answer=answer, sources=sources, session_id=req.session_id)
    
    except Exception as e:
        raise HTTPException(500, f"Query failed: {str(e)}")


@app.get("/documents")
async def get_documents(session_id: str = "default", db=Depends(get_db)):
    """Get all documents for a session."""
    # db = next(get_db())
    docs = db.query(Document).filter(Document.session_id == session_id).all()
    return [{"id": d.id, "filename": d.filename, "status": d.status, 
             "page_count": d.page_count, "uploaded_at": d.uploaded_at} for d in docs]


@app.get("/history")
async def get_history(session_id: str = "default", db=Depends(get_db)):
    """Get chat history for a session."""
    # db = next(get_db())
    messages = db.query(ChatMessage).filter(
        ChatMessage.session_id == session_id
    ).order_by(ChatMessage.created_at).all()
    return [{"role": m.role, "content": m.content, "created_at": m.created_at} 
            for m in messages]


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)