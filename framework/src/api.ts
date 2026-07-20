import type { AttackRun, PlatformStatus, RunRequest } from "./types";

const API_ROOT = "/api";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_ROOT}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...init?.headers,
    },
  });
  if (!response.ok) {
    let message = `${response.status} ${response.statusText}`;
    try {
      const payload = (await response.json()) as { detail?: string };
      if (payload.detail) message = payload.detail;
    } catch {
      // The status text remains the most useful fallback.
    }
    throw new Error(message);
  }
  if (response.status === 204) return undefined as T;
  return (await response.json()) as T;
}

export function getPlatformStatus(baseUrl: string): Promise<PlatformStatus> {
  return request(`/status?ollama_base_url=${encodeURIComponent(baseUrl)}`);
}

export function createRun(payload: RunRequest): Promise<AttackRun> {
  return request("/runs", { method: "POST", body: JSON.stringify(payload) });
}

export function getRun(runId: string): Promise<AttackRun> {
  return request(`/runs/${encodeURIComponent(runId)}`);
}

export async function listRuns(): Promise<AttackRun[]> {
  const payload = await request<{ runs: AttackRun[] }>("/runs");
  return payload.runs;
}

export function executeRun(runId: string): Promise<AttackRun> {
  return request(`/runs/${encodeURIComponent(runId)}/execute`, { method: "POST" });
}

export function cancelRun(runId: string): Promise<AttackRun> {
  return request(`/runs/${encodeURIComponent(runId)}/cancel`, { method: "POST" });
}

export function deleteRun(runId: string): Promise<void> {
  return request(`/runs/${encodeURIComponent(runId)}`, { method: "DELETE" });
}
