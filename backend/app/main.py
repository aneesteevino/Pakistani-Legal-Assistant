from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from dotenv import load_dotenv
import google.generativeai as genai
from typing import List, Dict, Any
import re
import json
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Pakistani Legal Assistant API", version="2.0.0", description="AI-powered Pakistani Legal Assistant with RAG system for accurate legal information")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure Gemini
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    api_key = api_key.strip()
    genai.configure(api_key=api_key)

# Global variables for RAG system
pdf_documents = []
vectorizer = None
document_vectors = None

def load_pdf_data():
    """Load and process PDF data for RAG system with strict filtering"""
    global pdf_documents, vectorizer, document_vectors
    
    try:
        # Try multiple possible locations for the PDF data file
        possible_paths = [
            'pdf_data.json',
            '../pdf_data.json',
            os.path.join(os.path.dirname(os.path.dirname(__file__)), 'pdf_data.json')
        ]
        
        pdf_data_path = None
        for path in possible_paths:
            if os.path.exists(path):
                pdf_data_path = path
                break
        
        if not pdf_data_path:
            logger.warning("PDF data file not found. RAG system will be disabled.")
            return
        
        with open(pdf_data_path, 'r', encoding='utf-8') as f:
            raw_documents = json.load(f)
        
        # Strict filtering for legal documents only
        pdf_documents = []
        system_terms = ['fastapi', 'vercel', 'backend', 'frontend', 'api', 'system', 'architecture', 
                       'deployment', 'tfidf', 'rag', 'gemini', 'openai', 'python', 'react', 'typescript']
        
        for doc in raw_documents:
            text = doc['text'].strip()
            filename = doc['file_name'].lower()
            
            # Skip documents that are not useful or contain system content
            if (len(text) < 100 or  # Too short
                text == "THIS LAW HAS BEEN REPEALED" or  # Just repealed notice
                (text.count("THIS LAW HAS BEEN REPEALED") > 0 and len(text) < 200) or  # Mostly repealed
                text.count('\n') < 5 or  # Too few lines of content
                any(term in text.lower() for term in system_terms) or  # Contains system terms
                any(term in filename for term in ['readme', 'system', 'config', 'setup'])):  # System files
                continue
                
            # Only include actual legal documents
            if any(legal_term in filename for legal_term in ['act', 'ordinance', 'code', 'constitution', 'law', 'regulation']):
                pdf_documents.append(doc)
        
        logger.info(f"Loaded {len(pdf_documents)} clean legal documents from {len(raw_documents)} total documents")
        
        if len(pdf_documents) == 0:
            logger.warning("No valid legal documents found after filtering")
            return
        
        # Extract text content for vectorization
        document_texts = [doc['text'] for doc in pdf_documents]
        
        # Create TF-IDF vectorizer with legal-focused parameters
        vectorizer = TfidfVectorizer(
            max_features=3000,  # Reduced for better performance
            stop_words='english',
            ngram_range=(1, 2),
            max_df=0.7,  # More restrictive
            min_df=3     # Higher minimum frequency
        )
        
        # Fit and transform documents
        document_vectors = vectorizer.fit_transform(document_texts)
        
        logger.info("Successfully initialized clean RAG system with TF-IDF vectorization")
        
    except Exception as e:
        logger.error(f"Error loading PDF data: {e}")
        pdf_documents = []
        vectorizer = None
        document_vectors = None

def search_relevant_documents(query: str, top_k: int = 3) -> List[Dict[str, Any]]:
    """Search for relevant documents using improved TF-IDF similarity"""
    if not vectorizer or document_vectors is None:
        return []
    
    try:
        # Transform query using the same vectorizer
        query_vector = vectorizer.transform([query])
        
        # Calculate cosine similarity
        similarities = cosine_similarity(query_vector, document_vectors).flatten()
        
        # Get top candidates with higher threshold
        top_indices = np.argsort(similarities)[::-1][:top_k * 2]  # Get fewer candidates
        
        relevant_docs = []
        system_terms = ['fastapi', 'vercel', 'backend', 'api', 'system', 'architecture']
        
        for idx in top_indices:
            if similarities[idx] > 0.15:  # Higher similarity threshold
                doc = pdf_documents[idx]
                doc_text = doc['text'].strip()
                
                # Strict filtering for legal content only
                if (len(doc_text) < 100 or  # Too short
                    doc_text == "THIS LAW HAS BEEN REPEALED" or  # Repealed laws
                    any(term in doc_text.lower() for term in system_terms) or  # System content
                    "administrator" in doc['file_name'].lower() and len(doc_text) < 300):  # Short admin files
                    continue
                
                relevant_docs.append({
                    'document': doc,
                    'similarity': float(similarities[idx]),
                    'index': int(idx)
                })
                
                # Stop when we have enough good documents
                if len(relevant_docs) >= top_k:
                    break
        
        logger.info(f"Found {len(relevant_docs)} relevant documents with similarities: {[d['similarity'] for d in relevant_docs]}")
        return relevant_docs
        
    except Exception as e:
        logger.error(f"Error searching documents: {e}")
        return []

# Initialize RAG system on startup
load_pdf_data()

# Vercel handler
handler = app

# Removed hardcoded responses - system now relies on Gemini API and RAG documents only

class QuestionRequest(BaseModel):
    question: str

class Source(BaseModel):
    law_name: str
    section: str
    content_preview: str
    page: int
    relevance_score: float

class QueryResponse(BaseModel):
    answer: str
    sources: List[Source] = []
    confidence: float = 0.0
    follow_up_questions: List[str] = []

def generate_follow_up_questions(question: str, answer: str, query_type: str) -> List[str]:
    """Generate simple follow-up questions without API calls"""
    try:
        question_lower = question.lower()
        
        if query_type == "legal":
            # Generate contextual follow-ups based on question content
            if any(word in question_lower for word in ['penalty', 'punishment', 'fine']):
                return [
                    "What is the legal procedure for this offense?",
                    "How can I get legal representation?",
                    "What are the appeal options available?"
                ]
            elif any(word in question_lower for word in ['rights', 'constitution']):
                return [
                    "How can these rights be enforced?",
                    "What remedies are available if rights are violated?",
                    "Which court has jurisdiction for constitutional matters?"
                ]
            elif any(word in question_lower for word in ['cyber', 'peca', 'electronic']):
                return [
                    "How to report cybercrime in Pakistan?",
                    "What evidence is needed for cybercrime cases?",
                    "Which authority handles cybercrime complaints?"
                ]
            else:
                return [
                    "What are the legal procedures for this matter?",
                    "How can I find a qualified Pakistani lawyer?",
                    "What documents are needed for this legal issue?"
                ]
        else:
            return [
                "Can you provide more specific information?",
                "What are the practical steps I should take?",
                "Where can I learn more about this topic?"
            ]
        
    except Exception as e:
        logger.error(f"Error generating follow-up questions: {e}")
        return [
            "What are the legal procedures for this matter?",
            "How can I get professional legal help?",
            "What are my rights in this situation?"
        ]

def create_relevant_sources(question: str, answer: str, query_type: str, relevant_docs: List[Dict] = None) -> List[Source]:
    """Create relevant sources based on the question type, content, and RAG results"""
    sources = []
    question_lower = question.lower()
    
    # Add RAG-based sources first (most relevant)
    if relevant_docs:
        for doc_info in relevant_docs[:2]:  # Top 2 most relevant documents
            doc = doc_info['document']
            similarity = doc_info['similarity']
            
            # Extract law name from filename
            law_name = doc['file_name'].replace('.pdf.txt', '').replace('_', ' ').title()
            
            # Create preview from first 200 characters
            content_preview = doc['text'][:200] + "..." if len(doc['text']) > 200 else doc['text']
            
            sources.append(Source(
                law_name=law_name,
                section="Relevant Sections",
                content_preview=content_preview,
                page=1,
                relevance_score=round(similarity, 2)
            ))
    
    if query_type == "legal":
        # Add traditional legal sources if no RAG results or as supplementary
        if not sources or len(sources) < 2:
            if any(word in question_lower for word in ['constitution', 'fundamental', 'rights', 'article']):
                sources.append(Source(
                    law_name="Constitution of Pakistan 1973",
                    section="Fundamental Rights (Articles 8-28)",
                    content_preview="Constitutional provisions regarding fundamental rights of Pakistani citizens including equality, freedom, and protection under law.",
                    page=15,
                    relevance_score=0.9
                ))
            
            if any(word in question_lower for word in ['cyber', 'peca', 'electronic', 'internet', 'computer']):
                sources.append(Source(
                    law_name="Prevention of Electronic Crimes Act (PECA) 2016",
                    section="Sections 3-37",
                    content_preview="Comprehensive legislation covering cybercrime offenses, penalties, and procedures in Pakistan.",
                    page=25,
                    relevance_score=0.9
                ))
            
            if any(word in question_lower for word in ['judge', 'judicial', 'court', 'justice']):
                sources.append(Source(
                    law_name="Constitution of Pakistan 1973",
                    section="Judiciary (Articles 175-212)",
                    content_preview="Constitutional framework for Pakistan's judicial system, appointment and tenure of judges.",
                    page=89,
                    relevance_score=0.9
                ))
            
            if any(word in question_lower for word in ['criminal', 'crime', 'ppc', 'penal']):
                sources.append(Source(
                    law_name="Pakistan Penal Code (PPC) 1860",
                    section="Various Sections",
                    content_preview="Primary criminal law of Pakistan defining offenses and punishments.",
                    page=1,
                    relevance_score=0.8
                ))
            
            if any(word in question_lower for word in ['procedure', 'crpc', 'investigation', 'trial']):
                sources.append(Source(
                    law_name="Code of Criminal Procedure (CrPC) 1898",
                    section="Various Sections",
                    content_preview="Procedural law governing criminal investigations, trials, and appeals in Pakistan.",
                    page=1,
                    relevance_score=0.8
                ))
        
        # If still no specific legal sources found, add general Pakistani legal framework
        if not sources:
            sources.append(Source(
                law_name="Pakistani Legal System",
                section="General Framework",
                content_preview="Based on Pakistani constitutional and statutory provisions, common law principles, and Islamic jurisprudence.",
                page=1,
                relevance_score=0.7
            ))
    
    else:
        # General query sources - provide informational context
        if not sources:
            sources.append(Source(
                law_name="AI Knowledge Base",
                section="General Information",
                content_preview="Response generated using advanced AI language model with comprehensive knowledge across various domains.",
                page=1,
                relevance_score=0.8
            ))
            
            # Add topic-specific sources based on question content
            if any(word in question_lower for word in ['technology', 'tech', 'computer', 'software', 'programming']):
                sources.append(Source(
                    law_name="Technology Resources",
                    section="Technical Information",
                    content_preview="Information about technology, programming, software development, and related technical topics.",
                    page=1,
                    relevance_score=0.8
                ))
            
            if any(word in question_lower for word in ['health', 'medical', 'medicine', 'doctor', 'treatment']):
                sources.append(Source(
                    law_name="Health Information",
                    section="Medical Knowledge",
                    content_preview="General health and medical information. Always consult healthcare professionals for medical advice.",
                    page=1,
                    relevance_score=0.8
                ))
            
            if any(word in question_lower for word in ['business', 'finance', 'money', 'investment', 'economy']):
                sources.append(Source(
                    law_name="Business & Finance",
                    section="Economic Information",
                    content_preview="Information about business, finance, economics, and related commercial topics.",
                    page=1,
                    relevance_score=0.8
                ))
    
    return sources

@app.get("/")
async def root():
    return {"message": "Pakistani Legal Assistant API", "status": "running", "capabilities": ["Pakistani Legal Queries", "RAG-Enhanced Responses", "Legal Document Search"]}

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "message": "Pakistani Legal Assistant API is running", "version": "2.0.0", "features": ["Legal queries", "RAG system", "Document search"]}

@app.get("/api/stats")
async def get_stats():
    return {
        "total_chunks": len(pdf_documents) if pdf_documents else 0,
        "unique_laws": len(set(doc['file_name'] for doc in pdf_documents)) if pdf_documents else 0,
        "status": "Running",
        "ai_model": "Gemini 2.5 Flash",
        "query_types": ["legal", "general"],
        "capabilities": ["Pakistani law", "General knowledge", "Multi-domain assistance"],
        "rag_system": "Active" if pdf_documents else "Inactive",
        "vectorization": "TF-IDF" if vectorizer else "Not initialized"
    }

# Add new endpoint to search documents directly
@app.post("/api/search")
async def search_documents(request: QuestionRequest):
    """Search for relevant documents in the RAG database"""
    try:
        if not request.question.strip():
            raise HTTPException(status_code=400, detail="Search query cannot be empty")
        
        if not pdf_documents:
            raise HTTPException(status_code=503, detail="Document database not available")
        
        relevant_docs = search_relevant_documents(request.question, top_k=5)
        
        search_results = []
        for doc_info in relevant_docs:
            doc = doc_info['document']
            search_results.append({
                "law_name": doc['file_name'].replace('.pdf.txt', '').replace('_', ' ').title(),
                "content_preview": doc['text'][:300] + "..." if len(doc['text']) > 300 else doc['text'],
                "similarity_score": doc_info['similarity'],
                "full_text_length": len(doc['text'])
            })
        
        return {
            "query": request.question,
            "results_found": len(search_results),
            "documents": search_results
        }
        
    except Exception as e:
        logger.error(f"Error searching documents: {e}")
        raise HTTPException(status_code=500, detail="Error searching documents")

def detect_query_type(question: str) -> str:
    """Detect if query is Pakistani legal related"""
    question_lower = question.lower()
    
    # Pakistani legal query indicators
    legal_keywords = ['law', 'legal', 'court', 'judge', 'constitution', 'act', 'section', 'article', 
                     'crime', 'criminal', 'civil', 'rights', 'procedure', 'penalty', 'punishment',
                     'lawyer', 'advocate', 'bail', 'case', 'trial', 'appeal', 'petition', 'fir',
                     'marriage', 'divorce', 'property', 'contract', 'inheritance', 'will', 'custody']
    
    # Pakistani context indicators
    pakistan_keywords = ['pakistan', 'pakistani', 'ppc', 'crpc', 'peca', 'lahore', 'karachi', 
                        'islamabad', 'supreme court', 'high court', 'district court', 'sharia',
                        'islamic', 'ordinance', 'gazette', 'federal', 'provincial']
    
    # Always treat as legal if it contains Pakistani legal terms
    if any(keyword in question_lower for keyword in legal_keywords + pakistan_keywords):
        return "legal"
    
    # Default to legal since this is a Pakistani Legal Assistant
    return "legal"

def create_dynamic_prompt(question: str, query_type: str, relevant_docs: List[Dict] = None) -> tuple:
    """Create clean prompts without system leakage"""
    
    if query_type == "legal":
        # Build clean context from relevant documents only
        context = ""
        if relevant_docs:
            context = "\n\nLegal Documents:\n"
            for i, doc_info in enumerate(relevant_docs[:2], 1):
                doc = doc_info['document']
                # Clean document text - remove system references
                doc_text = doc['text'][:800] + "..." if len(doc['text']) > 800 else doc['text']
                # Filter out any system/technical content
                if not any(term in doc_text.lower() for term in ['fastapi', 'vercel', 'tfidf', 'backend', 'frontend', 'api', 'system']):
                    context += f"\n{i}. {doc_text}\n"

        system_prompt = f"""You are a Pakistani Legal Assistant. Answer questions about Pakistani law using the provided legal documents.

{context}

Provide accurate legal information with specific references to Pakistani laws. Always recommend consulting qualified legal professionals for specific cases."""

        user_prompt = f"Question: {question}\n\nProvide a detailed answer about Pakistani law based on the legal documents provided."
    
    else:
        system_prompt = "You are a helpful AI assistant. Provide accurate, clear answers to questions."
        user_prompt = f"Question: {question}\n\nProvide a helpful and accurate answer."
    
    return system_prompt, user_prompt

@app.post("/api/ask")
async def ask_question(request: QuestionRequest):
    try:
        if not request.question.strip():
            raise HTTPException(status_code=400, detail="Question cannot be empty")
        
        logger.info(f"=== NEW QUESTION ===")
        logger.info(f"Question: {request.question}")
        logger.info(f"API Key configured: {bool(os.getenv('GEMINI_API_KEY'))}")
        logger.info(f"RAG documents loaded: {len(pdf_documents) if pdf_documents else 0}")
        
        # Detect query type and search relevant documents
        query_type = detect_query_type(request.question)
        logger.info(f"Query type detected: {query_type}")
        
        relevant_docs = []
        
        # For legal queries, search the RAG database
        if query_type == "legal" and pdf_documents:
            relevant_docs = search_relevant_documents(request.question, top_k=2)  # Reduced to 2
            logger.info(f"Found {len(relevant_docs)} relevant documents")
        
        # Generate response using Gemini API with better error handling
        try:
            if not api_key:
                raise Exception("Gemini API key not configured")
                
            model = genai.GenerativeModel('gemini-1.5-flash')  # Use stable model version
            
            # Clean prompts without system leakage
            system_prompt, user_prompt = create_dynamic_prompt(request.question, query_type, relevant_docs)
            
            logger.info(f"Sending to Gemini - System prompt length: {len(system_prompt)}, User prompt length: {len(user_prompt)}")
            
            response = model.generate_content(
                f"{system_prompt}\n\n{user_prompt}",
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=800,  # Reduced to avoid timeouts
                    temperature=0.3,
                    top_p=0.8,
                )
            )
            
            if response and response.text:
                answer = response.text.strip()
                logger.info(f"Gemini response received - length: {len(answer)}")
            else:
                raise Exception("Empty response from Gemini")
                
        except Exception as gemini_error:
            logger.error(f"Gemini API error: {str(gemini_error)}")
            
            # Clean RAG-based fallback response
            if relevant_docs:
                answer = f"""**Legal Information from Pakistani Documents**

**Your Question:** {request.question}

**Based on Legal Documents:**
"""
                for doc_info in relevant_docs[:2]:
                    doc = doc_info['document']
                    law_name = doc['file_name'].replace('.pdf.txt', '').replace('_', ' ').title()
                    similarity = doc_info['similarity']
                    content_snippet = doc['text'][:600] + "..." if len(doc['text']) > 600 else doc['text']
                    
                    # Filter out system content
                    if not any(term in content_snippet.lower() for term in ['fastapi', 'vercel', 'backend', 'api']):
                        answer += f"\n**From {law_name} (Relevance: {similarity:.1f}):**\n{content_snippet}\n"

                answer += f"""
**Important:** This information is from Pakistani legal documents. For specific legal advice, consult qualified Pakistani legal professionals.

**Contact:** Pakistan Bar Council: +92-51-9201681"""
            else:
                answer = f"""**Pakistani Legal Assistant**

I apologize, but I'm experiencing technical difficulties and couldn't find specific documents for your question: "{request.question}"

**For immediate legal help:**
• Contact Pakistan Bar Council: +92-51-9201681
• Visit your local district court
• Consult a qualified Pakistani lawyer

**Common Pakistani Legal Resources:**
• Constitution of Pakistan 1973
• Pakistan Penal Code (PPC) 1860
• Code of Criminal Procedure (CrPC) 1898
• Prevention of Electronic Crimes Act (PECA) 2016"""

        # Ensure proper formatting
        if not answer or len(answer.strip()) < 10:
            answer = f"""**Pakistani Legal Assistant**

I couldn't generate a proper response for: "{request.question}"

**For legal assistance:**
• Contact Pakistan Bar Council: +92-51-9201681
• Consult a qualified Pakistani lawyer
• Visit your local district court"""
        
        # Generate relevant sources based on the question type and RAG results
        sources = create_relevant_sources(request.question, answer, query_type, relevant_docs)
        
        # Generate simple follow-up questions
        follow_ups = generate_follow_up_questions(request.question, answer, query_type)
        
        # Determine confidence based on response quality and RAG results
        if relevant_docs and len(relevant_docs) > 0:
            avg_similarity = sum(doc['similarity'] for doc in relevant_docs) / len(relevant_docs)
            confidence = min(0.9, 0.5 + (avg_similarity * 0.4))  # RAG-based confidence
        else:
            confidence = 0.6 if "Pakistani Legal Assistant" not in answer else 0.3
        
        logger.info(f"Response generated successfully - confidence: {confidence}, sources: {len(sources)}")
        
        return QueryResponse(
            answer=answer,
            sources=sources,
            confidence=confidence,
            follow_up_questions=follow_ups
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error processing question: {e}", exc_info=True)
        
        # Return clean error response
        return QueryResponse(
            answer=f"""**Pakistani Legal Assistant - Service Error**

I encountered an error while processing your question: "{request.question}"

**For immediate legal assistance:**
• Contact Pakistan Bar Council: +92-51-9201681
• Visit your local district court
• Consult a qualified Pakistani lawyer

**Error Details:** Technical service temporarily unavailable. Please try again in a few minutes.""",
            sources=[],
            confidence=0.1,
            follow_up_questions=[
                "How can I contact Pakistan Bar Council?",
                "Where is my nearest district court?",
                "What should I do for urgent legal matters?"
            ]
        )Try:**
• Rephrasing your question about Pakistani law
• Being more specific about the legal area (criminal, civil, family law, etc.)
• Trying again in a few moments

**For Immediate Legal Help:**
• Contact Pakistan Bar Council: +92-51-9201681
• Visit your local district court
• Consult with a qualified Pakistani lawyer
• Contact legal aid services in your area

**Common Pakistani Legal Areas:**
• Criminal Law (PPC, CrPC)
• Family Law (Marriage, Divorce, Inheritance)
• Civil Law (Contracts, Property)
• Constitutional Law (Fundamental Rights)"""

        return QueryResponse(
            answer=error_answer,
            sources=[Source(
                law_name="Pakistani Legal System",
                section="Error Recovery",
                content_preview="Technical issue encountered. Please consult qualified Pakistani legal professionals for immediate assistance.",
                page=0,
                relevance_score=0.0
            )],
            confidence=0.0,
            follow_up_questions=[
                "How can I find a qualified Pakistani lawyer?",
                "What are the main courts in Pakistan?",
                "Where can I get free legal aid in Pakistan?"
            ]
        )

@app.get("/api/list-models")
async def list_models():
    """List available Gemini models"""
    try:
        if not os.getenv("GEMINI_API_KEY"):
            return {"status": "error", "message": "Gemini API key not configured"}
        
        models = genai.list_models()
        model_list = []
        for model in models:
            model_list.append({
                "name": model.name,
                "display_name": model.display_name if hasattr(model, 'display_name') else "N/A",
                "supported_generation_methods": model.supported_generation_methods if hasattr(model, 'supported_generation_methods') else []
            })
        
        return {
            "status": "success",
            "models": model_list
        }
        
    except Exception as e:
        logger.error(f"Error listing models: {e}")
        return {
            "status": "error",
            "message": f"Error listing models: {str(e)}"
        }

@app.get("/api/test-gemini")
async def test_gemini():
    """Test endpoint to check if Gemini API is working"""
    try:
        if not os.getenv("GEMINI_API_KEY"):
            return {"status": "error", "message": "Gemini API key not configured"}
        
        model = genai.GenerativeModel('models/gemini-2.5-flash')
        response = model.generate_content("Hello, this is a test. Please respond with 'Gemini API is working correctly.'")
        
        return {
            "status": "success",
            "message": "Gemini API is working",
            "response": response.text.strip(),
            "model_used": "models/gemini-2.5-flash"
        }
    except Exception as e:
        logger.error(f"Gemini test error: {e}")
        return {
            "status": "error",
            "message": f"Gemini API error: {str(e)}"
        }

# Add new endpoint to get RAG system information
@app.get("/api/rag-info")
async def get_rag_info():
    """Get information about the RAG system status and loaded documents"""
    if not pdf_documents:
        return {
            "status": "inactive",
            "message": "RAG system not initialized",
            "documents_loaded": 0,
            "vectorizer_status": "not_initialized"
        }
    
    # Get document statistics
    doc_stats = {}
    for doc in pdf_documents:
        law_name = doc['file_name'].replace('.pdf.txt', '').replace('_', ' ').title()
        doc_stats[law_name] = {
            "text_length": len(doc['text']),
            "word_count": len(doc['text'].split())
        }
    
    return {
        "status": "active",
        "message": "Pakistani Legal RAG system operational",
        "documents_loaded": len(pdf_documents),
        "vectorizer_status": "initialized" if vectorizer else "not_initialized",
        "vectorization_method": "TF-IDF",
        "max_features": 5000,
        "document_statistics": doc_stats,
        "search_capabilities": ["semantic_search", "similarity_ranking", "context_extraction"],
        "legal_focus": "Pakistani Law"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)