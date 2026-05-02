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
  lat?: number;
  lng?: number;
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

export interface TranscribeResponse {
  text: string;
  lang: Lang;
}

export interface TranslateResponse {
  texts: string[];
  target_lang: Lang;
}

const BASE_URL =
  (import.meta as unknown as { env: Record<string, string | undefined> }).env
    ?.VITE_API_BASE_URL || "http://localhost:8000";

const pendingRequests = new Map<string, Promise<unknown>>();

function makeRequestKey(path: string, init?: RequestInit): string {
  return JSON.stringify({
    path,
    method: init?.method ?? "GET",
    body: typeof init?.body === "string" ? init.body : null,
  });
}

async function fetchWithTimeout(
  url: string,
  options: RequestInit,
  timeout = 10000,
): Promise<Response> {
  const controller = new AbortController();
  const timeoutId = window.setTimeout(() => controller.abort(), timeout);
  try {
    return await fetch(url, {
      ...options,
      signal: controller.signal,
    });
  } finally {
    window.clearTimeout(timeoutId);
  }
}

async function fetchWithRetry(
  url: string,
  options: RequestInit,
  retries = 2,
): Promise<Response> {
  let lastError: unknown;
  for (let attempt = 0; attempt <= retries; attempt += 1) {
    try {
      return await fetchWithTimeout(url, options);
    } catch (error) {
      lastError = error;
      if (attempt === retries) {
        break;
      }
    }
  }
  throw lastError instanceof Error ? lastError : new Error("Network request failed");
}

async function jsonFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const requestKey = makeRequestKey(path, init);
  const existing = pendingRequests.get(requestKey);
  if (existing) {
    return existing as Promise<T>;
  }

  const requestPromise = (async () => {
    const response = await fetchWithRetry(`${BASE_URL}${path}`, {
      ...init,
      headers: { "Content-Type": "application/json", ...(init?.headers || {}) },
    });
    if (!response.ok) {
      throw new Error(`Request failed: ${response.status}`);
    }
    return (await response.json()) as T;
  })();

  pendingRequests.set(requestKey, requestPromise);
  try {
    return await requestPromise;
  } finally {
    pendingRequests.delete(requestKey);
  }
}

export const api = {
  ask: (query: string, session_id?: string, lang?: Lang) =>
    jsonFetch<AskResponse>("/api/ask", {
      method: "POST",
      body: JSON.stringify({ query, session_id, lang }),
    }),

  streamAskUrl: (query: string, session_id?: string, lang?: Lang) => {
    const params = new URLSearchParams({ query });
    if (session_id) params.set("session_id", session_id);
    if (lang) params.set("lang", lang);
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

  transcribe: async (audio: Blob, lang: Lang) => {
    const form = new FormData();
    form.append("audio", audio, "voice-input.webm");
    form.append("lang", lang);
    const response = await fetchWithRetry(`${BASE_URL}/api/transcribe`, {
      method: "POST",
      body: form,
    });
    if (!response.ok) {
      throw new Error(`Request failed: ${response.status}`);
    }
    return (await response.json()) as TranscribeResponse;
  },

  translateBatch: (texts: string[], target_lang: Lang) =>
    jsonFetch<TranslateResponse>("/api/translate", {
      method: "POST",
      body: JSON.stringify({ texts, target_lang }),
    }),

  stats: () => jsonFetch<StatsResponse>("/api/stats"),
};
