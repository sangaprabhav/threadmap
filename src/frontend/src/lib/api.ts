/**
 * ThreadMap API client — typed fetch wrapper for the intelligence API.
 */

const API_BASE = "/api/v1";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...options?.headers },
    ...options,
  });
  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(error.detail || `API error: ${res.status}`);
  }
  return res.json();
}

// Content
export const getStream = (limit = 50, platform?: string) =>
  request<ContentItem[]>(
    `/content/stream?limit=${limit}${platform ? `&platform=${platform}` : ""}`
  );

export const searchContent = (params: ContentSearchParams) =>
  request<PaginatedResponse<ContentItem>>("/content/search", {
    method: "POST",
    body: JSON.stringify(params),
  });

export const getContentStats = () => request<ContentStats>("/content/stats");

// Alerts
export const getAlerts = (params?: AlertParams) => {
  const qs = new URLSearchParams();
  if (params?.status) qs.set("status", params.status);
  if (params?.priority) qs.set("priority", params.priority);
  qs.set("offset", String(params?.offset ?? 0));
  qs.set("limit", String(params?.limit ?? 50));
  return request<PaginatedResponse<Alert>>(`/alerts?${qs}`);
};

export const triageAlert = (id: string, data: TriageRequest) =>
  request<Alert>(`/alerts/${id}/triage`, {
    method: "POST",
    body: JSON.stringify(data),
  });

export const getAlertStats = () => request<AlertStats>("/alerts/stats");

// Cases
export const getCases = (params?: CaseParams) => {
  const qs = new URLSearchParams();
  if (params?.status) qs.set("status", params.status);
  qs.set("offset", String(params?.offset ?? 0));
  qs.set("limit", String(params?.limit ?? 50));
  return request<PaginatedResponse<Case>>(`/cases?${qs}`);
};

export const createCase = (data: CreateCaseRequest) =>
  request<Case>("/cases", { method: "POST", body: JSON.stringify(data) });

export const updateCase = (id: string, data: UpdateCaseRequest) =>
  request<Case>(`/cases/${id}`, { method: "PATCH", body: JSON.stringify(data) });

export const addCaseNote = (id: string, data: CaseNoteRequest) =>
  request<Case>(`/cases/${id}/notes`, {
    method: "POST",
    body: JSON.stringify(data),
  });

// Watchlists
export const getWatchlists = () =>
  request<PaginatedResponse<Watchlist>>("/watchlists");

export const createWatchlist = (data: CreateWatchlistRequest) =>
  request<Watchlist>("/watchlists", {
    method: "POST",
    body: JSON.stringify(data),
  });

export const addWatchlistEntry = (id: string, data: WatchlistEntryRequest) =>
  request<WatchlistEntry>(`/watchlists/${id}/entries`, {
    method: "POST",
    body: JSON.stringify(data),
  });

// Briefs
export const getDailyBrief = (hours = 24) =>
  request<DailyBrief>(`/briefs/daily?hours=${hours}`);

// Ingest
export const ingestUrl = (data: IngestUrlRequest) =>
  request<IngestResponse>("/ingest/url", {
    method: "POST",
    body: JSON.stringify(data),
  });

export const ingestText = (data: IngestTextRequest) =>
  request<IngestResponse>("/ingest/text", {
    method: "POST",
    body: JSON.stringify(data),
  });

// Health
export const getHealth = () => request<HealthResponse>("/health");

// Types
export interface ContentItem {
  id: string;
  platform: string | null;
  content_type: string;
  text: string | null;
  title: string | null;
  language: string | null;
  source_url: string | null;
  like_count: number | null;
  reply_count: number | null;
  repost_count: number | null;
  risk_score: number | null;
  risk_labels: string[] | null;
  topics: string[] | null;
  actor_id: string | null;
  collected_at: string | null;
  observed_at: string | null;
  created_at: string;
}

export interface ContentSearchParams {
  query?: string;
  platform?: string;
  content_type?: string;
  language?: string;
  min_risk_score?: number;
  start_date?: string;
  end_date?: string;
  offset?: number;
  limit?: number;
}

export interface ContentStats {
  total: number;
  by_platform: Record<string, number>;
  by_type: Record<string, number>;
}

export interface Alert {
  id: string;
  alert_type: string;
  title: string;
  summary: string | null;
  status: string;
  priority: string;
  overall_priority_score: number | null;
  created_at: string;
}

export interface AlertParams {
  status?: string;
  priority?: string;
  offset?: number;
  limit?: number;
}

export interface AlertStats {
  by_status: Record<string, number>;
  by_priority: Record<string, number>;
}

export interface TriageRequest {
  status: string;
  feedback?: string;
  triage_notes?: string;
  case_id?: string;
}

export interface Case {
  id: string;
  title: string;
  description: string | null;
  status: string;
  priority: string;
  tags: string[] | null;
  category: string | null;
  briefing: string | null;
  created_at: string;
  updated_at: string;
}

export interface CaseParams {
  status?: string;
  offset?: number;
  limit?: number;
}

export interface CreateCaseRequest {
  title: string;
  description?: string;
  priority?: string;
  tags?: string[];
  category?: string;
}

export interface UpdateCaseRequest {
  title?: string;
  description?: string;
  status?: string;
  priority?: string;
  tags?: string[];
}

export interface CaseNoteRequest {
  text: string;
  note_type?: string;
}

export interface Watchlist {
  id: string;
  name: string;
  description: string | null;
  watch_type: string;
  is_active: boolean;
  alert_on_match: boolean;
  entry_count: number;
  created_at: string;
}

export interface CreateWatchlistRequest {
  name: string;
  description?: string;
  watch_type?: string;
  alert_on_match?: boolean;
  platforms?: string[];
}

export interface WatchlistEntry {
  id: string;
  value: string;
  entry_type: string;
  is_active: boolean;
  match_count: number;
  created_at: string;
}

export interface WatchlistEntryRequest {
  value: string;
  entry_type?: string;
}

export interface DailyBrief {
  generated_at: string;
  period_hours: number;
  summary: {
    total_content_items: number;
    platform_breakdown: Record<string, number>;
    alert_summary: Record<string, number>;
  };
  high_risk_content: Array<{
    id: string;
    platform: string;
    text_preview: string;
    risk_score: number;
    source_url: string | null;
  }>;
  recent_alerts: Array<{
    id: string;
    type: string;
    title: string;
    priority: string;
    status: string;
  }>;
  provenance: {
    data_sources: string[];
    generation_method: string;
  };
}

export interface IngestUrlRequest {
  url: string;
  title?: string;
  text?: string;
}

export interface IngestTextRequest {
  text: string;
  title?: string;
  actor_handle?: string;
}

export interface IngestResponse {
  event_count: number;
  message: string;
}

export interface HealthResponse {
  status: string;
  version: string;
  collectors: Record<string, boolean>;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  offset: number;
  limit: number;
}
