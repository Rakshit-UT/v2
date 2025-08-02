import os
import asyncio
import logging
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Depends, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import requests
import tempfile
import shutil
from urllib.parse import urlparse
import google.generativeai as genai
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import PyPDF2
import docx
import email
from email import policy
from email.parser import BytesParser
import re
import json
from datetime import datetime
import hashlib

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="LLM-Powered Intelligent Query-Retrieval System",
    description="HackRx 6.0 - Bajaj GenAI Hackathon Submission",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
GOOGLE_API_KEY = "AIzaSyBwqeD-FzyCxAhlJLms4FqiZ1fl2AZiBfk"
TEAM_TOKEN = "c0df38f44acb385ecd42f8e0c02ee14acd6d145835643ee57acd84f79afeb798"

# Initialize Google Gemini
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# Initialize embedding model
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

# Global variables for vector storage
vector_index = None
document_chunks = []
chunk_metadata = []

class QueryRequest(BaseModel):
    documents: str = Field(..., description="URL to the PDF document")
    questions: List[str] = Field(..., description="List of questions to answer")

class AnswerResponse(BaseModel):
    answers: List[str] = Field(..., description="List of answers to the questions")

class DocumentChunk:
    def __init__(self, text: str, source: str, page: int = None, chunk_id: str = None):
        self.text = text
        self.source = source
        self.page = page
        self.chunk_id = chunk_id or hashlib.md5(text.encode()).hexdigest()[:8]

def extract_text_from_pdf_url(url: str) -> List[DocumentChunk]:
    """Extract text from PDF URL"""
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        chunks = []
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            temp_file.write(response.content)
            temp_file.flush()

            with open(temp_file.name, 'rb') as pdf_file:
                pdf_reader = PyPDF2.PdfReader(pdf_file)

                for page_num, page in enumerate(pdf_reader.pages):
                    text = page.extract_text()
                    if text.strip():
                        # Split text into smaller chunks
                        text_chunks = split_text_into_chunks(text, max_chunk_size=500)
                        for i, chunk in enumerate(text_chunks):
                            chunks.append(DocumentChunk(
                                text=chunk,
                                source=url,
                                page=page_num + 1,
                                chunk_id=f"page_{page_num+1}_chunk_{i+1}"
                            ))

        os.unlink(temp_file.name)
        return chunks

    except Exception as e:
        logger.error(f"Error extracting text from PDF: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Error processing PDF: {str(e)}")

def split_text_into_chunks(text: str, max_chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """Split text into overlapping chunks"""
    sentences = re.split(r'[.!?]+', text)
    chunks = []
    current_chunk = ""

    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue

        if len(current_chunk) + len(sentence) < max_chunk_size:
            current_chunk += sentence + ". "
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = sentence + ". "

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks

def create_vector_index(chunks: List[DocumentChunk]):
    """Create FAISS vector index from document chunks"""
    global vector_index, document_chunks, chunk_metadata

    if not chunks:
        raise ValueError("No chunks provided for indexing")

    # Extract text for embedding
    texts = [chunk.text for chunk in chunks]

    # Generate embeddings
    embeddings = embedding_model.encode(texts)
    embeddings = np.array(embeddings).astype('float32')

    # Create FAISS index
    dimension = embeddings.shape[1]
    vector_index = faiss.IndexFlatL2(dimension)
    vector_index.add(embeddings)

    # Store chunks and metadata
    document_chunks = chunks
    chunk_metadata = [
        {
            "chunk_id": chunk.chunk_id,
            "source": chunk.source,
            "page": chunk.page,
            "text": chunk.text[:200] + "..." if len(chunk.text) > 200 else chunk.text
        }
        for chunk in chunks
    ]

    logger.info(f"Created vector index with {len(chunks)} chunks")

def semantic_search(query: str, k: int = 5) -> List[Dict[str, Any]]:
    """Perform semantic search using FAISS"""
    global vector_index, document_chunks

    if vector_index is None or not document_chunks:
        return []

    # Encode query
    query_embedding = embedding_model.encode([query])
    query_embedding = np.array(query_embedding).astype('float32')

    # Search
    distances, indices = vector_index.search(query_embedding, k)

    results = []
    for i, idx in enumerate(indices[0]):
        if idx < len(document_chunks):
            chunk = document_chunks[idx]
            results.append({
                "chunk_id": chunk.chunk_id,
                "text": chunk.text,
                "source": chunk.source,
                "page": chunk.page,
                "similarity_score": float(distances[0][i])
            })

    return results

def generate_answer_with_context(question: str, context_chunks: List[Dict[str, Any]]) -> str:
    """Generate answer using Google Gemini with retrieved context"""
    try:
        # Prepare context
        context_text = "\n\n".join([
            f"Source: {chunk['source']} (Page {chunk['page']})\n{chunk['text']}"
            for chunk in context_chunks[:3]  # Use top 3 chunks
        ])

        # Create prompt
        prompt = f"""You are an expert document analyst. Based on the following context from insurance policy documents, answer the question accurately and concisely.

Context:
{context_text}

Question: {question}

Instructions:
1. Answer based only on the provided context
2. Be specific and factual
3. If the context doesn't contain enough information, state that clearly
4. Cite relevant sections when possible
5. Keep the answer concise but complete

Answer:"""

        # Generate response using Gemini
        response = model.generate_content(prompt)
        return response.text.strip()

    except Exception as e:
        logger.error(f"Error generating answer: {str(e)}")
        return f"Error generating answer: {str(e)}"

@app.get("/")
async def root():
    return {
        "message": "LLM-Powered Intelligent Query-Retrieval System",
        "version": "1.0.0",
        "hackathon": "HackRx 6.0 - Bajaj GenAI",
        "status": "active"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "vector_index_ready": vector_index is not None,
        "documents_indexed": len(document_chunks)
    }

@app.post("/hackrx/run", response_model=AnswerResponse)
async def process_hackrx_query(request: QueryRequest):
    """
    Main endpoint for HackRx 6.0 hackathon submission
    Processes documents and answers questions using LLM-powered retrieval
    """
    try:
        logger.info(f"Processing request with {len(request.questions)} questions")

        # Extract text from PDF
        logger.info("Extracting text from PDF...")
        chunks = extract_text_from_pdf_url(request.documents)

        if not chunks:
            raise HTTPException(status_code=400, detail="No text extracted from document")

        # Create vector index
        logger.info("Creating vector index...")
        create_vector_index(chunks)

        # Process each question
        answers = []
        for question in request.questions:
            logger.info(f"Processing question: {question[:50]}...")

            # Retrieve relevant chunks
            relevant_chunks = semantic_search(question, k=5)

            # Generate answer
            answer = generate_answer_with_context(question, relevant_chunks)
            answers.append(answer)

        logger.info(f"Successfully processed {len(answers)} questions")
        return AnswerResponse(answers=answers)

    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/documents/chunks")
async def get_document_chunks():
    """Get information about indexed document chunks"""
    return {
        "total_chunks": len(document_chunks),
        "metadata": chunk_metadata[:10],  # Return first 10 for preview
        "index_ready": vector_index is not None
    }

@app.post("/search")
async def search_documents(query: str, k: int = 5):
    """Search through indexed documents"""
    if not vector_index:
        raise HTTPException(status_code=400, detail="No documents indexed")

    results = semantic_search(query, k)
    return {
        "query": query,
        "results": results,
        "total_found": len(results)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
