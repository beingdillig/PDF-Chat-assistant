# PDF RAG Application

A simple Retrieval-Augmented Generation (RAG) system for querying PDF documents using Qdrant, PostgreSQL, and Gemini.

## Features

- Upload and process PDF files
- Vector search using Qdrant
- Chat interface with Streamlit
- Store chat history in PostgreSQL
- Source citations for all answers

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Create a `.env` file:

```bash
GEMINI_API_KEY="AIxxxxxxxxxxxxxxxxxxxxxxxx"
QDRANT_URL="https://qdrant.io"
QDRANT_API_KEY="eyJxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx.gxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxA"
QDRANT_COLLECTION="pdf_docs"
TOP_K=5
```

### 3. Run API Server

```bash
uvicorn app:app --reload
```

API will run on http://localhost:8000

### 4. Run Streamlit UI

```bash
streamlit run stapp.py
```

UI will open at http://localhost:8501

## Usage

1. Upload PDF files using the sidebar
2. Wait for processing to complete
3. Ask questions in the chat interface
4. View source citations by expanding the sources section

## Architecture

- **FastAPI**: REST API for PDF processing and queries
- **Qdrant**: Vector database for embeddings
- **PostgreSQL**: Relational database for metadata and history
- **Sentence Transformers**: Generate embeddings
- **Gemini**: Generate answers from retrieved context
- **Streamlit**: User interface

## Project Structure

```
.
├── app.py                 # FastAPI application
├── stapp.py               # Streamlit UI
├── database.py            # PostgreSQL models
├── qdrantservice.py       # Vector database service
├── pdfservice.py          # PDF processing
├── llm.py                 # Gemini integration
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## API Endpoints

- `POST /upload` - Upload and process PDF
- `POST /query` - Query the RAG system
- `GET /documents` - List all documents
- `GET /history` - Get chat history

## Notes

- Uses `pypdf` for PDF parsing (simple and reliable)
- Embeddings: `all-MiniLM-L6-v2` (384 dimensions)
- Chunk size: 500 characters with 50 character overlap
- Default top_k: 5 results
