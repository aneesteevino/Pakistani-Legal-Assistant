import React from 'react';
import { Chat } from '../types';

interface SidebarProps {
  chats: Chat[];
  currentChatId: string | null;
  onSelectChat: (chatId: string) => void;
  onNewChat: () => void;
  onDeleteChat: (chatId: string) => void;
  isOpen?: boolean;
}

const Sidebar: React.FC<SidebarProps> = ({ 
  chats, 
  currentChatId, 
  onSelectChat, 
  onNewChat, 
  onDeleteChat,
  isOpen = false
}) => {
  const formatDate = (date: Date) => {
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));
    
    if (days === 0) return 'Today';
    if (days === 1) return 'Yesterday';
    if (days < 7) return `${days} days ago`;
    return date.toLocaleDateString();
  };

  const truncateTitle = (title: string, maxLength: number = 30) => {
    return title.length > maxLength ? title.substring(0, maxLength) + '...' : title;
  };

  return (
    <div className={`sidebar glass ${isOpen ? 'open' : ''}`}>
      <div className="sidebar-header">
        <button className="new-chat-btn skeu-button" onClick={onNewChat}>
          <span className="btn-icon">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <line x1="12" y1="5" x2="12" y2="19"></line>
              <line x1="5" y1="12" x2="19" y2="12"></line>
            </svg>
          </span>
          New Legal Consultation
        </button>
      </div>

      <div className="chat-list">
        <div className="chat-list-header">
          <h3 className="legal-heading">Recent Consultations</h3>
          <span className="chat-count">{chats.length}</span>
        </div>
        
        <div className="chat-items">
          {chats.length === 0 ? (
            <div className="empty-chats">
              <div className="empty-icon">⚖️</div>
              <p className="legal-text">No consultations yet</p>
              <span>Start a new legal consultation to begin</span>
            </div>
          ) : (
            chats.map((chat) => (
              <div
                key={chat.id}
                className={`chat-item glass ${currentChatId === chat.id ? 'active' : ''}`}
                onClick={() => onSelectChat(chat.id)}
              >
                <div className="chat-icon">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                    <polyline points="14,2 14,8 20,8"></polyline>
                    <line x1="16" y1="13" x2="8" y2="13"></line>
                    <line x1="16" y1="17" x2="8" y2="17"></line>
                    <polyline points="10,9 9,9 8,9"></polyline>
                  </svg>
                </div>
                
                <div className="chat-item-content">
                  <div className="chat-title legal-text">
                    {truncateTitle(chat.title)}
                  </div>
                  <div className="chat-meta">
                    <span className="chat-date">{formatDate(chat.updatedAt)}</span>
                    <span className="message-count">{chat.messages.length} msgs</span>
                  </div>
                </div>
                
                <button
                  className="delete-chat-btn skeu-button"
                  onClick={(e) => {
                    e.stopPropagation();
                    onDeleteChat(chat.id);
                  }}
                  title="Delete consultation"
                >
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <polyline points="3,6 5,6 21,6"></polyline>
                    <path d="m19,6v14a2,2 0 0,1 -2,2H7a2,2 0 0,1 -2,-2V6m3,0V4a2,2 0 0,1 2,-2h4a2,2 0 0,1 2,2v2"></path>
                  </svg>
                </button>
              </div>
            ))
          )}
        </div>
      </div>

      <div className="sidebar-footer glass">
        <div className="system-info">
          <div className="info-item">
            <span className="info-label">Legal Database</span>
            <span className="status-indicator active">Active</span>
          </div>
          <div className="info-item">
            <span className="info-label">AI Assistant</span>
            <span className="version">v2.0.0</span>
          </div>
          <div className="info-item">
            <span className="info-label">Pakistani Law</span>
            <span className="status-indicator active">Updated</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Sidebar;