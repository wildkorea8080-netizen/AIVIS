import type { Dashboard, MonitorProject, MonitorQuestion, RunSummary } from "./types";

const API_BASE = process.env.API_URL ?? "http://localhost:8000";

export async function createProject(body: {
  name: string;
  target_url: string;
  mode: string;
  brand_keyword: string;
  owner_email?: string;
}): Promise<MonitorProject> {
  const res = await fetch(`${API_BASE}/monitor/projects`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
    cache: "no-store",
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function getProject(id: number): Promise<MonitorProject> {
  const res = await fetch(`${API_BASE}/monitor/projects/${id}`, { cache: "no-store" });
  if (!res.ok) throw new Error("프로젝트를 찾을 수 없습니다.");
  return res.json();
}

export async function listQuestions(projectId: number): Promise<MonitorQuestion[]> {
  const res = await fetch(`${API_BASE}/monitor/projects/${projectId}/questions`, { cache: "no-store" });
  if (!res.ok) return [];
  return res.json();
}

export async function addQuestion(projectId: number, question: string): Promise<MonitorQuestion> {
  const res = await fetch(`${API_BASE}/monitor/projects/${projectId}/questions`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
    cache: "no-store",
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function runMonitor(projectId: number): Promise<RunSummary[]> {
  const res = await fetch(`${API_BASE}/monitor/projects/${projectId}/run`, {
    method: "POST",
    cache: "no-store",
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function getDashboard(projectId: number): Promise<Dashboard> {
  const res = await fetch(`${API_BASE}/monitor/projects/${projectId}/dashboard`, { cache: "no-store" });
  if (!res.ok) throw new Error("대시보드를 불러올 수 없습니다.");
  return res.json();
}
