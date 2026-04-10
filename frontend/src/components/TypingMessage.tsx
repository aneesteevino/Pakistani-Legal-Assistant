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
    <div className={`message ${message.type}`}>
      <div className="message-avatar">
        {message.type === 'user' ? 'U' : '⚖'}
      </div>
      
      <div className="message-bubble">
        <div className="message-content">
          {displayedText}
          {message.type === 'assistant' && !isTypingComplete && (
            <span className="typing-cursor">|</span>
          )}
        </div>
        
        {message.type === 'assistant' && message.sources && message.sources.length > 0 && isTypingComplete && (
          <div className="sources">
            <h4>📚 Sources:</h4>
            {message.sources.map((source, index) => (
              <div key={index} className="source-item">
                <div className="source-title">
                  {source.law_name}
                  {source.section && ` - ${source.section}`}
                </div>
                <div className="source-preview">
                  {source.content_preview}
                </div>
              </div>
            ))}
            {message.confidence !== undefined && getConfidenceBadge(message.confidence)}
          </div>
        )}
      </div>
    </div>
  );
};

export default TypingMessage;