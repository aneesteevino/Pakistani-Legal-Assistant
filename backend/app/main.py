from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from dotenv import load_dotenv
import google.generativeai as genai
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

# Configure Gemini
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    api_key = api_key.strip()
    genai.configure(api_key=api_key)

class QuestionRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    answer: str
    sources: list = []
    confidence: float = 0.0

class ApiStats(BaseModel):
    total_chunks: int
    unique_laws: int
    status: str

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
    # Fallback values since pdf_data.json is too large for Vercel
    total_docs = len(LEGAL_DOCUMENTS) if LEGAL_DOCUMENTS else 1250  # Fallback number
    return ApiStats(
        total_chunks=total_docs,
        unique_laws=50,  # Placeholder - you can calculate actual unique laws
        status="Running"
    )

@app.post("/api/ask")
async def ask_question(request: QuestionRequest):
    try:
        if not request.question.strip():
            raise HTTPException(status_code=400, detail="Question cannot be empty")
        
        # Check if Gemini API key is configured
        if not os.getenv("GEMINI_API_KEY"):
            raise HTTPException(status_code=500, detail="Gemini API key not configured")
        
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
        
        # If no relevant documents found, provide a general response
        if not context.strip():
            context = "No specific legal documents found for this query. Please provide a general response about Pakistani law."
        
        # Generate response using Gemini
        system_prompt = """You are an expert Pakistani legal assistant with deep knowledge of Pakistani law, constitution, and legal procedures. 
        
        Your task is to provide comprehensive, detailed, and well-structured answers about Pakistani law based on the provided context.
        
        Guidelines for your responses:
        1. Provide detailed explanations in paragraph form (minimum 3-4 sentences per main point)
        2. Include relevant legal citations, article numbers, and section references when available
        3. Explain the practical implications and applications of the law
        4. Use clear, professional language that both lawyers and citizens can understand
        5. Structure your response with multiple paragraphs when covering different aspects
        6. If you're uncertain about specific details, clearly state your limitations
        7. Provide context about how the law fits into Pakistan's broader legal framework
        8. ALWAYS end your response with:
           - A question asking if the user needs clarification on any specific aspect
           - 2-3 related follow-up questions they might want to explore
        
        Always aim for comprehensive responses that thoroughly address the question."""
        
        user_prompt = f"""Legal Context from Pakistani Documents: {context}
        
        User Question: {request.question}
        
        Please provide a comprehensive, detailed answer that thoroughly explains the legal aspects of this question. 
        Your response should be informative, well-structured, and contain multiple paragraphs with detailed explanations.
        Include relevant legal principles, procedures, and practical implications where applicable.

        IMPORTANT: End your response with:
        1. A question asking if they need clarification on any specific aspect
        2. 2-3 related follow-up questions they might want to explore, formatted as:
           "You might also want to explore:
           • [Related question 1]
           • [Related question 2] 
           • [Related question 3]"
        
        Make sure the follow-up questions are directly related to the topic and would be genuinely helpful for someone seeking legal guidance."""
        
        # Initialize Gemini model
        model = genai.GenerativeModel('models/gemini-2.5-flash')
        
        # Generate response
        response = model.generate_content(
            f"{system_prompt}\n\n{user_prompt}",
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=1500,  # Increased for longer responses
                temperature=0.4,  # Slightly higher for more varied responses
                top_p=0.8,  # Add top_p for better response quality
                top_k=40,  # Add top_k for more diverse vocabulary
            )
        )
        
        answer = response.text
        
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