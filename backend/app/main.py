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
    """Load and process PDF data for RAG system"""
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
        
        # Filter out useless documents during loading
        pdf_documents = []
        for doc in raw_documents:
            text = doc['text'].strip()
            # Skip documents that are not useful
            if (len(text) < 50 or  # Too short
                text == "THIS LAW HAS BEEN REPEALED" or  # Just repealed notice
                (text.count("THIS LAW HAS BEEN REPEALED") > 0 and len(text) < 100) or  # Mostly repealed
                text.count('\n') < 3):  # Too few lines of content
                continue
            pdf_documents.append(doc)
        
        logger.info(f"Loaded {len(pdf_documents)} useful documents from {len(raw_documents)} total documents")
        
        # Extract text content for vectorization
        document_texts = [doc['text'] for doc in pdf_documents]
        
        # Create TF-IDF vectorizer
        vectorizer = TfidfVectorizer(
            max_features=5000,
            stop_words='english',
            ngram_range=(1, 2),
            max_df=0.8,
            min_df=2
        )
        
        # Fit and transform documents
        document_vectors = vectorizer.fit_transform(document_texts)
        
        logger.info("Successfully initialized RAG system with TF-IDF vectorization")
        
    except Exception as e:
        logger.error(f"Error loading PDF data: {e}")
        pdf_documents = []
        vectorizer = None
        document_vectors = None

def search_relevant_documents(query: str, top_k: int = 3) -> List[Dict[str, Any]]:
    """Search for relevant documents using TF-IDF similarity"""
    if not vectorizer or document_vectors is None:
        return []
    
    try:
        # Transform query using the same vectorizer
        query_vector = vectorizer.transform([query])
        
        # Calculate cosine similarity
        similarities = cosine_similarity(query_vector, document_vectors).flatten()
        
        # Get top-k most similar documents
        top_indices = np.argsort(similarities)[::-1][:top_k * 3]  # Get more candidates to filter
        
        relevant_docs = []
        for idx in top_indices:
            if similarities[idx] > 0.1:  # Minimum similarity threshold
                doc = pdf_documents[idx]
                doc_text = doc['text'].strip()
                
                # Filter out useless documents
                if (len(doc_text) < 50 or  # Too short
                    doc_text == "THIS LAW HAS BEEN REPEALED" or  # Repealed laws
                    doc_text.count("THIS LAW HAS BEEN REPEALED") > 0 and len(doc_text) < 100 or  # Mostly repealed text
                    "administrator" in doc['file_name'].lower() and len(doc_text) < 200):  # Short admin files
                    continue
                
                relevant_docs.append({
                    'document': doc,
                    'similarity': float(similarities[idx]),
                    'index': int(idx)
                })
                
                # Stop when we have enough good documents
                if len(relevant_docs) >= top_k:
                    break
        
        return relevant_docs
        
    except Exception as e:
        logger.error(f"Error searching documents: {e}")
        return []

# Initialize RAG system on startup
load_pdf_data()

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
    """Generate relevant follow-up questions using Gemini API"""
    try:
        model = genai.GenerativeModel('models/gemini-2.5-flash')
        
        if query_type == "legal":
            follow_up_prompt = f"""Based on this Pakistani legal question and answer, generate 3 relevant follow-up questions that would help the user explore the topic deeper.

Original Question: {question}
Answer: {answer[:500]}...

Generate 3 specific, actionable follow-up questions about Pakistani law that are:
1. Related to the original topic
2. Practical and useful for the user
3. About Pakistani legal system, procedures, or rights

Format: Return only the 3 questions, one per line, without numbering or bullets."""
        else:
            follow_up_prompt = f"""Based on this question and answer, generate 3 relevant follow-up questions that would help the user explore the topic deeper.

Original Question: {question}
Answer: {answer[:500]}...

Generate 3 specific, actionable follow-up questions that are:
1. Related to the original topic
2. Practical and useful for the user
3. Help them understand the topic better or take next steps

Format: Return only the 3 questions, one per line, without numbering or bullets."""

        response = model.generate_content(
            follow_up_prompt,
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=200,
                temperature=0.7,
                top_p=0.8,
            )
        )
        
        questions = [q.strip() for q in response.text.split('\n') if q.strip()]
        return questions[:3]  # Return max 3 questions
        
    except Exception as e:
        print(f"Error generating follow-up questions: {e}")
        # Fallback questions based on query type
        if query_type == "legal":
            return [
                "What are the legal procedures related to this matter?",
                "How can I get legal help for this issue?",
                "What are my rights in this situation?"
            ]
        else:
            return [
                "Can you explain this topic in more detail?",
                "What are the practical applications of this information?",
                "Where can I learn more about this subject?"
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
    """Create appropriate prompts based on query type and RAG context"""
    
    if query_type == "legal":
        # Build context from relevant documents
        context = ""
        if relevant_docs:
            context = "\n\nRELEVANT LEGAL DOCUMENTS:\n"
            for i, doc_info in enumerate(relevant_docs[:3], 1):
                doc = doc_info['document']
                law_name = doc['file_name'].replace('.pdf.txt', '').replace('_', ' ').title()
                # Use first 1000 characters to avoid token limits
                doc_text = doc['text'][:1000] + "..." if len(doc['text']) > 1000 else doc['text']
                context += f"\n{i}. {law_name}:\n{doc_text}\n"

        system_prompt = f"""You are an expert Pakistani Legal Assistant with comprehensive knowledge of Pakistani law, including:

- Constitution of Pakistan 1973
- Pakistan Penal Code (PPC) 1860
- Code of Criminal Procedure (CrPC) 1898
- Prevention of Electronic Crimes Act (PECA) 2016
- Family Laws Ordinance 1961
- Contract Act 1872
- Evidence Act 1984
- Civil Procedure Code (CPC) 1908
- Pakistani court system and legal procedures
- Islamic jurisprudence as applied in Pakistan

{context}

INSTRUCTIONS:
1. Use the relevant legal documents provided above as your primary source of information
2. Provide accurate, detailed information about Pakistani law
3. Use clear bullet points and structured formatting
4. Include specific legal references (articles, sections, acts) from the provided documents
5. Mention relevant court procedures and legal processes
6. Provide practical guidance while recommending professional legal consultation
7. Be specific about Pakistani legal context and jurisdiction
8. If the provided documents don't contain sufficient information, clearly state this and provide general guidance

RESPONSE FORMAT:
**Answer:**
• [Detailed legal explanation with specific Pakistani law references from provided documents]
• [Key procedures, requirements, or penalties based on the legal texts]
• [Practical steps or guidance for the user]

**Legal Framework:**
• [Relevant Pakistani laws, acts, or constitutional provisions from the documents]
• [Court procedures or legal processes mentioned in the sources]
• [Important legal precedents if applicable]

**Important Note:**
• [Disclaimer about consulting qualified Pakistani legal professionals]"""

        user_prompt = f"""Question about Pakistani Law: {question}

Please provide a comprehensive answer about this Pakistani legal matter using the relevant legal documents provided. Include relevant laws, procedures, penalties, and practical guidance. Be specific about Pakistani legal context and cite the provided legal sources where applicable."""
    
    else:
        # General query handling
        system_prompt = """You are a knowledgeable AI assistant that can help with a wide variety of questions and topics. You provide accurate, helpful, and well-structured information.

INSTRUCTIONS:
1. Provide clear, accurate, and comprehensive answers
2. Use proper formatting with bullet points when appropriate
3. Be helpful and informative
4. If you're unsure about something, clearly state your limitations
5. Provide practical guidance when applicable
6. Structure your response clearly

RESPONSE FORMAT:
**Answer:**
• [Clear explanation of the topic or question]
• [Key points, facts, or information]
• [Practical guidance or next steps if applicable]

**Additional Information:**
• [Related concepts, tips, or considerations]
• [Resources or references if helpful]"""

        user_prompt = f"""Question: {question}

Please provide a comprehensive and helpful answer to this question."""
    
    return system_prompt, user_prompt

@app.post("/api/ask")
async def ask_question(request: QuestionRequest):
    try:
        if not request.question.strip():
            raise HTTPException(status_code=400, detail="Question cannot be empty")
        
        # Check if Gemini API key is configured
        if not os.getenv("GEMINI_API_KEY"):
            raise HTTPException(status_code=500, detail="Gemini API key not configured")
        
        logger.info(f"Processing question: {request.question[:100]}...")
        
        # Detect query type and search relevant documents
        query_type = detect_query_type(request.question)
        relevant_docs = []
        
        # For legal queries, search the RAG database
        if query_type == "legal" and pdf_documents:
            relevant_docs = search_relevant_documents(request.question, top_k=3)
            logger.info(f"Found {len(relevant_docs)} relevant documents for query")
        
        # Create dynamic prompts with RAG context
        system_prompt, user_prompt = create_dynamic_prompt(request.question, query_type, relevant_docs)

        # Generate response using Gemini API or intelligent fallback
        try:
            model = genai.GenerativeModel('models/gemini-2.5-flash')  # Correct model name with 'models/' prefix
            
            response = model.generate_content(
                f"{system_prompt}\n\n{user_prompt}",
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=1000,
                    temperature=0.2 if query_type == "legal" else 0.3,
                    top_p=0.8,
                    top_k=30,
                )
            )
            
            answer = response.text.strip()
            logger.info(f"Generated response length: {len(answer)}")
            
        except Exception as gemini_error:
            logger.error(f"Gemini API error: {gemini_error}")
            
            # Enhanced RAG-based response when Gemini API fails
            if relevant_docs:
                # Create a comprehensive response using RAG documents
                doc_content = ""
                law_sources = []
                
                for doc_info in relevant_docs[:3]:
                    doc = doc_info['document']
                    law_name = doc['file_name'].replace('.pdf.txt', '').replace('_', ' ').title()
                    similarity = doc_info['similarity']
                    
                    # Use substantial content for comprehensive answers
                    content_snippet = doc['text'][:1500] + "..." if len(doc['text']) > 1500 else doc['text']
                    doc_content += f"\n\n**From {law_name} (Relevance: {similarity:.2f}):**\n{content_snippet}"
                    law_sources.append(law_name)
                
                # Create intelligent summary based on question type
                question_lower = request.question.lower()
                if any(word in question_lower for word in ['section', 'article', 'law', 'act', 'code']):
                    intro = "**Legal Provision Information**"
                elif any(word in question_lower for word in ['procedure', 'process', 'how to', 'steps']):
                    intro = "**Legal Procedure Information**"
                elif any(word in question_lower for word in ['rights', 'protection', 'freedom']):
                    intro = "**Rights and Protections**"
                else:
                    intro = "**Pakistani Legal Information**"
                
                answer = f"""{intro}

**Your Question:** {request.question}

**Based on Pakistani Legal Documents:**{doc_content}

**Summary:** This information is extracted from {len(relevant_docs)} relevant Pakistani legal documents including {', '.join(law_sources[:2])}.

**For Detailed Legal Advice:**
• Consult a qualified Pakistani lawyer
• Contact Pakistan Bar Council: +92-51-9201681
• Visit your local district court
• Access complete legal documents

**Important:** This information is sourced from official Pakistani legal documents. For specific legal advice and current interpretations, always consult qualified legal professionals."""
            else:
                # Enhanced fallback when no RAG documents found
                answer = f"""**Pakistani Legal Information**

**Your Question:** {request.question}

**Status:** The AI service is temporarily unavailable, and no specific documents were found for your query in our legal database.

**Recommended Actions:**
• **Immediate Help:** Contact Pakistan Bar Council at +92-51-9201681
• **Local Assistance:** Visit your nearest district court
• **Legal Aid:** Contact legal aid services in your area
• **Online Resources:** Visit Pakistan's official legal portals

**Key Pakistani Legal Resources:**
• **Constitutional Law:** Constitution of Pakistan 1973
• **Criminal Law:** Pakistan Penal Code (PPC) 1860, CrPC 1898
• **Family Law:** Family Laws Ordinance 1961
• **Cyber Law:** Prevention of Electronic Crimes Act (PECA) 2016
• **Civil Law:** Contract Act 1872, Transfer of Property Act 1882

**Professional Consultation Required:** For specific legal matters, professional legal advice is essential as laws can have complex interpretations and recent amendments."""

        # Ensure proper formatting
        if not answer:
            answer = "I apologize, but I couldn't generate a proper response. Please try rephrasing your question about Pakistani law."
        
        # Generate relevant sources based on the question type and RAG results
        sources = create_relevant_sources(request.question, answer, query_type, relevant_docs)
        
        # Generate follow-up questions using Gemini
        try:
            follow_ups = generate_follow_up_questions(request.question, answer, query_type)
        except Exception as followup_error:
            logger.error(f"Error generating follow-up questions: {followup_error}")
            follow_ups = [
                "What are the legal procedures for this matter?",
                "How can I find a qualified Pakistani lawyer?",
                "What documents do I need for this legal issue?"
            ]
        
        # Determine confidence based on response quality, query type, and RAG results
        if "Gemini API error" in str(locals().get('gemini_error', '')):
            # When using RAG fallback, confidence depends on document relevance
            if relevant_docs and len(relevant_docs) > 0:
                avg_similarity = sum(doc['similarity'] for doc in relevant_docs) / len(relevant_docs)
                confidence = min(0.85, 0.6 + (avg_similarity * 0.25))  # RAG-based confidence
            else:
                confidence = 0.3  # Low confidence when no relevant docs
        else:
            # Normal Gemini API response confidence
            base_confidence = 0.9 if len(answer) > 200 and ("**Answer:**" in answer or query_type == "general") else 0.7
            rag_boost = 0.1 if relevant_docs else 0.0
            confidence = min(1.0, base_confidence + rag_boost)
        
        logger.info(f"Response generated successfully with confidence: {confidence}")
        
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
        # Return helpful error response
        error_answer = """I apologize, but I encountered an error while processing your Pakistani legal question.

**Possible Issues:**
• Temporary connectivity issue with the AI service
• Complex legal query that needs clarification
• System overload

**Please Try:**
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