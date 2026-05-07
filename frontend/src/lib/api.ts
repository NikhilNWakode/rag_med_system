const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

export interface Source {
  source_number: number;
  title: string;
  authors: string;
  journal: string;
  year: number;
  pmid: string;
  doi: string;
  url: string;
}

export interface SearchResponse {
  query: string;
  answer: string;
  sources: Source[];
}

export interface ChatResponse {
  query: string;
  answer: string;
  sources: Source[];
  conversation_id: string;
}

export interface IngestResponse {
  message: string;
  documents_ingested: number;
  chunks_created: number;
}

export interface HealthResponse {
  status: string;
  ollama_connected: boolean;
  vector_store_ready: boolean;
  documents_count: number;
}

export async function searchQuery(
  query: string,
  topK: number = 5,
  yearFrom?: number,
  yearTo?: number
): Promise<SearchResponse> {
  const res = await fetch(`${API_BASE}/api/search`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      query,
      top_k: topK,
      year_from: yearFrom || null,
      year_to: yearTo || null,
    }),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function chatQuery(
  query: string,
  conversationId?: string,
  topK: number = 5
): Promise<ChatResponse> {
  const res = await fetch(`${API_BASE}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      query,
      conversation_id: conversationId || null,
      top_k: topK,
    }),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function ingestPapers(
  query: string,
  maxResults: number = 10
): Promise<IngestResponse> {
  const res = await fetch(`${API_BASE}/api/ingest`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query, max_results: maxResults }),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function healthCheck(): Promise<HealthResponse> {
  const res = await fetch(`${API_BASE}/api/health`);
  if (!res.ok) throw new Error("Health check failed");
  return res.json();
}

export interface Conversation {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
}

export interface ConversationMessages {
  conversation_id: string;
  messages: { role: string; content: string; sources: Source[] | null; created_at: string }[];
}

export async function getConversations(): Promise<Conversation[]> {
  const res = await fetch(`${API_BASE}/api/conversations`);
  if (!res.ok) throw new Error("Failed to load conversations");
  return res.json();
}

export async function getConversationMessages(id: string): Promise<ConversationMessages> {
  const res = await fetch(`${API_BASE}/api/conversations/${id}/messages`);
  if (!res.ok) throw new Error("Failed to load messages");
  return res.json();
}

export async function deleteConversation(id: string): Promise<void> {
  const res = await fetch(`${API_BASE}/api/conversations/${id}`, { method: "DELETE" });
  if (!res.ok) throw new Error("Failed to delete conversation");
}

export interface AuthResponse {
  token: string;
  user: { id: string; email: string; name: string };
}

export async function register(email: string, name: string, password: string): Promise<AuthResponse> {
  const res = await fetch(`${API_BASE}/api/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, name, password }),
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Registration failed");
  }
  return res.json();
}

export function getExportUrl(conversationId: string): string {
  return `${API_BASE}/api/conversations/${conversationId}/export`;
}

export async function login(email: string, password: string): Promise<AuthResponse> {
  const res = await fetch(`${API_BASE}/api/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Login failed");
  }
  return res.json();
}
