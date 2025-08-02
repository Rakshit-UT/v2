# LLM-Powered Intelligent Query-Retrieval System

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
source venv/bin/activate  # On Windows: venv\Scripts\activate
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
