# HackRx 6.0 - Bajaj GenAI Hackathon Deployment Guide

## Complete LLM-Powered Intelligent Query-Retrieval System

This deployment guide provides step-by-step instructions for deploying your HackRx 6.0 submission to various platforms.

## Quick Start (Local Testing)

1. **Clone/Create Project Directory:**
```bash
mkdir hackrx-bajaj-genai
cd hackrx-bajaj-genai
```

2. **Save all provided files** (main.py, requirements.txt, index.html, etc.)

3. **Install Dependencies:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

4. **Run Locally:**
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

5. **Test API:**
   - API Docs: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health
   - Web Interface: Open `index.html` in browser

## Deployment Options

### Option 1: Railway (Recommended)

Railway offers the simplest deployment process with automatic detection of FastAPI apps.

#### Steps:
1. **Create GitHub Repository:**
```bash
git init
git add .
git commit -m "Initial commit - HackRx 6.0 submission"
git remote add origin https://github.com/yourusername/hackrx-bajaj-genai.git
git push -u origin main
```

2. **Deploy to Railway:**
   - Visit [railway.app](https://railway.app)
   - Sign up/login with GitHub
   - Click "Deploy from GitHub repo"
   - Select your repository
   - Railway will automatically:
     - Detect Python application
     - Install dependencies from requirements.txt
     - Run with the command from railway.json
   - Get your deployment URL (e.g., `your-app-name.railway.app`)

3. **Update HTML File:**
   - Replace `API_BASE_URL` in index.html with your Railway URL
   - Commit and push changes

#### Configuration:
The included `railway.json` file automatically configures:
- Build: Dockerfile
- Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- Health check: `/health` endpoint

### Option 2: Render

Render provides free hosting with easy GitHub integration.

#### Steps:
1. **Create GitHub Repository** (same as Railway)

2. **Deploy to Render:**
   - Visit [render.com](https://render.com)
   - Sign up/login with GitHub
   - Click "New Web Service"
   - Connect your GitHub repository
   - Configure:
     - **Build Command:** `pip install -r requirements.txt`
     - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
     - **Environment:** Python 3
   - Deploy

3. **Update HTML File** with your Render URL

### Option 3: Heroku

Traditional platform with extensive documentation.

#### Steps:
1. **Create GitHub Repository** (same as above)

2. **Create Procfile:**
```
web: uvicorn main:app --host 0.0.0.0 --port $PORT
```

3. **Deploy to Heroku:**
   - Install Heroku CLI
   - `heroku login`
   - `heroku create your-app-name`
   - Connect to GitHub repository in Heroku dashboard
   - Enable automatic deploys
   - Or push directly: `git push heroku main`

4. **Update HTML File** with your Heroku URL

### Option 4: Docker Deployment

For any Docker-compatible platform.

#### Steps:
1. **Build Docker Image:**
```bash
docker build -t hackrx-bajaj-genai .
```

2. **Run Locally:**
```bash
docker run -p 8000:8000 hackrx-bajaj-genai
```

3. **Deploy to Cloud:**
   - Push to Docker Hub: `docker push yourusername/hackrx-bajaj-genai`
   - Deploy on any cloud provider supporting Docker

## GitHub Pages for HTML Interface

For hosting just the HTML interface (API must be deployed separately):

#### Steps:
1. **Create GitHub Repository**

2. **Enable GitHub Pages:**
   - Go to repository Settings
   - Scroll to "Pages" section
   - Select source: "Deploy from a branch"
   - Choose branch: "main"
   - Select folder: "/ (root)"
   - Save

3. **Access your site:**
   - URL: `https://yourusername.github.io/repository-name`
   - Update API_BASE_URL in index.html to point to your deployed API

## Environment Variables

The system uses these pre-configured values:
- **Google Gemini API Key:** `AIzaSyBwqeD-FzyCxAhlJLms4FqiZ1fl2AZiBfk`
- **Team Token:** `c0df38f44acb385ecd42f8e0c02ee14acd6d145835643ee57acd84f79afeb798`

## Testing Your Deployment

### Sample Test Data:
```json
{
  "documents": "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D",
  "questions": [
    "What is the grace period for premium payment under the National Parivar Mediclaim Plus Policy?",
    "What is the waiting period for pre-existing diseases (PED) to be covered?",
    "Does this policy cover maternity expenses, and what are the conditions?"
  ]
}
```

### API Endpoints to Test:
- `GET /` - Basic info
- `GET /health` - Health check
- `POST /hackrx/run` - Main submission endpoint
- `GET /documents/chunks` - View indexed chunks
- `POST /search` - Direct search

## Troubleshooting

### Common Issues:

1. **Port Binding Error:**
   - Ensure using `--host 0.0.0.0 --port $PORT`
   - Check if port is available

2. **Dependency Installation:**
   - Verify requirements.txt is complete
   - Check Python version compatibility (3.9+)

3. **API Connection Issues:**
   - Verify Google Gemini API key is valid
   - Check network connectivity
   - Ensure CORS is properly configured

4. **PDF Processing Errors:**
   - Verify PDF URL is accessible
   - Check PDF format compatibility
   - Ensure sufficient memory for large documents

### Performance Optimization:

1. **For Large Documents:**
   - Implement streaming processing
   - Add caching for repeated queries
   - Optimize chunk size for your use case

2. **For High Traffic:**
   - Enable Redis caching
   - Implement rate limiting
   - Scale horizontally with multiple instances

## Monitoring and Maintenance

### Health Monitoring:
- Use `/health` endpoint for uptime monitoring
- Monitor response times and error rates
- Set up alerts for API failures

### Log Analysis:
- Check application logs for errors
- Monitor PDF processing performance
- Track popular queries and optimize accordingly

## Security Considerations

- API keys are included for hackathon use
- For production use, implement:
  - Environment variable management
  - Request rate limiting
  - Input validation and sanitization
  - Authentication if needed

## Support and Documentation

- **API Documentation:** Available at `/docs` endpoint
- **GitHub Repository:** Include comprehensive README
- **Demo Interface:** Use provided index.html for testing

This deployment guide ensures your HackRx 6.0 submission is accessible online for evaluation while maintaining all required functionality and JSON input/output format.