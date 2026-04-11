# ⚖️ Pakistani Legal Assistant

A sophisticated AI-powered legal assistant with modern glassmorphism UI, designed to help users navigate Pakistani law with comprehensive, well-researched answers.

![Pakistani Legal Assistant](https://img.shields.io/badge/Status-Live-brightgreen)
![React](https://img.shields.io/badge/React-18.x-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Latest-green)
![TypeScript](https://img.shields.io/badge/TypeScript-5.x-blue)
![Gemini AI](https://img.shields.io/badge/Gemini-AI-orange)

## ✨ Features

### 🎨 Modern UI Design
- **Dark Theme**: Sophisticated color palette with legal gold accents
- **Glassmorphism Effects**: Backdrop blur and transparency for modern aesthetics
- **Skeumorphism Elements**: Realistic shadows and depth for tactile experience
- **Legal Typography**: Playfair Display and Inter fonts for professional appearance
- **Responsive Design**: Optimized for desktop, tablet, and mobile devices

### 🤖 AI-Powered Legal Analysis
- **Comprehensive Responses**: Detailed explanations with legal citations
- **Follow-up Questions**: AI suggests related queries for deeper exploration
- **Source Citations**: References to specific legal documents and sections
- **Confidence Scoring**: Transparency about response reliability
- **Interactive Samples**: Pre-built questions to get users started

### 💬 Chat Experience
- **Real-time Typing**: Animated response generation
- **Chat History**: Persistent conversation storage
- **Multiple Conversations**: Organize different legal topics
- **Mobile Optimized**: Touch-friendly interface for mobile users

## 🚀 Live Demo

- **Frontend**: [https://pakistani-legal-assistant.vercel.app](https://pakistani-legal-assistant.vercel.app)
- **Backend API**: [https://backend-phi-eight-99.vercel.app](https://backend-phi-eight-99.vercel.app)
- **API Docs**: [https://backend-phi-eight-99.vercel.app/docs](https://backend-phi-eight-99.vercel.app/docs)

## 🛠️ Tech Stack

### Frontend
- **React 18** with TypeScript
- **Modern CSS** with CSS Variables
- **Responsive Design** with mobile-first approach
- **Local Storage** for chat persistence

### Backend
- **FastAPI** with automatic documentation
- **Google Gemini AI** for legal analysis
- **Python 3.13** with async support
- **Pydantic** for data validation

### Deployment
- **Vercel** for both frontend and backend
- **Environment Variables** for secure configuration
- **CORS** configured for cross-origin requests

## 📦 Installation

### Prerequisites
- Node.js 18+ and npm
- Python 3.13+
- Gemini API key

### Backend Setup

```bash
# Clone repository
git clone https://github.com/yourusername/pakistani-legal-assistant.git
cd pakistani-legal-assistant

# Setup backend
cd backend
pip install -r requirements.txt

# Create .env file
echo "GEMINI_API_KEY=your_api_key_here" > .env

# Run backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

```bash
# Setup frontend (in new terminal)
cd frontend
npm install

# Run frontend
npm start
```

Visit `http://localhost:3000` to see the application.

## 🎯 Usage Examples

### Sample Legal Questions

1. **Constitutional Law**
   - "What are the fundamental rights in Pakistan's constitution?"
   - "Explain the structure of Pakistan's judicial system"

2. **Criminal Law**
   - "What are the penalties for cybercrime under PECA?"
   - "Explain the procedure for filing an FIR under CrPC"

3. **Civil Law**
   - "What constitutes fraud under PPC Section 420?"
   - "What are the grounds for divorce under Pakistani law?"

### API Usage

```bash
# Ask a legal question
curl -X POST http://localhost:8000/api/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What are the basic rights of citizens in Pakistan?"}'

# Get system statistics
curl http://localhost:8000/api/stats
```

## 🎨 UI Components

### Design System
- **Colors**: Dark theme with legal gold accents (#d4af37)
- **Typography**: Playfair Display for headings, Inter for body text
- **Effects**: Glassmorphism with backdrop-filter blur
- **Animations**: Smooth transitions and hover effects

### Key Components
- **Sidebar**: Chat history with glassmorphism design
- **Message Bubbles**: Enhanced with avatars and timestamps
- **Input Field**: Skeumorphic design with send button
- **Sample Questions**: Interactive cards with hover effects

## 🔧 Configuration

### Environment Variables

#### Backend (.env)
```env
GEMINI_API_KEY=your_gemini_api_key
```

#### Frontend (.env.production)
```env
REACT_APP_API_URL=https://your-backend.vercel.app
```

### Customization

The UI can be customized by modifying CSS variables in `frontend/src/index.css`:

```css
:root {
  --accent-gold: #d4af37;
  --bg-primary: #0a0a0f;
  --text-primary: #ffffff;
  /* ... more variables */
}
```

## 📚 API Documentation

### Endpoints

- `GET /` - Health check
- `GET /api/health` - Detailed health status
- `GET /api/stats` - System statistics
- `POST /api/ask` - Ask legal question
- `POST /api/search` - Search legal documents

### Response Format

```json
{
  "answer": "Detailed legal explanation...",
  "sources": [
    {
      "law_name": "Constitution of Pakistan",
      "section": "Article 25",
      "content_preview": "All citizens are equal...",
      "page": 15
    }
  ],
  "confidence": 0.85
}
```

## 🚀 Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions.

### Quick Deploy

```bash
# Deploy backend
cd backend && vercel --prod

# Deploy frontend
cd frontend && npm run build && vercel --prod
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow TypeScript best practices
- Use semantic commit messages
- Ensure responsive design
- Test on multiple devices
- Maintain glassmorphism design consistency

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Google Gemini AI** for powerful language processing
- **Vercel** for seamless deployment platform
- **React Community** for excellent documentation
- **FastAPI** for intuitive API development

## 📞 Support

For support and questions:
- Create an issue on GitHub
- Check the [deployment guide](DEPLOYMENT.md)
- Review API documentation at `/docs` endpoint

---

**Built with ❤️ for the Pakistani legal community**

*Empowering citizens with accessible legal knowledge through modern AI technology*