import axios from 'axios';
import { QueryResponse, ApiStats } from '../types';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000, // Increased timeout for Vercel
  headers: {
    'Content-Type': 'application/json',
  },
});

// Helper function to detect continuation requests
export const isContinuationRequest = (message: string): boolean => {
  const continuationKeywords = ['continue', 'complete', 'go on', 'finish', 'more', 'keep going'];
  return continuationKeywords.some(keyword => 
    message.toLowerCase().includes(keyword.toLowerCase())
  );
};

// Helper function to detect modification requests
export const isModificationRequest = (message: string): boolean => {
  const modificationPatterns = [
    'short this', 'shorten this', 'make it short', 'make this brief',
    'summarize this', 'brief version', 'concise version',
    'make it precise', 'be more precise', 'more specific',
    'simplify this', 'make it simple', 'explain simply', 'make it easy',
    'bullet points', 'list format', 'numbered list', 'in points',
    'rephrase this', 'rewrite this', 'different way', 'another way'
  ];
  const messageLower = message.toLowerCase().trim();
  return modificationPatterns.some(pattern => messageLower.includes(pattern));
};

// Helper function to detect incomplete responses
export const isResponseIncomplete = (response: string): boolean => {
  return response.includes('*Response may be incomplete') || 
         response.includes('Type \'continue\'') ||
         response.endsWith('...') ||
         response.endsWith(',');
};

export const apiService = {
  async askQuestion(question: string): Promise<QueryResponse> {
    const response = await api.post('/api/ask', { question });
    return response.data;
  },

  async getStats(): Promise<ApiStats> {
    const response = await api.get('/api/stats');
    return response.data;
  },

  async getSystemStatus(): Promise<any> {
    const response = await api.get('/api/system-status');
    return response.data;
  },

  async healthCheck(): Promise<any> {
    const response = await api.get('/api/health');
    return response.data;
  },

  async searchDocuments(question: string): Promise<any> {
    const response = await api.post('/api/search', { question });
    return response.data;
  },
};

export default apiService;