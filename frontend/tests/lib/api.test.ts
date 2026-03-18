import { describe, it, expect, vi, beforeEach } from "vitest";

const mockFetch = vi.fn();
global.fetch = mockFetch;

// Import the singleton after mocking fetch
const { api } = await import("@/lib/api");

describe("ApiClient", () => {
  beforeEach(() => {
    mockFetch.mockReset();
  });

  it("sends query request to correct endpoint", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () =>
        Promise.resolve({
          id: "1",
          question: "test",
          answer: "response",
          timestamp: new Date().toISOString(),
          model: "claude-haiku-4-5-20251001",
        }),
    });

    const result = await api.query("test");
    expect(mockFetch).toHaveBeenCalledWith(
      expect.stringContaining("/api/query"),
      expect.objectContaining({
        method: "POST",
      })
    );
    expect(result.answer).toBe("response");
  });

  it("fetches history with pagination params", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () =>
        Promise.resolve({ conversations: [], total: 0, limit: 10, offset: 5 }),
    });

    await api.getHistory(10, 5);
    expect(mockFetch).toHaveBeenCalledWith(
      expect.stringContaining("/api/history?limit=10&offset=5")
    );
  });

  it("throws on non-ok response", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: false,
      json: () => Promise.resolve({ error: "Bad request" }),
    });

    await expect(api.query("test")).rejects.toThrow();
  });

  it("calls health check endpoint", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ status: "healthy" }),
    });

    await api.healthCheck();
    expect(mockFetch).toHaveBeenCalledWith(
      expect.stringContaining("/api/health")
    );
  });
});