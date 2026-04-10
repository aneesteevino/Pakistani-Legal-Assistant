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
    <div className={`sidebar ${isOpen ? 'open' : ''}`}>
      <div className="sidebar-header">
        <button className="new-chat-btn" onClick={onNewChat}>
          <span className="btn-icon">+</span>
          New chat
        </button>
      </div>

      <div className="chat-list">
        <div className="chat-list-header">
          <h3>Recent</h3>
          <span className="chat-count">{chats.length}</span>
        </div>
        
        <div className="chat-items">
          {chats.length === 0 ? (
            <div className="empty-chats">
              <p>No conversations yet</p>
              <span>Start a new chat to begin</span>
            </div>
          ) : (
            chats.map((chat) => (
              <div
                key={chat.id}
                className={`chat-item ${currentChatId === chat.id ? 'active' : ''}`}
                onClick={() => onSelectChat(chat.id)}
              >
                <div className="chat-item-content">
                  <div className="chat-title">
                    {truncateTitle(chat.title)}
                  </div>
                  <div className="chat-meta">
                    <span className="chat-date">{formatDate(chat.updatedAt)}</span>
                    <span className="message-count">{chat.messages.length}</span>
                  </div>
                </div>
                
                <button
                  className="delete-chat-btn"
                  onClick={(e) => {
                    e.stopPropagation();
                    onDeleteChat(chat.id);
                  }}
                  title="Delete chat"
                >
                  🗑️
                </button>
              </div>
            ))
          )}
        </div>
      </div>

      <div className="sidebar-footer">
        <div className="system-info">
          <div className="info-item">
            <span className="info-label">Status</span>
            <span className="status-indicator active">Online</span>
          </div>
          <div className="info-item">
            <span className="info-label">Version</span>
            <span className="version">v1.0.0</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Sidebar;