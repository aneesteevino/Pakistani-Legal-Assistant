import React, { useState, useEffect, useRef, useMemo, useCallback } from 'react';
import TypingMessage from './components/TypingMessage';
import ChatInput from './components/ChatInput';
import Sidebar from './components/Sidebar';
import { Message, Chat, ApiStats } from './types';
import { apiService, isModificationRequest } from './services/api';
import './index.css';

const SAMPLE_QUESTIONS = [
  "What are the penalties for cybercrime under PECA 2016?",
  "Explain the procedure for filing an FIR under CrPC",
  "What constitutes fraud under PPC Section 420?",
  "What are the fundamental rights guaranteed by Pakistan's Constitution?",
  "How to register a marriage under Pakistani family laws?",
  "What is the procedure for property transfer in Pakistan?",
  "What are the rights of an accused person during police investigation?",
  "How to file for divorce under Pakistani family laws?",
  "What is the punishment for theft under Pakistani Penal Code?",
  "What are the grounds for bail in criminal cases?",
  "How to challenge a government decision in Pakistani courts?",
  "What are the inheritance laws for Muslims in Pakistan?"
];

function App() {
  const [chats, setChats] = useState<Chat[]>([]);
  const [currentChatId, setCurrentChatId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [stats, setStats] = useState<ApiStats | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const currentChat = chats.find(chat => chat.id === currentChatId);
  const messages = useMemo(() => currentChat?.messages || [], [currentChat?.messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    loadStats();
    loadChatsFromStorage();
  }, []);

  const saveChatsToStorage = useCallback(() => {
    localStorage.setItem('legal-assistant-chats', JSON.stringify(chats));
  }, [chats]);

  useEffect(() => {
    saveChatsToStorage();
  }, [saveChatsToStorage]);

  const loadStats = async () => {
    try {
      const statsData = await apiService.getStats();
      setStats(statsData);
    } catch (error) {
      console.error('Failed to load stats:', error);
    }
  };

  const loadChatsFromStorage = () => {
    const savedChats = localStorage.getItem('legal-assistant-chats');
    if (savedChats) {
      const parsedChats = JSON.parse(savedChats).map((chat: any) => ({
        ...chat,
        createdAt: new Date(chat.createdAt),
        updatedAt: new Date(chat.updatedAt),
        messages: chat.messages.map((msg: any) => ({
          ...msg,
          timestamp: new Date(msg.timestamp)
        }))
      }));
      setChats(parsedChats);
      if (parsedChats.length > 0) {
        setCurrentChatId(parsedChats[0].id);
      }
    }
  };

  const generateChatTitle = (firstMessage: string): string => {
    // Clean and truncate the message for title
    const cleanMessage = firstMessage.replace(/[^a-zA-Z0-9\s]/g, '').trim();
    const words = cleanMessage.split(' ').slice(0, 6);
    return words.join(' ') + (cleanMessage.split(' ').length > 6 ? '...' : '');
  };

  const createNewChat = (): string => {
    const newChat: Chat = {
      id: Date.now().toString(),
      title: 'New Chat',
      messages: [],
      createdAt: new Date(),
      updatedAt: new Date()
    };

    setChats(prev => [newChat, ...prev]);
    setCurrentChatId(newChat.id);
    setIsMobileMenuOpen(false); // Close mobile menu when creating new chat
    return newChat.id;
  };

  const updateChatTitle = (chatId: string, firstMessage: string) => {
    setChats(prev => prev.map(chat =>
      chat.id === chatId
        ? { ...chat, title: generateChatTitle(firstMessage), updatedAt: new Date() }
        : chat
    ));
  };

  const addMessageToChat = (chatId: string, message: Message) => {
    setChats(prev => prev.map(chat =>
      chat.id === chatId
        ? {
          ...chat,
          messages: [...chat.messages, message],
          updatedAt: new Date()
        }
        : chat
    ));
  };

  const handleNewChat = () => {
    createNewChat();
  };

  const handleSelectChat = (chatId: string) => {
    setCurrentChatId(chatId);
    setIsMobileMenuOpen(false); // Close mobile menu when selecting chat
  };

  const handleDeleteChat = (chatId: string) => {
    setChats(prev => prev.filter(chat => chat.id !== chatId));
    if (currentChatId === chatId) {
      const remainingChats = chats.filter(chat => chat.id !== chatId);
      setCurrentChatId(remainingChats.length > 0 ? remainingChats[0].id : null);
    }
  };

  const handleSendMessage = async (question: string) => {
    let chatId = currentChatId;

    // Create new chat if none exists
    if (!chatId) {
      chatId = createNewChat();
    }

    // For continuation and modification requests, don't add a user message
    const isContinuation = question.toLowerCase() === 'continue';
    const isModification = isModificationRequest(question);

    if (!isContinuation && !isModification) {
      const userMessage: Message = {
        id: Date.now().toString(),
        type: 'user',
        content: question,
        timestamp: new Date(),
      };

      addMessageToChat(chatId, userMessage);

      // Update chat title if this is the first user message
      const currentChatData = chats.find(c => c.id === chatId);
      const userMessages = currentChatData?.messages.filter(m => m.type === 'user') || [];

      if (userMessages.length === 0) {
        updateChatTitle(chatId, question);
      }
    }

    setIsLoading(true);
    setError(null);

    try {
      const response = await apiService.askQuestion(question);

      if (isContinuation || isModification) {
        // For continuation/modification, update the last assistant message
        const currentChatData = chats.find(c => c.id === chatId);
        const lastMessage = currentChatData?.messages[currentChatData.messages.length - 1];

        if (lastMessage && lastMessage.type === 'assistant') {
          // Update the existing message with continued/modified content
          setChats(prev => prev.map(chat =>
            chat.id === chatId
              ? {
                ...chat,
                messages: chat.messages.map((msg, index) =>
                  index === chat.messages.length - 1 && msg.type === 'assistant'
                    ? { ...msg, content: response.answer, timestamp: new Date() }
                    : msg
                ),
                updatedAt: new Date()
              }
              : chat
          ));
        } else {
          // Fallback: add as new message if no assistant message found
          const assistantMessage: Message = {
            id: (Date.now() + 1).toString(),
            type: 'assistant',
            content: response.answer,
            sources: response.sources,
            confidence: response.confidence,
            follow_up_questions: response.follow_up_questions,
            timestamp: new Date(),
          };
          addMessageToChat(chatId, assistantMessage);
        }
      } else {
        // Regular new message
        const assistantMessage: Message = {
          id: (Date.now() + 1).toString(),
          type: 'assistant',
          content: response.answer,
          sources: response.sources,
          confidence: response.confidence,
          follow_up_questions: response.follow_up_questions,
          timestamp: new Date(),
        };

        addMessageToChat(chatId, assistantMessage);
      }
    } catch (error: any) {
      console.error('Error asking question:', error);

      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: 'I apologize, but I encountered an error while processing your question. Please check if the backend server is running and try again.',
        timestamp: new Date(),
      };

      addMessageToChat(chatId, errorMessage);
      setError(error.message || 'An error occurred');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSampleQuestion = (question: string) => {
    if (!isLoading) {
      handleSendMessage(question);
    }
  };

  const toggleMobileMenu = () => {
    setIsMobileMenuOpen(!isMobileMenuOpen);
  };

  const closeMobileMenu = () => {
    setIsMobileMenuOpen(false);
  };

  return (
    <div className="app-container">
      {/* Mobile Menu Toggle */}
      <button className="mobile-menu-toggle" onClick={toggleMobileMenu}>
        ☰
      </button>

      {/* Mobile Overlay */}
      <div
        className={`mobile-overlay ${isMobileMenuOpen ? 'open' : ''}`}
        onClick={closeMobileMenu}
      />

      <Sidebar
        chats={chats}
        currentChatId={currentChatId}
        onSelectChat={handleSelectChat}
        onNewChat={handleNewChat}
        onDeleteChat={handleDeleteChat}
        isOpen={isMobileMenuOpen}
      />

      <div className="main-content">
        <header className="main-header">
          <div className="header-left">
            <div className="header-logo">
              <div className="logo-icon">⚖</div>
              <div className="header-info">
                <h1>Pakistani Legal Assistant</h1>
                <p>AI-powered legal analysis</p>
              </div>
            </div>
          </div>

          <div className="header-right">
            {stats && (
              <div className="stats-card">
                <div className="stat-item">
                  <span className="stat-number">{stats.total_chunks.toLocaleString()}</span>
                  <span className="stat-label">Docs</span>
                </div>
                <div className="stat-divider"></div>
                <div className="stat-item">
                  <span className="stat-number">{stats.unique_laws}</span>
                  <span className="stat-label">Laws</span>
                </div>
                <div className="stat-divider"></div>
                <div className="stat-item">
                  <span className="stat-status">{stats.status}</span>
                  <span className="stat-label">Status</span>
                </div>
              </div>
            )}

            <div className="header-actions">
              <button className="header-btn">
                <div className="status-dot"></div>
                Online
              </button>
            </div>
          </div>
        </header>

        <div className="chat-container">
          <div className="messages-container">
            {messages.length === 0 ? (
              <div className="empty-state">
                <div className="welcome-icon">⚖️</div>
                <h3>What's on your legal agenda today?</h3>
                <p>Ask me any question about Pakistani law and I'll help you find relevant information from legal documents.</p>

                <div className="sample-questions">
                  <h4>💡 Try asking:</h4>
                  {SAMPLE_QUESTIONS.map((question, index) => (
                    <div
                      key={index}
                      className="sample-question"
                      onClick={() => handleSampleQuestion(question)}
                    >
                      {question}
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <>
                {messages.map((message) => (
                  <TypingMessage
                    key={message.id}
                    message={message}
                    onContinueRequest={handleSendMessage}
                  />
                ))}
                {isLoading && (
                  <div className="loading">
                    <div className="loading-spinner">🤔</div>
                    Analyzing legal documents...
                  </div>
                )}
              </>
            )}
            <div ref={messagesEndRef} />
          </div>

          <ChatInput
            onSendMessage={handleSendMessage}
            isLoading={isLoading}
          />
        </div>

        {error && (
          <div className="error-card">
            ⚠️ {error}
          </div>
        )}
      </div>
    </div>
  );
}

export default App;