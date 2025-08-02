from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import requests, io, logging
import PyPDF2
import numpy as np

# Attempt to import FAISS
try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False

from sentence_transformers import SentenceTransformer
import google.generativeai as genai
from sklearn.metrics.pairwise import cosine_similarity
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="HackRx 6.0 LLM Query Retrieval System",
    description="Intelligent document query system using LLM and vector embeddings",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure Google Gemini
genai.configure(api_key="AIzaSyBwqeD-FzyCxAhlJLms4FqiZ1fl2AZiBfk")
gemini_model = genai.GenerativeModel("gemini-pro")
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

class QueryRequest(BaseModel):
    documents: str
    questions: List[str]

class QueryResponse(BaseModel):
    answers: List[str]

class DocumentProcessor:
    def extract_text_from_pdf_url(self, pdf_url: str) -> str:
        try:
            resp = requests.get(pdf_url)
            resp.raise_for_status()
            reader = PyPDF2.PdfReader(io.BytesIO(resp.content))
            text = "".join(page.extract_text() + "\n" for page in reader.pages)
            return text
        except Exception as e:
            logger.error(f"PDF extraction error: {e}")
            raise HTTPException(status_code=400, detail=str(e))

    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        chunks, start = [], 0
        while start < len(text):
            end = start + chunk_size
            chunks.append(text[start:end])
            start = end - overlap
        return chunks

    def create_embeddings(self, chunks: List[str]) -> np.ndarray:
        return embedding_model.encode(chunks)

    def build_index(self, embeddings: np.ndarray):
        if FAISS_AVAILABLE:
            dim = embeddings.shape[1]
            idx = faiss.IndexFlatL2(dim)
            idx.add(embeddings.astype(np.float32))
            return idx
        else:
            return embeddings  # fallback store raw embeddings

class QueryProcessor:
    def find_relevant_chunks(self, query: str, index, chunks: List[str], k: int = 5) -> List[str]:
        q_emb = embedding_model.encode([query])
        if FAISS_AVAILABLE and hasattr(index, "search"):
            dists, ids = index.search(q_emb.astype(np.float32), k)
            return [chunks[i] for i in ids[0]]
        else:
            sims = cosine_similarity(q_emb, index)[0]
            top = np.argsort(sims)[-k:][::-1]
            return [chunks[i] for i in top]

    def generate_answer(self, query: str, context: List[str]) -> str:
        prompt = (
            "Based on the context below, answer the question. If unavailable, say so.\n\n"
            f"Context:\n\n{chr(10).join(context)}\n\nQuestion: {query}\nAnswer:"
        )
        try:
            res = gemini_model.generate_content(prompt)
            return res.text
        except Exception as e:
            logger.error(f"LLM error: {e}")
            return f"Error generating answer: {e}"

doc_proc = DocumentProcessor()
qry_proc = QueryProcessor()

@app.post("/hackrx/run", response_model=QueryResponse)
async def process_queries(req: QueryRequest):
    try:
        text = doc_proc.extract_text_from_pdf_url(req.documents)
        chunks = doc_proc.chunk_text(text)
        embs = doc_proc.create_embeddings(chunks)
        index = doc_proc.build_index(embs)
        answers = []
        for q in req.questions:
            ctx = qry_proc.find_relevant_chunks(q, index, chunks)
            answers.append(qry_proc.generate_answer(q, ctx))
        return QueryResponse(answers=answers)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Processing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/")
async def root():
    return {
        "message": "HackRx 6.0 LLM Query Retrieval System",
        "version": "1.0.0",
        "endpoints": {"main": "/hackrx/run", "health": "/health"}
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
