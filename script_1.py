# Create requirements.txt file with all necessary dependencies
requirements = """
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
requests==2.31.0
PyPDF2==3.0.1
faiss-cpu==1.7.4
sentence-transformers==2.2.2
google-generativeai==0.3.2
python-multipart==0.0.6
numpy==1.24.3
pandas==2.1.3
aiofiles==23.2.1
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
"""

# Save requirements.txt
with open('requirements.txt', 'w') as f:
    f.write(requirements.strip())

print("Requirements.txt created successfully")
print("Dependencies included:", requirements.count('\n'), "packages")