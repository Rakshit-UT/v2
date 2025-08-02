
# HackRx 6.0 - LLM-Powered Document Query System 🚀

An intelligent document query-retrieval system built for the Bajaj Finserv HackRx 6.0 hackathon. This system uses Large Language Models (LLM) to process natural language queries and retrieve relevant information from large unstructured documents.

## 🎯 Features

- **PDF Document Processing**: Extract and process text from PDF URLs
- **Semantic Search**: FAISS-powered vector similarity search
- **LLM Integration**: Google Gemini API for intelligent query answering
- **RESTful API**: FastAPI-based backend with automatic documentation
- **Web Interface**: Clean, responsive HTML interface
- **JSON Response Format**: Structured output for easy integration

## 🏗️ System Architecture

```
Input Documents (PDF) → Text Extraction → Chunking → Embedding Generation
                                                              ↓
Query Processing ← FAISS Index ← Vector Storage ← Embeddings
        ↓
    LLM Analysis (Gemini) → Structured JSON Response
```

## 🛠️ Tech Stack

- **Backend**: FastAPI, Python 3.11+
- **LLM**: Google Gemini Pro API
- **Vector Search**: FAISS (Facebook AI Similarity Search)
- **Embeddings**: Sentence Transformers
- **Document Processing**: PyPDF2
- **Frontend**: HTML, CSS, JavaScript

## 📋 Prerequisites

- Python 3.11 or higher
- Google Gemini API key
- Internet connection for document processing

## 🚀 Quick Start

### Local Development

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd hackrx-6.0-solution
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python main.py
   ```

   Or with uvicorn:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

4. **Access the application**
   - Web Interface: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

### Docker Deployment

1. **Build Docker image**
   ```bash
   docker build -t hackrx-solution .
   ```

2. **Run container**
   ```bash
   docker run -p 8000:8000 hackrx-solution
   ```

## 📡 API Endpoints

### POST `/hackrx/run`

Process document queries and return structured answers.

**Request Body:**
```json
{
  "documents": "https://example.com/document.pdf",
  "questions": [
    "What is the grace period for premium payment?",
    "What is the waiting period for pre-existing diseases?",
    "Does this policy cover maternity expenses?"
  ]
}
```

**Response:**
```json
{
  "answers": [
    "A grace period of thirty days is provided for premium payment...",
    "There is a waiting period of thirty-six (36) months...",
    "Yes, the policy covers maternity expenses..."
  ]
}
```

**Headers:**
```
Content-Type: application/json
Authorization: Bearer c0df38f44acb385ecd42f8e0c02ee14acd6d145835643ee57acd84f79afeb798
```

### GET `/health`
Health check endpoint

### GET `/`
Root endpoint with API information

## 🔧 Configuration

The application uses the following configuration:

- **Gemini API Key**: `AIzaSyBwqeD-FzyCxAhlJLms4FqiZ1fl2AZiBfk`
- **Authorization Token**: `c0df38f44acb385ecd42f8e0c02ee14acd6d145835643ee57acd84f79afeb798`
- **Embedding Model**: `all-MiniLM-L6-v2`
- **Chunk Size**: 1000 characters
- **Chunk Overlap**: 200 characters

## 🎮 Usage Examples

### Using the Web Interface

1. Open http://localhost:8000 in your browser
2. Enter a PDF URL in the document field
3. Add your questions (one per line)
4. Click "Process Queries"
5. View results and copy JSON output

### Using cURL

```bash
curl -X POST "http://localhost:8000/hackrx/run" \
-H "Content-Type: application/json" \
-H "Authorization: Bearer c0df38f44acb385ecd42f8e0c02ee14acd6d145835643ee57acd84f79afeb798" \
-d '{
  "documents": "https://hackrx.blob.core.windows.net/assets/policy.pdf",
  "questions": [
    "What is the grace period for premium payment?",
    "What is the waiting period for pre-existing diseases?"
  ]
}'
```

### Using Python Requests

```python
import requests
import json

url = "http://localhost:8000/hackrx/run"
headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer c0df38f44acb385ecd42f8e0c02ee14acd6d145835643ee57acd84f79afeb798"
}

data = {
    "documents": "https://example.com/document.pdf",
    "questions": [
        "What is the grace period for premium payment?",
        "What is the waiting period for pre-existing diseases?"
    ]
}

response = requests.post(url, headers=headers, json=data)
result = response.json()
print(json.dumps(result, indent=2))
```

## 🏃‍♂️ Performance Optimization

- **Chunking Strategy**: Optimized chunk size and overlap for better context retention
- **Vector Indexing**: FAISS IndexFlatL2 for efficient similarity search
- **Caching**: Document embeddings cached during processing
- **Async Processing**: FastAPI async endpoints for better performance

## 🔐 Security Features

- **API Authentication**: Bearer token authentication
- **Input Validation**: Pydantic models for request validation
- **Error Handling**: Comprehensive error handling and logging
- **CORS Configuration**: Configurable CORS settings

## 🧪 Testing

### Manual Testing
Use the provided web interface or API documentation at `/docs`

### Sample Test Cases
The system has been tested with:
- Insurance policy documents
- Legal contracts
- HR handbooks
- Compliance documents

## 📊 System Limitations

- **Document Size**: Large PDFs may take longer to process
- **API Rate Limits**: Subject to Google Gemini API rate limits
- **Language Support**: Optimized for English documents
- **PDF Format**: Works best with text-based PDFs

## 🚀 Deployment Options

### GitHub Pages (Static Frontend)
For deploying just the frontend:
1. Push code to GitHub repository
2. Enable GitHub Pages in repository settings
3. Update API base URL in HTML file

### Cloud Platforms
- **Heroku**: Use provided Dockerfile
- **Google Cloud Run**: Container-ready
- **AWS ECS**: Docker deployment
- **Azure Container Instances**: Direct deployment

### Environment Variables
For production deployment, set:
```
GEMINI_API_KEY=your_api_key_here
AUTH_TOKEN=your_auth_token_here
```

## 🎯 HackRx 6.0 Compliance

This solution addresses all key requirements:

✅ **LLM Integration**: Google Gemini Pro API  
✅ **Document Processing**: PDF text extraction  
✅ **Vector Search**: FAISS implementation  
✅ **Semantic Retrieval**: Sentence transformers  
✅ **JSON Output**: Structured API responses  
✅ **Real-world Applications**: Insurance, legal, HR domains  
✅ **Scalable Architecture**: FastAPI + Docker  
✅ **Authentication**: Bearer token system  

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 License

This project is created for the HackRx 6.0 hackathon by Bajaj Finserv.

## 📞 Support

For technical support or questions:
- Check the API documentation at `/docs`
- Review the error logs in the application
- Ensure all dependencies are properly installed

---

**Built with ❤️ for HackRx 6.0 - Bajaj Finserv Health Limited**
