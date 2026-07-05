import type { RunOut, ScenarioDetail, ScenarioSummary } from "./types";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`/api${path}`, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });
  if (!response.ok) {
    const body = await response.text().catch(() => "");
    throw new Error(`${response.status} ${response.statusText}${body ? ` — ${body}` : ""}`);
  }
  return (await response.json()) as T;
}

export const api = {
  listScenarios: () => request<ScenarioSummary[]>("/scenarios"),
  getScenario: (id: string) => request<ScenarioDetail>(`/scenarios/${id}`),
  runScenario: (scenarioId: string, employeeId: string, text: string) =>
    request<RunOut>("/runs", {
      method: "POST",
      body: JSON.stringify({ scenario_id: scenarioId, employee_id: employeeId, text }),
    }),
};
