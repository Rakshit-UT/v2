
from fastapi import FastAPI, HTTPException, Depends, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import requests
import PyPDF2
import io
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import google.generativeai as genai
import os
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="HackRx 6.0 LLM Query Retrieval System",
    description="Intelligent document query system using LLM and vector embeddings",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure Google Gemini API
GEMINI_API_KEY = "AIzaSyBwqeD-FzyCxAhlJLms4FqiZ1fl2AZiBfk"
genai.configure(api_key=GEMINI_API_KEY)

# Initialize models
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
gemini_model = genai.GenerativeModel('gemini-pro')

# Pydantic models for request/response
class QueryRequest(BaseModel):
    documents: str  # URL to PDF document
    questions: List[str]

class QueryResponse(BaseModel):
    answers: List[str]

# Global variables for document storage and indexing
document_chunks = []
faiss_index = None
chunk_embeddings = []

class DocumentProcessor:
    def __init__(self):
        self.embedding_model = embedding_model

    def extract_text_from_pdf_url(self, pdf_url: str) -> str:
        """Extract text from PDF URL"""
        try:
            response = requests.get(pdf_url)
            response.raise_for_status()

            pdf_file = io.BytesIO(response.content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)

            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"

            return text
        except Exception as e:
            logger.error(f"Error extracting PDF: {e}")
            raise HTTPException(status_code=400, detail=f"Failed to extract PDF: {str(e)}")

    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Split text into overlapping chunks"""
        chunks = []
        start = 0

        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            chunks.append(chunk)
            start = end - overlap

        return chunks

    def create_embeddings(self, chunks: List[str]) -> np.ndarray:
        """Create embeddings for text chunks"""
        embeddings = self.embedding_model.encode(chunks)
        return embeddings

    def build_faiss_index(self, embeddings: np.ndarray) -> faiss.Index:
        """Build FAISS index for similarity search"""
        dimension = embeddings.shape[1]
        index = faiss.IndexFlatL2(dimension)
        index.add(embeddings.astype(np.float32))
        return index

class QueryProcessor:
    def __init__(self):
        self.gemini_model = gemini_model

    def find_relevant_chunks(self, query: str, index: faiss.Index, chunks: List[str], k: int = 5) -> List[str]:
        """Find most relevant chunks using FAISS"""
        query_embedding = embedding_model.encode([query])

        distances, indices = index.search(query_embedding.astype(np.float32), k)

        relevant_chunks = [chunks[i] for i in indices[0]]
        return relevant_chunks

    def generate_answer(self, query: str, context_chunks: List[str]) -> str:
        """Generate answer using Gemini LLM"""
        context = "\n\n".join(context_chunks)

        prompt = f"""
        Based on the following context from a document, please answer the question accurately and concisely.

        Context:
        {context}

        Question: {query}

        Answer: Provide a clear and specific answer based only on the information in the context. If the information is not available in the context, state that clearly.
        """

        try:
            response = self.gemini_model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Error generating answer: {e}")
            return f"Error generating answer: {str(e)}"

# Initialize processors
doc_processor = DocumentProcessor()
query_processor = QueryProcessor()

@app.post("/hackrx/run", response_model=QueryResponse)
async def process_queries(request: QueryRequest):
    """Main endpoint for processing document queries"""
    global document_chunks, faiss_index, chunk_embeddings

    try:
        # Extract text from PDF
        logger.info(f"Processing PDF from URL: {request.documents}")
        document_text = doc_processor.extract_text_from_pdf_url(request.documents)

        # Chunk the document
        document_chunks = doc_processor.chunk_text(document_text)
        logger.info(f"Created {len(document_chunks)} chunks")

        # Create embeddings
        chunk_embeddings = doc_processor.create_embeddings(document_chunks)

        # Build FAISS index
        faiss_index = doc_processor.build_faiss_index(chunk_embeddings)

        # Process each question
        answers = []
        for question in request.questions:
            logger.info(f"Processing question: {question}")

            # Find relevant chunks
            relevant_chunks = query_processor.find_relevant_chunks(
                question, faiss_index, document_chunks
            )

            # Generate answer
            answer = query_processor.generate_answer(question, relevant_chunks)
            answers.append(answer)

        return QueryResponse(answers=answers)

    except Exception as e:
        logger.error(f"Error processing request: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "HackRx 6.0 LLM Query Retrieval System",
        "version": "1.0.0",
        "endpoints": {
            "main": "/hackrx/run",
            "health": "/health"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
