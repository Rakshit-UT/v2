# Create a complete FastAPI application with document processing and LLM integration
# This will generate all the necessary files for the Bajaj GenAI Hackathon project

import os
import json

# Create the main FastAPI application
main_py_content = '''import os
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
        context_text = "\\n\\n".join([
            f"Source: {chunk['source']} (Page {chunk['page']})\\n{chunk['text']}"
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
'''

# Create requirements.txt
requirements_content = '''fastapi==0.104.1
uvicorn[standard]==0.24.0
python-multipart==0.0.6
requests==2.31.0
google-generativeai==0.3.2
faiss-cpu==1.7.4
sentence-transformers==2.2.2
PyPDF2==3.0.1
python-docx==1.1.0
numpy==1.24.3
pydantic==2.5.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
'''

# Create HTML interface
html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LLM-Powered Document Query System</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 2.5rem;
            margin-bottom: 10px;
            font-weight: 700;
        }
        
        .header p {
            font-size: 1.1rem;
            opacity: 0.9;
        }
        
        .badge {
            background: rgba(255, 255, 255, 0.2);
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.9rem;
            margin-top: 10px;
            display: inline-block;
        }
        
        .main-content {
            padding: 40px;
        }
        
        .input-section {
            margin-bottom: 30px;
        }
        
        .form-group {
            margin-bottom: 25px;
        }
        
        label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: #374151;
            font-size: 1rem;
        }
        
        .input-field {
            width: 100%;
            padding: 15px;
            border: 2px solid #e5e7eb;
            border-radius: 8px;
            font-size: 1rem;
            transition: all 0.3s ease;
        }
        
        .input-field:focus {
            outline: none;
            border-color: #4f46e5;
            box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1);
        }
        
        .textarea-field {
            min-height: 120px;
            resize: vertical;
            font-family: inherit;
        }
        
        .question-item {
            background: #f9fafb;
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .question-item input {
            flex: 1;
            border: none;
            background: transparent;
            font-size: 1rem;
            padding: 5px;
        }
        
        .question-item input:focus {
            outline: none;
        }
        
        .remove-btn {
            background: #ef4444;
            color: white;
            border: none;
            padding: 8px 12px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 0.9rem;
            transition: background 0.3s ease;
        }
        
        .remove-btn:hover {
            background: #dc2626;
        }
        
        .add-btn {
            background: #10b981;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 1rem;
            margin-bottom: 20px;
            transition: background 0.3s ease;
        }
        
        .add-btn:hover {
            background: #059669;
        }
        
        .submit-btn {
            background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
            color: white;
            border: none;
            padding: 15px 40px;
            border-radius: 8px;
            font-size: 1.1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(79, 70, 229, 0.3);
        }
        
        .submit-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(79, 70, 229, 0.4);
        }
        
        .submit-btn:disabled {
            background: #9ca3af;
            cursor: not-allowed;
            transform: none;
            box-shadow: none;
        }
        
        .loading {
            display: none;
            text-align: center;
            padding: 20px;
        }
        
        .spinner {
            width: 40px;
            height: 40px;
            border: 4px solid #f3f4f6;
            border-top: 4px solid #4f46e5;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 0 auto 15px;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .results {
            margin-top: 30px;
            display: none;
        }
        
        .result-item {
            background: #f8fafc;
            border-left: 4px solid #4f46e5;
            padding: 20px;
            margin-bottom: 20px;
            border-radius: 0 8px 8px 0;
        }
        
        .question {
            font-weight: 600;
            color: #1f2937;
            margin-bottom: 10px;
            font-size: 1.1rem;
        }
        
        .answer {
            color: #4b5563;
            line-height: 1.6;
            font-size: 1rem;
        }
        
        .error {
            background: #fef2f2;
            color: #dc2626;
            padding: 15px;
            border-radius: 8px;
            border: 1px solid #fecaca;
            margin: 20px 0;
        }
        
        .success {
            background: #f0fdf4;
            color: #166534;
            padding: 15px;
            border-radius: 8px;
            border: 1px solid #bbf7d0;
            margin: 20px 0;
        }
        
        .info-box {
            background: #eff6ff;
            border: 1px solid #bfdbfe;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 30px;
        }
        
        .info-box h3 {
            color: #1e40af;
            margin-bottom: 10px;
        }
        
        .info-box p {
            color: #1e3a8a;
            line-height: 1.5;
        }
        
        @media (max-width: 768px) {
            .container {
                margin: 10px;
                border-radius: 10px;
            }
            
            .header {
                padding: 20px;
            }
            
            .header h1 {
                font-size: 2rem;
            }
            
            .main-content {
                padding: 20px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 LLM-Powered Document Query System</h1>
            <p>Intelligent Query-Retrieval System for Document Analysis</p>
            <div class="badge">HackRx 6.0 - Bajaj GenAI Hackathon</div>
        </div>
        
        <div class="main-content">
            <div class="info-box">
                <h3>📋 How it works:</h3>
                <p>
                    1. Enter the URL of a PDF document (insurance policies, contracts, etc.)<br>
                    2. Add your questions about the document content<br>
                    3. Our AI system will analyze the document and provide accurate answers<br>
                    4. Results are returned in JSON format for easy integration
                </p>
            </div>
            
            <form id="queryForm">
                <div class="form-group">
                    <label for="documentUrl">📄 Document URL (PDF):</label>
                    <input 
                        type="url" 
                        id="documentUrl" 
                        class="input-field" 
                        placeholder="https://example.com/document.pdf"
                        required
                    >
                </div>
                
                <div class="form-group">
                    <label>❓ Questions:</label>
                    <div id="questionsContainer">
                        <div class="question-item">
                            <input type="text" placeholder="What is the grace period for premium payment?" required>
                            <button type="button" class="remove-btn" onclick="removeQuestion(this)">Remove</button>
                        </div>
                        <div class="question-item">
                            <input type="text" placeholder="What is the waiting period for pre-existing diseases?" required>
                            <button type="button" class="remove-btn" onclick="removeQuestion(this)">Remove</button>
                        </div>
                    </div>
                    <button type="button" class="add-btn" onclick="addQuestion()">+ Add Question</button>
                </div>
                
                <button type="submit" class="submit-btn" id="submitBtn">
                    🚀 Analyze Document & Get Answers
                </button>
            </form>
            
            <div class="loading" id="loading">
                <div class="spinner"></div>
                <p>Processing document and generating answers...</p>
            </div>
            
            <div class="results" id="results">
                <h2>📊 Results:</h2>
                <div id="resultsContainer"></div>
                
                <h3>💻 JSON Response:</h3>
                <textarea id="jsonOutput" class="input-field textarea-field" readonly></textarea>
            </div>
        </div>
    </div>

    <script>
        // API Configuration
        const API_BASE_URL = 'https://your-deployed-app.herokuapp.com'; // Replace with actual deployed URL
        const LOCAL_API_URL = 'http://localhost:8000';
        
        // Use local URL for development, deployed URL for production
        const API_URL = window.location.hostname === 'localhost' ? LOCAL_API_URL : API_BASE_URL;
        
        function addQuestion() {
            const container = document.getElementById('questionsContainer');
            const questionDiv = document.createElement('div');
            questionDiv.className = 'question-item';
            questionDiv.innerHTML = `
                <input type="text" placeholder="Enter your question here..." required>
                <button type="button" class="remove-btn" onclick="removeQuestion(this)">Remove</button>
            `;
            container.appendChild(questionDiv);
        }
        
        function removeQuestion(button) {
            const container = document.getElementById('questionsContainer');
            if (container.children.length > 1) {
                button.parentElement.remove();
            } else {
                alert('At least one question is required.');
            }
        }
        
        function showLoading() {
            document.getElementById('loading').style.display = 'block';
            document.getElementById('results').style.display = 'none';
            document.getElementById('submitBtn').disabled = true;
        }
        
        function hideLoading() {
            document.getElementById('loading').style.display = 'none';
            document.getElementById('submitBtn').disabled = false;
        }
        
        function showError(message) {
            const resultsContainer = document.getElementById('resultsContainer');
            resultsContainer.innerHTML = `<div class="error">❌ Error: ${message}</div>`;
            document.getElementById('results').style.display = 'block';
        }
        
        function displayResults(data) {
            const resultsContainer = document.getElementById('resultsContainer');
            const jsonOutput = document.getElementById('jsonOutput');
            
            // Display formatted results
            let resultsHTML = '';
            const questions = getQuestions();
            
            data.answers.forEach((answer, index) => {
                resultsHTML += `
                    <div class="result-item">
                        <div class="question">Q${index + 1}: ${questions[index]}</div>
                        <div class="answer">${answer}</div>
                    </div>
                `;
            });
            
            resultsContainer.innerHTML = resultsHTML;
            
            // Display JSON output
            jsonOutput.value = JSON.stringify(data, null, 2);
            
            document.getElementById('results').style.display = 'block';
        }
        
        function getQuestions() {
            const questionInputs = document.querySelectorAll('#questionsContainer input');
            return Array.from(questionInputs).map(input => input.value.trim()).filter(q => q);
        }
        
        async function submitQuery(documentUrl, questions) {
            const requestData = {
                documents: documentUrl,
                questions: questions
            };
            
            try {
                const response = await fetch(`${API_URL}/hackrx/run`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Accept': 'application/json'
                    },
                    body: JSON.stringify(requestData)
                });
                
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                
                const data = await response.json();
                return data;
                
            } catch (error) {
                console.error('API Error:', error);
                throw error;
            }
        }
        
        // Form submission handler
        document.getElementById('queryForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const documentUrl = document.getElementById('documentUrl').value.trim();
            const questions = getQuestions();
            
            if (!documentUrl) {
                alert('Please enter a document URL.');
                return;
            }
            
            if (questions.length === 0) {
                alert('Please add at least one question.');
                return;
            }
            
            showLoading();
            
            try {
                const result = await submitQuery(documentUrl, questions);
                displayResults(result);
                
                // Show success message
                const successDiv = document.createElement('div');
                successDiv.className = 'success';
                successDiv.innerHTML = '✅ Document processed successfully! Results are displayed below.';
                document.getElementById('results').insertBefore(successDiv, document.getElementById('results').firstChild);
                
            } catch (error) {
                showError(error.message || 'Failed to process request. Please check your inputs and try again.');
            } finally {
                hideLoading();
            }
        });
        
        // Sample data button (for demo purposes)
        function loadSampleData() {
            document.getElementById('documentUrl').value = 'https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D';
            
            const container = document.getElementById('questionsContainer');
            container.innerHTML = `
                <div class="question-item">
                    <input type="text" value="What is the grace period for premium payment under the National Parivar Mediclaim Plus Policy?" required>
                    <button type="button" class="remove-btn" onclick="removeQuestion(this)">Remove</button>
                </div>
                <div class="question-item">
                    <input type="text" value="What is the waiting period for pre-existing diseases (PED) to be covered?" required>
                    <button type="button" class="remove-btn" onclick="removeQuestion(this)">Remove</button>
                </div>
                <div class="question-item">
                    <input type="text" value="Does this policy cover maternity expenses, and what are the conditions?" required>
                    <button type="button" class="remove-btn" onclick="removeQuestion(this)">Remove</button>
                </div>
            `;
        }
        
        // Add sample data button
        window.addEventListener('load', function() {
            const sampleBtn = document.createElement('button');
            sampleBtn.type = 'button';
            sampleBtn.className = 'add-btn';
            sampleBtn.innerHTML = '📝 Load Sample Data';
            sampleBtn.onclick = loadSampleData;
            sampleBtn.style.marginRight = '10px';
            
            const submitBtn = document.getElementById('submitBtn');
            submitBtn.parentNode.insertBefore(sampleBtn, submitBtn);
        });
        
        // Health check on page load
        window.addEventListener('load', async function() {
            try {
                const response = await fetch(`${API_URL}/health`);
                if (response.ok) {
                    console.log('✅ API is healthy');
                } else {
                    console.warn('⚠️ API health check failed');
                }
            } catch (error) {
                console.warn('⚠️ Could not connect to API:', error.message);
            }
        });
    </script>
</body>
</html>'''

# Create Dockerfile
dockerfile_content = '''FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    g++ \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
'''

# Create deployment configuration
railway_json = '''{
    "build": {
        "builder": "DOCKERFILE"
    },
    "deploy": {
        "startCommand": "uvicorn main:app --host 0.0.0.0 --port $PORT",
        "healthcheckPath": "/health",
        "healthcheckTimeout": 300
    }
}'''

# Create .gitignore
gitignore_content = '''# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Virtual environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Logs
*.log

# Temporary files
*.tmp
*.temp
temp/
tmp/
'''

# Create README
readme_content = '''# LLM-Powered Intelligent Query-Retrieval System

## HackRx 6.0 - Bajaj GenAI Hackathon Submission

This is an intelligent document query system that processes large PDF documents and answers questions using advanced LLM techniques.

### Features

- **Document Processing**: Extracts text from PDF documents via URL
- **Semantic Search**: Uses FAISS for efficient vector-based document retrieval  
- **LLM Integration**: Powered by Google Gemini for intelligent question answering
- **RESTful API**: FastAPI backend with JSON input/output
- **Web Interface**: Clean HTML interface for easy testing
- **Production Ready**: Dockerized and deployable to various platforms

### Architecture

1. **Document Ingestion**: Downloads and processes PDF documents
2. **Text Chunking**: Splits documents into semantic chunks with overlap
3. **Vector Indexing**: Creates FAISS index using sentence transformers
4. **Semantic Retrieval**: Finds relevant chunks for each query
5. **Answer Generation**: Uses Google Gemini to generate contextual answers
6. **JSON Response**: Returns structured answers in the required format

### Tech Stack

- **Backend**: FastAPI, Python 3.9+
- **LLM**: Google Gemini 1.5 Flash
- **Vector DB**: FAISS (Facebook AI Similarity Search)
- **Embeddings**: SentenceTransformers (all-MiniLM-L6-v2)
- **PDF Processing**: PyPDF2
- **Deployment**: Docker, Railway/Render/Heroku compatible

### API Endpoints

#### POST /hackrx/run
Main hackathon endpoint that processes documents and answers questions.

**Request:**
```json
{
  "documents": "https://example.com/policy.pdf",
  "questions": [
    "What is the grace period for premium payment?",
    "What is the waiting period for pre-existing diseases?"
  ]
}
```

**Response:**
```json
{
  "answers": [
    "A grace period of thirty days is provided for premium payment...",
    "There is a waiting period of thirty-six (36) months..."
  ]
}
```

#### GET /health
Health check endpoint for monitoring.

#### GET /documents/chunks
View indexed document chunks (for debugging).

#### POST /search
Direct search interface for querying indexed documents.

### Local Development

1. **Clone and setup:**
```bash
git clone <repository-url>
cd hackrx-rag-system
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate
pip install -r requirements.txt
```

2. **Run the application:**
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

3. **Access the application:**
- API: http://localhost:8000
- Web Interface: Open `index.html` in a browser
- API Docs: http://localhost:8000/docs

### Deployment

#### Docker
```bash
docker build -t hackrx-rag-system .
docker run -p 8000:8000 hackrx-rag-system
```

#### Railway
1. Connect your GitHub repository to Railway
2. Railway will automatically detect and deploy the FastAPI app
3. Environment variables are configured automatically

#### Render/Heroku
1. Connect repository to platform
2. Set build command: `pip install -r requirements.txt`
3. Set start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### Configuration

- **Google Gemini API Key**: `AIzaSyBwqeD-FzyCxAhlJLms4FqiZ1fl2AZiBfk`
- **Team Token**: `c0df38f44acb385ecd42f8e0c02ee14acd6d145835643ee57acd84f79afeb798`

### Sample Usage

Test with the provided sample policy document:
```
Document URL: https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D

Sample Questions:
1. What is the grace period for premium payment under the National Parivar Mediclaim Plus Policy?
2. What is the waiting period for pre-existing diseases (PED) to be covered?
3. Does this policy cover maternity expenses, and what are the conditions?
```

### Features Implemented

✅ PDF document processing from URLs  
✅ Text chunking with semantic overlap  
✅ FAISS vector indexing for semantic search  
✅ Google Gemini LLM integration  
✅ RESTful API with JSON I/O  
✅ Comprehensive error handling  
✅ Web interface for testing  
✅ Docker containerization  
✅ Production deployment ready  
✅ Health monitoring endpoints  

### Team Information

- **Hackathon**: HackRx 6.0 - Bajaj GenAI Challenge
- **Team Token**: c0df38f44acb385ecd42f8e0c02ee14acd6d145835643ee57acd84f79afeb798
- **Submission**: LLM-Powered Intelligent Query-Retrieval System

This system is designed to handle real-world scenarios in insurance, legal, HR, and compliance domains by providing accurate, contextual answers from large document corpora.
'''

# Write all files
files_to_create = {
    'main.py': main_py_content,
    'requirements.txt': requirements_content,
    'index.html': html_content,
    'Dockerfile': dockerfile_content,
    'railway.json': railway_json,
    '.gitignore': gitignore_content,
    'README.md': readme_content
}

print("Creating HackRx 6.0 - Bajaj GenAI Hackathon Project Files...")
print("=" * 60)

for filename, content in files_to_create.items():
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ Created: {filename}")

print("\n" + "=" * 60)
print("🎉 Project files created successfully!")
print("\nNext steps:")
print("1. Initialize git repository: git init")
print("2. Add files: git add .")
print("3. Commit: git commit -m 'Initial commit - HackRx 6.0 submission'")
print("4. Create GitHub repository and push code")
print("5. Deploy to Railway/Render/Heroku")
print("6. Update API_BASE_URL in index.html with deployed URL")
print("\nFor local testing:")
print("pip install -r requirements.txt")
print("uvicorn main:app --reload")