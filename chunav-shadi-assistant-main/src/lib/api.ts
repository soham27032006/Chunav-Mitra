export type Lang = "hi" | "en";
export type IntentType = "voter_check" | "booth_finder" | "timeline" | "explain" | "general";

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
  intent?: IntentType;
}

export interface AskResponse {
  response: string;
  detected_lang: Lang;
  intent: IntentType;
  session_id: string;
}

export interface VoterCheckResponse {
  found: boolean;
  message: string;
  voter_id?: string;
}

export interface BoothResponse {
  booth_name: string;
  address: string;
  distance: string;
  maps_link: string;
  message: string;
}

export interface TimelinePhase {
  phase: number;
  name: string;
  date: string;
  description: string;
}

export interface TimelineResponse {
  current_phase: string;
  phases: TimelinePhase[];
  next_deadline: string;
  days_remaining: number;
}

export interface ExplainResponse {
  topic: string;
  shaadi_analogy: string;
  simple_explanation: string;
  action_step: string;
  fun_fact: string;
  lang: Lang;
}

export interface StatsResponse {
  total_queries: number;
  top_intents: Record<string, number>;
  languages_used: Record<string, number>;
  queries_today: number;
  most_asked_intent: string;
}

const BASE_URL =
  (import.meta as unknown as { env: Record<string, string | undefined> }).env
    ?.VITE_API_BASE_URL || "http://localhost:8000";

async function jsonFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    ...init,
    headers: { "Content-Type": "application/json", ...(init?.headers || {}) },
  });
  if (!res.ok) throw new Error(`Request failed: ${res.status}`);
  return res.json() as Promise<T>;
}

export const api = {
  ask: (query: string, session_id?: string, lang?: Lang) =>
    jsonFetch<AskResponse>("/api/ask", {
      method: "POST",
      body: JSON.stringify({ query, session_id, lang }),
    }),

  streamAskUrl: (query: string, session_id?: string) => {
    const params = new URLSearchParams({ query });
    if (session_id) params.set("session_id", session_id);
    return `${BASE_URL}/api/ask/stream?${params.toString()}`;
  },

  checkVoter: (data: { name: string; state: string; dob: string }) =>
    jsonFetch<VoterCheckResponse>("/api/check-voter", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  findBooth: (data: { pincode?: string; lat?: number; lng?: number }) =>
    jsonFetch<BoothResponse>("/api/find-booth", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  timeline: () => jsonFetch<TimelineResponse>("/api/timeline"),

  explain: (topic: string, lang: Lang = "en") =>
    jsonFetch<ExplainResponse>("/api/explain", {
      method: "POST",
      body: JSON.stringify({ topic, lang }),
    }),

  stats: () => jsonFetch<StatsResponse>("/api/stats"),
};
