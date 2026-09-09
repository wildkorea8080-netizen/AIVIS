import type { Dashboard, MonitorProject, MonitorQuestion, RunSummary } from "./types";

const API_BASE = process.env.API_URL ?? "http://localhost:8000";

// 무료 호스팅은 유휴 후 첫 요청에서 30~50초가 걸릴 수 있다. 타임아웃 없이 두면
// 요청이 매달린 채 플랫폼이 함수를 강제 종료해 500이 뜬다. 플랫폼 한도(60초)보다
// 짧게 잡아 우리 쪽에서 먼저 끊고, 호출부가 안내 화면을 그릴 수 있게 한다.
const TIMEOUT_MS = 50_000;

async function apiFetch(path: string, init?: RequestInit): Promise<Response> {
  return fetch(`${API_BASE}${path}`, {
    ...init,
    cache: "no-store",
    signal: AbortSignal.timeout(TIMEOUT_MS),
  });
}

export async function createProject(body: {
  name: string;
  target_url: string;
  mode: string;
  brand_keyword: string;
  owner_email?: string;
}): Promise<MonitorProject> {
  const res = await apiFetch("/monitor/projects", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

/** 프로젝트가 없으면 null. 서버에 닿지 못하면 예외를 던진다(호출부가 구분해 처리). */
export async function getProject(id: number): Promise<MonitorProject | null> {
  const res = await apiFetch(`/monitor/projects/${id}`);
  if (res.status === 404) return null;
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

export async function listQuestions(projectId: number): Promise<MonitorQuestion[]> {
  const res = await apiFetch(`/monitor/projects/${projectId}/questions`);
  if (!res.ok) return [];
  return res.json();
}

export async function addQuestion(projectId: number, question: string): Promise<MonitorQuestion> {
  const res = await apiFetch(`/monitor/projects/${projectId}/questions`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function runMonitor(projectId: number): Promise<RunSummary[]> {
  const res = await apiFetch(`/monitor/projects/${projectId}/run`, { method: "POST" });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function getDashboard(projectId: number): Promise<Dashboard> {
  const res = await apiFetch(`/monitor/projects/${projectId}/dashboard`);
  if (!res.ok) throw new Error("대시보드를 불러올 수 없습니다.");
  return res.json();
}
