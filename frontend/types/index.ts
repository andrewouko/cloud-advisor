export interface QueryRequest {
  question: string;
}

export interface QueryResponse {
  id: string;
  question: string;
  answer: string;
  timestamp: string;
  model: string;
  tokens_used: number | null;
}

export interface HistoryItem {
  id: string;
  question: string;
  answer: string;
  timestamp: string;
}

export interface HistoryResponse {
  conversations: HistoryItem[];
  total: number;
  limit: number;
  offset: number;
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: string;
  isLoading?: boolean;
  isError?: boolean;
}

export interface APIError {
  error: string;
  type: string;
}
