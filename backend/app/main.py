from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from dotenv import load_dotenv
import openai
import json
from pathlib import Path

# Load environment variables
load_dotenv()

app = FastAPI(title="Pakistani Legal Assistant API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

class QuestionRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    answer: str
    sources: list = []
    confidence: float = 0.0

class ApiStats(BaseModel):
    total_documents: int
    total_queries: int
    uptime: str

# Load legal data
def load_legal_data():
    """Load legal documents from pdf_data.json"""
    try:
        data_file = Path("../pdf_data.json")
        if not data_file.exists():
            data_file = Path("../../pdf_data.json")
        
        if data_file.exists():
            with open(data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading legal data: {e}")
    
    return []

# Global variable to store legal documents
LEGAL_DOCUMENTS = load_legal_data()

@app.get("/")
async def root():
    return {"message": "Pakistani Legal Assistant API", "status": "running"}

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "message": "API is running"}

@app.get("/api/stats")
async def get_stats():
    return ApiStats(
        total_documents=len(LEGAL_DOCUMENTS),
        total_queries=0,  # You can implement query counting
        uptime="Running"
    )

@app.post("/api/ask")
async def ask_question(request: QuestionRequest):
    try:
        if not request.question.strip():
            raise HTTPException(status_code=400, detail="Question cannot be empty")
        
        # Simple search through documents
        relevant_docs = []
        question_lower = request.question.lower()
        
        for doc in LEGAL_DOCUMENTS[:5]:  # Limit to first 5 docs for demo
            if any(keyword in doc.get('content', '').lower() for keyword in question_lower.split()):
                relevant_docs.append(doc)
        
        # Create context from relevant documents
        context = ""
        sources = []
        
        for doc in relevant_docs[:3]:  # Use top 3 relevant docs
            context += f"\n{doc.get('content', '')[:500]}..."
            sources.append({
                "title": doc.get('title', 'Legal Document'),
                "page": doc.get('page', 1)
            })
        
        # Generate response using OpenAI
        system_prompt = """You are a Pakistani legal assistant. Answer questions about Pakistani law based on the provided context. 
        Be accurate, cite relevant laws when possible, and if you're not certain about something, say so.
        Keep responses concise but informative."""
        
        user_prompt = f"""Context: {context}
        
        Question: {request.question}
        
        Please provide a helpful answer based on the context provided."""
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=500,
            temperature=0.3
        )
        
        answer = response.choices[0].message.content
        
        return QueryResponse(
            answer=answer,
            sources=sources,
            confidence=0.8 if relevant_docs else 0.3
        )
        
    except Exception as e:
        print(f"Error processing question: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing question: {str(e)}")

@app.post("/api/search")
async def search_documents(request: QuestionRequest):
    try:
        question_lower = request.question.lower()
        results = []
        
        for doc in LEGAL_DOCUMENTS:
            if any(keyword in doc.get('content', '').lower() for keyword in question_lower.split()):
                results.append({
                    "title": doc.get('title', 'Legal Document'),
                    "content": doc.get('content', '')[:200] + "...",
                    "page": doc.get('page', 1),
                    "relevance": 0.8
                })
        
        return {"results": results[:10]}  # Return top 10 results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)