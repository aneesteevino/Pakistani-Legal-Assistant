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

export const apiService = {
  async askQuestion(question: string): Promise<QueryResponse> {
    const response = await api.post('/api/ask', { question });
    return response.data;
  },

  async getStats(): Promise<ApiStats> {
    const response = await api.get('/api/stats');
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