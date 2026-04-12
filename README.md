# ⚖️ Pakistani Legal Assistant - Enhanced RAG System

A sophisticated AI-powered legal assistant with advanced RAG (Retrieval-Augmented Generation) capabilities, designed to provide comprehensive Pakistani legal analysis with structured responses and enhanced accuracy.

![Pakistani Legal Assistant](https://img.shields.io/badge/Status-Live-brightgreen)
![React](https://img.shields.io/badge/React-18.x-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Latest-green)
![TypeScript](https://img.shields.io/badge/TypeScript-5.x-blue)
![Gemini AI](https://img.shields.io/badge/Gemini-1.5%20Flash-orange)

## ✨ Enhanced Features

### 🧠 Advanced AI Legal Analysis
- **Structured Response Format**: Mandatory 5-section format for comprehensive legal guidance
  1. Legal Understanding of the Issue
  2. Relevant Pakistani Law
  3. Step-by-Step Legal Procedure
  4. Practical Advice
  5. Prevention / Best Practice
- **Enhanced Query Detection**: Improved Pakistani legal context recognition
- **Comprehensive Legal Coverage**: Constitutional, Criminal, Civil, Family, Cyber, and Property law
- **Contextual Follow-ups**: Intelligent follow-up questions based on legal domain

### 🔍 Improved RAG System
- **Enhanced Document Search**: Boosted relevance for Pakistani legal terms
- **Better Filtering**: Advanced filtering to eliminate system/technical content
- **Legal Domain Focus**: Specialized vectorization for legal documents
- **Quality Scoring**: Confidence scoring based on document relevance and AI certainty

### 🎨 Modern UI Design
- **Dark Theme**: Sophisticated color palette with legal gold accents
- **Glassmorphism Effects**: Backdrop blur and transparency for modern aesthetics
- **Responsive Design**: Optimized for desktop, tablet, and mobile devices
- **Enhanced Sample Questions**: 12 comprehensive legal scenarios

### 📊 System Monitoring
- **Advanced Status Endpoint**: Comprehensive system health monitoring
- **Component Status**: Real-time status of Gemini AI, RAG system, and database
- **Performance Metrics**: Response times, capabilities, and system limits
- **Legal Document Analytics**: Breakdown by law types (Constitutional, Criminal, etc.)

## 🚀 Live Demo

- **Frontend**: [https://pakistani-legal-assistant.vercel.app](https://pakistani-legal-assistant.vercel.app)
- **Backend API**: [https://backend-phi-eight-99.vercel.app](https://backend-phi-eight-99.vercel.app)
- **API Docs**: [https://backend-phi-eight-99.vercel.app/docs](https://backend-phi-eight-99.vercel.app/docs)
- **System Status**: [https://backend-phi-eight-99.vercel.app/api/system-status](https://backend-phi-eight-99.vercel.app/api/system-status)

## 🛠️ Tech Stack

### Backend Enhancements
- **FastAPI** with enhanced error handling and structured responses
- **Google Gemini 1.5 Flash** with optimized generation parameters
- **Advanced RAG Pipeline** with TF-IDF vectorization and legal domain boosting
- **Comprehensive Logging** for better debugging and monitoring
- **Structured Prompting** following Pakistani Legal RAG best practices

### Frontend Improvements
- **Enhanced Sample Questions** covering major Pakistani legal areas
- **Improved Error Handling** with graceful fallbacks
- **Better Mobile Experience** with responsive design improvements
- **System Status Integration** for real-time monitoring

## 📦 Installation & Setup

### Prerequisites
- Node.js 18+ and npm
- Python 3.13+
- Gemini API key from Google AI Studio

### Backend Setup

```bash
# Clone repository
git clone https://github.com/yourusername/pakistani-legal-assistant.git
cd pakistani-legal-assistant

# Setup backend
cd backend
pip install -r requirements.txt

# Create .env file with your Gemini API key
echo "GEMINI_API_KEY=your_api_key_here" > .env

# Run backend with enhanced features
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

```bash
# Setup frontend (in new terminal)
cd frontend
npm install

# Configure API endpoint (optional - defaults to localhost:8000)
echo "REACT_APP_API_URL=http://localhost:8000" > .env.local

# Run frontend
npm start
```

Visit `http://localhost:3000` to see the enhanced application.

## 🎯 Enhanced Usage Examples

### Comprehensive Legal Analysis

The system now provides structured responses for all Pakistani legal queries:

**Input**: "What are the penalties for cybercrime under PECA?"

**Output Structure**:
1. **Legal Understanding**: Clear explanation of cybercrime in Pakistani context
2. **Relevant Law**: PECA 2016 sections and constitutional provisions
3. **Step-by-Step Procedure**: How to report, investigate, and prosecute
4. **Practical Advice**: Contact information, documentation requirements
5. **Prevention**: Best practices to avoid cybercrime issues

### Enhanced Sample Questions

The system now includes 12 comprehensive legal scenarios:

1. **Constitutional Law**: Fundamental rights and judicial system
2. **Criminal Law**: PPC offenses, FIR procedures, bail applications
3. **Cyber Law**: PECA violations, cybercrime reporting
4. **Family Law**: Marriage registration, divorce procedures
5. **Property Law**: Transfer procedures, inheritance laws
6. **Civil Procedure**: Court jurisdiction, legal timelines

### API Usage

```bash
# Ask enhanced legal question
curl -X POST http://localhost:8000/api/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the procedure for filing a constitutional petition in Pakistan?"}'

# Get comprehensive system status
curl http://localhost:8000/api/system-status

# Search legal documents with enhanced filtering
curl -X POST http://localhost:8000/api/search \
  -H "Content-Type: application/json" \
  -d '{"question": "PECA cybercrime penalties"}'
```

## 🔧 Enhanced Configuration

### Environment Variables

#### Backend (.env)
```env
GEMINI_API_KEY=your_gemini_api_key_from_google_ai_studio
# Optional: Supabase for future database integration
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
```

#### Frontend (.env.production)
```env
REACT_APP_API_URL=https://your-backend.vercel.app
```

### Advanced Customization

#### RAG System Parameters
```python
# In backend/app/main.py - TF-IDF Configuration
vectorizer = TfidfVectorizer(
    max_features=3000,      # Vocabulary size
    stop_words='english',   # Remove common words
    ngram_range=(1, 2),     # Unigrams and bigrams
    max_df=0.7,            # Maximum document frequency
    min_df=3               # Minimum document frequency
)
```

#### Gemini AI Parameters
```python
generation_config=genai.types.GenerationConfig(
    max_output_tokens=1200,  # Comprehensive responses
    temperature=0.2,         # Consistent legal advice
    top_p=0.9,              # Nucleus sampling
    top_k=40,               # Top-k sampling
)
```

## 📚 Enhanced API Documentation

### New Endpoints

- `GET /api/system-status` - Comprehensive system health and capabilities
- `POST /api/ask` - Enhanced with structured Pakistani legal responses
- `POST /api/search` - Improved document search with legal domain boosting

### Response Format

```json
{
  "answer": "**Legal Understanding of the Issue:**\n[Structured response]...",
  "sources": [
    {
      "law_name": "Prevention of Electronic Crimes Act 2016",
      "section": "Section 3-37",
      "content_preview": "Comprehensive legislation covering...",
      "page": 25,
      "relevance_score": 0.92
    }
  ],
  "confidence": 0.89,
  "follow_up_questions": [
    "How to report cybercrime to FIA in Pakistan?",
    "What evidence is needed for cybercrime cases under PECA?",
    "Which authority handles different types of cybercrimes?"
  ]
}
```

### System Status Response

```json
{
  "system_status": "operational",
  "timestamp": "2024-12-20T10:30:00Z",
  "version": "2.1.0",
  "components": {
    "gemini_ai": {
      "status": "connected",
      "model": "gemini-1.5-flash",
      "api_key_configured": true
    },
    "rag_system": {
      "status": "active",
      "total_documents": 1247,
      "document_types": {
        "Constitutional Law": 45,
        "Criminal Law": 312,
        "Cyber Law": 28,
        "Family Law": 156
      }
    }
  },
  "capabilities": {
    "pakistani_legal_analysis": true,
    "structured_responses": true,
    "document_search": true,
    "confidence_scoring": true
  }
}
```

## 🚀 Deployment

The enhanced system maintains the same deployment process:

```bash
# Deploy backend with enhanced features
cd backend && vercel --prod

# Deploy frontend with improved UI
cd frontend && npm run build && vercel --prod
```

## 🤝 Contributing

We welcome contributions to improve the Pakistani Legal Assistant:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/legal-enhancement`)
3. Implement improvements following the structured response format
4. Test with various Pakistani legal scenarios
5. Submit a pull request with detailed description

### Development Guidelines

- Follow the mandatory 5-section response format for legal queries
- Ensure Pakistani legal context accuracy
- Test RAG system with various legal document types
- Maintain responsive design for mobile users
- Use semantic commit messages

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Google Gemini AI** for advanced language processing capabilities
- **Pakistani Legal Community** for guidance on legal accuracy
- **Vercel** for seamless deployment platform
- **Open Source Community** for excellent libraries and tools

## 📞 Support & Contact

For support, questions, or legal accuracy feedback:
- Create an issue on GitHub with detailed description
- Check the [system status endpoint](https://backend-phi-eight-99.vercel.app/api/system-status)
- Review comprehensive API documentation at `/docs`
- Contact Pakistan Bar Council: +92-51-9201681 for legal verification

---

**Built with ❤️ for the Pakistani legal community**

*Empowering citizens with accessible, accurate, and comprehensive legal knowledge through advanced AI technology and structured legal analysis*

## 🔄 Version History

- **v2.1.0** - Enhanced RAG system with structured responses and improved Pakistani legal analysis
- **v2.0.0** - Advanced UI with glassmorphism design and comprehensive legal coverage
- **v1.0.0** - Initial release with basic Pakistani legal assistance