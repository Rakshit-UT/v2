# Create HTML interface for the application (minimal interface as requested)
html_interface = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HackRx 6.0 - LLM Query Retrieval System</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Arial', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        
        .container {
            background: white;
            padding: 2rem;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            width: 90%;
            max-width: 800px;
        }
        
        .header {
            text-align: center;
            margin-bottom: 2rem;
        }
        
        .header h1 {
            color: #333;
            margin-bottom: 0.5rem;
            font-size: 2.5rem;
        }
        
        .header p {
            color: #666;
            font-size: 1.1rem;
        }
        
        .input-section {
            margin-bottom: 2rem;
        }
        
        .input-group {
            margin-bottom: 1.5rem;
        }
        
        label {
            display: block;
            margin-bottom: 0.5rem;
            font-weight: bold;
            color: #333;
        }
        
        input[type="url"], textarea {
            width: 100%;
            padding: 1rem;
            border: 2px solid #e1e5e9;
            border-radius: 8px;
            font-size: 1rem;
            transition: border-color 0.3s;
        }
        
        input[type="url"]:focus, textarea:focus {
            outline: none;
            border-color: #667eea;
        }
        
        textarea {
            resize: vertical;
            min-height: 120px;
        }
        
        .submit-btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 1rem 2rem;
            border-radius: 8px;
            font-size: 1.1rem;
            cursor: pointer;
            transition: transform 0.2s;
            width: 100%;
        }
        
        .submit-btn:hover {
            transform: translateY(-2px);
        }
        
        .submit-btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }
        
        .loading {
            display: none;
            text-align: center;
            margin: 2rem 0;
        }
        
        .loading-spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto 1rem;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .results {
            display: none;
            margin-top: 2rem;
        }
        
        .result-item {
            background: #f8f9fa;
            padding: 1.5rem;
            margin-bottom: 1rem;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }
        
        .question {
            font-weight: bold;
            color: #333;
            margin-bottom: 0.5rem;
        }
        
        .answer {
            color: #555;
            line-height: 1.6;
        }
        
        .error {
            background: #fee;
            color: #c33;
            padding: 1rem;
            border-radius: 8px;
            margin-top: 1rem;
            display: none;
        }
        
        .json-output {
            background: #1e1e1e;
            color: #f8f8f2;
            padding: 1rem;
            border-radius: 8px;
            margin-top: 1rem;
            overflow-x: auto;
            font-family: 'Courier New', monospace;
            font-size: 0.9rem;
        }
        
        .copy-btn {
            background: #28a745;
            color: white;
            border: none;
            padding: 0.5rem 1rem;
            border-radius: 4px;
            cursor: pointer;
            margin-top: 0.5rem;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 HackRx 6.0</h1>
            <p>LLM-Powered Document Query System</p>
        </div>
        
        <form id="queryForm">
            <div class="input-section">
                <div class="input-group">
                    <label for="documentUrl">📄 Document URL (PDF)</label>
                    <input 
                        type="url" 
                        id="documentUrl" 
                        placeholder="https://example.com/document.pdf"
                        required
                    >
                </div>
                
                <div class="input-group">
                    <label for="questions">❓ Questions (one per line)</label>
                    <textarea 
                        id="questions" 
                        placeholder="What is the grace period for premium payment?
What is the waiting period for pre-existing diseases?
Does this policy cover maternity expenses?"
                        required
                    ></textarea>
                </div>
            </div>
            
            <button type="submit" class="submit-btn" id="submitBtn">
                🔍 Process Queries
            </button>
        </form>
        
        <div class="loading" id="loading">
            <div class="loading-spinner"></div>
            <p>Processing your queries...</p>
        </div>
        
        <div class="error" id="error"></div>
        
        <div class="results" id="results">
            <h3>📋 Results</h3>
            <div id="resultsList"></div>
            
            <h4>📤 JSON Output</h4>
            <div class="json-output" id="jsonOutput"></div>
            <button class="copy-btn" onclick="copyJson()">📋 Copy JSON</button>
        </div>
    </div>
    
    <script>
        const API_BASE = window.location.origin;
        
        document.getElementById('queryForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const documentUrl = document.getElementById('documentUrl').value;
            const questionsText = document.getElementById('questions').value;
            const questions = questionsText.split('\\n').filter(q => q.trim());
            
            if (questions.length === 0) {
                showError('Please enter at least one question.');
                return;
            }
            
            const requestData = {
                documents: documentUrl,
                questions: questions
            };
            
            showLoading(true);
            hideError();
            hideResults();
            
            try {
                const response = await fetch(`${API_BASE}/hackrx/run`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': 'Bearer c0df38f44acb385ecd42f8e0c02ee14acd6d145835643ee57acd84f79afeb798'
                    },
                    body: JSON.stringify(requestData)
                });
                
                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.detail || 'Request failed');
                }
                
                const result = await response.json();
                displayResults(questions, result.answers, result);
                
            } catch (error) {
                console.error('Error:', error);
                showError(`Error: ${error.message}`);
            } finally {
                showLoading(false);
            }
        });
        
        function showLoading(show) {
            document.getElementById('loading').style.display = show ? 'block' : 'none';
            document.getElementById('submitBtn').disabled = show;
        }
        
        function showError(message) {
            const errorDiv = document.getElementById('error');
            errorDiv.textContent = message;
            errorDiv.style.display = 'block';
        }
        
        function hideError() {
            document.getElementById('error').style.display = 'none';
        }
        
        function hideResults() {
            document.getElementById('results').style.display = 'none';
        }
        
        function displayResults(questions, answers, fullResponse) {
            const resultsList = document.getElementById('resultsList');
            const jsonOutput = document.getElementById('jsonOutput');
            
            resultsList.innerHTML = '';
            
            questions.forEach((question, index) => {
                const resultItem = document.createElement('div');
                resultItem.className = 'result-item';
                resultItem.innerHTML = `
                    <div class="question">Q${index + 1}: ${question}</div>
                    <div class="answer">A: ${answers[index] || 'No answer provided'}</div>
                `;
                resultsList.appendChild(resultItem);
            });
            
            jsonOutput.textContent = JSON.stringify(fullResponse, null, 2);
            document.getElementById('results').style.display = 'block';
        }
        
        function copyJson() {
            const jsonText = document.getElementById('jsonOutput').textContent;
            navigator.clipboard.writeText(jsonText).then(() => {
                const btn = event.target;
                const originalText = btn.textContent;
                btn.textContent = '✅ Copied!';
                setTimeout(() => {
                    btn.textContent = originalText;
                }, 2000);
            });
        }
        
        // Auto-resize textarea
        document.getElementById('questions').addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = this.scrollHeight + 'px';
        });
    </script>
</body>
</html>
"""

# Save the HTML file
with open('index.html', 'w') as f:
    f.write(html_interface)

print("HTML interface created successfully")
print("File size:", len(html_interface), "characters")