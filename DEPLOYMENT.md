
# 🚀 Deployment Guide - HackRx 6.0 Solution

## Quick Deploy Options (Recommended for Hackathon)

### 1. Railway (Recommended - Free & Fast)
1. Fork this repository to your GitHub
2. Sign up at https://railway.app
3. Connect your GitHub account
4. Click "Deploy from GitHub repo"
5. Select your forked repository
6. Railway will auto-detect Python and deploy
7. Get your live URL within 5 minutes!

### 2. Render (Alternative)
1. Fork this repository
2. Sign up at https://render.com
3. Create new "Web Service"
4. Connect your GitHub repo
5. Use these settings:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
6. Deploy and get your URL

### 3. Vercel (Serverless)
1. Fork this repository
2. Sign up at https://vercel.com
3. Import your GitHub repo
4. Vercel auto-deploys with vercel.json config
5. Perfect for serverless deployment

## Local Development

### Option 1: Quick Start (Recommended)
```bash
# For Unix/Linux/Mac
chmod +x deploy.sh
./deploy.sh

# For Windows
deploy.bat
```

### Option 2: Manual Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Option 3: Docker
```bash
# Build image
docker build -t hackrx-solution .

# Run container
docker run -p 8000:8000 hackrx-solution
```

## Testing the Deployment

Once deployed, test your API:

1. **Health Check**: GET `https://your-domain.com/health`
2. **Main Endpoint**: POST `https://your-domain.com/hackrx/run`
3. **API Docs**: `https://your-domain.com/docs`

### Sample Test Request:
```bash
curl -X POST "https://your-domain.com/hackrx/run" \
-H "Content-Type: application/json" \
-H "Authorization: Bearer c0df38f44acb385ecd42f8e0c02ee14acd6d145835643ee57acd84f79afeb798" \
-d '{
  "documents": "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D",
  "questions": [
    "What is the grace period for premium payment?",
    "What is the waiting period for pre-existing diseases?"
  ]
}'
```

## Troubleshooting

### Common Issues:
1. **Port Issues**: Make sure your app binds to `0.0.0.0:$PORT`
2. **Dependencies**: Ensure all packages are in requirements.txt
3. **Python Version**: Most platforms support Python 3.8-3.11
4. **API Keys**: Verify Google Gemini API key is valid
5. **Memory**: Some platforms have memory limits for free tiers

### Platform-Specific Notes:
- **Railway**: Best for hackathons, generous free tier
- **Render**: Good performance, hibernates after inactivity on free tier
- **Vercel**: Serverless, good for APIs with intermittent traffic

## For Hackathon Submission

1. **Choose Railway** for fastest deployment
2. **Test thoroughly** with provided sample data
3. **Submit the live URL** for evaluation
4. **Keep logs accessible** for debugging if needed

Your live API will be ready in under 10 minutes! 🎉
