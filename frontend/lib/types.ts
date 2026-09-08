export type State = "yes" | "partial" | "no" | "unknown";
export type Mode = "local" | "brand";

export interface Finding {
  item_id: string;
  label: string;
  state: State;
  evidence: string | null;
}

export interface SignalResult {
  collector: string;
  status: "ok" | "partial" | "error";
  findings: Finding[];
  raw: Record<string, unknown>;
  error: string | null;
}

export interface ReadinessReport {
  target_url: string;
  place_name: string | null;
  region: string | null;
  mode: Mode;
  score: number;
  findings: Finding[];
  results: SignalResult[];
  generated_at: string;
  share_id?: string | null;
}

export interface AuditRequest {
  url?: string;           // LOCAL 모드에서 선택
  place_name?: string;
  region?: string;
  mode: Mode;
}

// ── Monitor ───────────────────────────────────────────────────

export interface MonitorProject {
  id: number;
  name: string;
  target_url: string;
  mode: Mode;
  brand_keyword: string;
  created_at: string;
}

export interface MonitorQuestion {
  id: number;
  question: string;
  active: boolean;
}

export interface RunResult {
  ai_model: string;
  mentioned: boolean;
  rank: number | null;
  snippet: string | null;
  error: string | null;
}

export interface RunSummary {
  question_id: number;
  question: string;
  results: RunResult[];
}

export interface DashboardRun {
  ai_model: string;
  mentioned: boolean;
  rank: number | null;
  ran_at: string;
}

export interface DashboardRow {
  question_id: number;
  question: string;
  runs: DashboardRun[];
  mention_rate: number;
}

export interface ModelStat {
  ai_model: string;
  label: string;
  configured: boolean;      // false면 "미설정"이지 "0% 언급"이 아님
  total_runs: number;
  mentioned_runs: number;
  rate: number;
  avg_rank: number | null;
}

export interface Dashboard {
  project_id: number;
  project_name: string;
  total_mention_rate: number;
  rows: DashboardRow[];
  by_model: ModelStat[];
}
