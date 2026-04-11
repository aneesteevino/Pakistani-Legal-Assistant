export interface Source {
  law_name: string;
  section: string;
  content_preview: string;
  page: number;
  relevance_score: number;
}

export interface QueryResponse {
  answer: string;
  sources: Source[];
  confidence: number;
  follow_up_questions: string[];
}

export interface Message {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  sources?: Source[];
  confidence?: number;
  follow_up_questions?: string[];
  timestamp: Date;
}

export interface Chat {
  id: string;
  title: string;
  messages: Message[];
  createdAt: Date;
  updatedAt: Date;
}

export interface ApiStats {
  total_chunks: number;
  unique_laws: number;
  status: string;
  rag_enabled?: boolean;
  knowledge_base_size?: number;
}