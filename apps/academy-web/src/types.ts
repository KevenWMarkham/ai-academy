// Mirrors the academy-api response models (apps/academy-api/src/academy_api/main.py).

export interface ScenarioSummary {
  scenario_id: string;
  name: string;
  tagline: string;
  service: string;
  chain_focus: string;
  hitl_mode: "ZERO_TOUCH" | "ACK_ONLY" | "ESCALATION" | "HITL";
  lead_agent: string;
}

export interface Kpi {
  name: string;
  owner: string;
  baseline: string;
  target: string;
}

export interface ScenarioDetail extends ScenarioSummary {
  area: string;
  maf_pattern: string;
  personas: string[];
  azure_services: string[];
  kpis: Kpi[];
  sample_text: string;
}

export interface Gate {
  mode: string;
  approved: boolean;
  escalated: boolean;
  actor: string;
  note: string;
}

export interface LedgerRow {
  seq: number;
  step: number;
  stage: string;
  action: string;
  detail: string;
  outcome: string;
  confidence: number | null;
}

export interface RunOut {
  scenario_id: string;
  scenario_name: string;
  answer: string;
  gate: Gate;
  escalation_route: string | null;
  kpis: Kpi[];
  ledger: LedgerRow[];
}

export interface Employee {
  id: string;
  label: string;
}

// The synthetic roster (data/employees.json) — the API is employee-scoped by id.
export const EMPLOYEES: Employee[] = [
  { id: "E1001", label: "Raj Patel · Engineering · US-CA" },
  { id: "E1002", label: "Ingrid Weber · Operations · DE-BY" },
  { id: "E1003", label: "Lucía Álvarez · Sales · MX" },
];
