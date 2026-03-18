import type { QueryResponse, HistoryResponse } from "@/types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  async query(question: string): Promise<QueryResponse> {
    const response = await fetch(`${this.baseUrl}/api/query`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question }),
    });

    if (!response.ok) {
      const body = await response.json().catch(() => null);
      throw new Error(body?.error || `Request failed (${response.status})`);
    }

    return response.json();
  }

  async getHistory(limit = 50, offset = 0): Promise<HistoryResponse> {
    const params = new URLSearchParams({
      limit: String(limit),
      offset: String(offset),
    });

    const response = await fetch(`${this.baseUrl}/api/history?${params}`);

    if (!response.ok) {
      throw new Error("Failed to fetch history");
    }

    return response.json();
  }

  async clearHistory(): Promise<void> {
    const response = await fetch(`${this.baseUrl}/api/history`, {
      method: "DELETE",
    });

    if (!response.ok) {
      throw new Error("Failed to clear history");
    }
  }

  async healthCheck(): Promise<{ status: string }> {
    const response = await fetch(`${this.baseUrl}/api/health`);
    return response.json();
  }
}

export const api = new ApiClient(API_BASE);
