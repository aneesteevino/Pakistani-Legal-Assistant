import React, { useState, useEffect } from 'react';
import { Message } from '../types';

interface TypingMessageProps {
  message: Message;
  onTypingComplete?: () => void;
}

const TypingMessage: React.FC<TypingMessageProps> = ({ message, onTypingComplete }) => {
  const [displayedText, setDisplayedText] = useState('');
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isTypingComplete, setIsTypingComplete] = useState(false);

  const typingSpeed = 15; // milliseconds per character (faster)

  useEffect(() => {
    if (message.type === 'user') {
      setDisplayedText(message.content);
      setIsTypingComplete(true);
      return;
    }

    if (currentIndex < message.content.length) {
      const timer = setTimeout(() => {
        setDisplayedText(message.content.slice(0, currentIndex + 1));
        setCurrentIndex(currentIndex + 1);
      }, typingSpeed);

      return () => clearTimeout(timer);
    } else if (!isTypingComplete) {
      setIsTypingComplete(true);
      onTypingComplete?.();
    }
  }, [currentIndex, message.content, message.type, isTypingComplete, onTypingComplete]);

  const getConfidenceBadge = (confidence: number) => {
    if (confidence >= 0.7) {
      return <span className="confidence-badge confidence-high">High Confidence</span>;
    } else if (confidence >= 0.4) {
      return <span className="confidence-badge confidence-medium">Medium Confidence</span>;
    } else {
      return <span className="confidence-badge confidence-low">Low Confidence</span>;
    }
  };

  return (
    <div className={`message ${message.type} animate-fadeInUp`}>
      <div className="message-avatar">
        {message.type === 'user' ? (
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
            <circle cx="12" cy="7" r="4"></circle>
          </svg>
        ) : (
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M12 2L2 7l10 5 10-5-10-5z"></path>
            <path d="M2 17l10 5 10-5"></path>
            <path d="M2 12l10 5 10-5"></path>
          </svg>
        )}
      </div>
      
      <div className="message-bubble">
        <div className="message-header">
          <span className="message-sender legal-text">
            {message.type === 'user' ? 'You' : 'Legal Assistant'}
          </span>
          <span className="message-time">
            {new Date(message.timestamp).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
          </span>
        </div>
        
        <div className="message-content legal-text">
          {displayedText}
          {message.type === 'assistant' && !isTypingComplete && (
            <span className="typing-cursor">|</span>
          )}
        </div>
        
        {message.type === 'assistant' && message.sources && message.sources.length > 0 && isTypingComplete && (
          <div className="sources glass">
            <h4 className="legal-heading">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" style={{marginRight: '0.5rem'}}>
                <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path>
                <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path>
              </svg>
              Legal Sources:
            </h4>
            <div className="sources-list">
              {message.sources.map((source, index) => (
                <div key={index} className="source-item glass">
                  <div className="source-header">
                    <div className="source-title legal-text">
                      {source.law_name}
                      {source.section && ` - ${source.section}`}
                    </div>
                    <div className="source-page">
                      Page {source.page || 'N/A'}
                    </div>
                  </div>
                  <div className="source-preview legal-text">
                    {source.content_preview}
                  </div>
                </div>
              ))}
            </div>
            {message.confidence !== undefined && (
              <div className="confidence-section">
                {getConfidenceBadge(message.confidence)}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default TypingMessage;