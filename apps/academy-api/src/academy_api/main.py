"""FastAPI app exposing the scenario chains to the M365 Copilot declarative agent.

Design notes for students:
- The API is a thin adapter: request in → ChainRunner.run() → RunReport out.
  No business logic lives here; the chain stays the single source of truth.
- ``operationId``s (listScenarios / getScenario / runScenario) are load-bearing:
  they are the function names the Copilot orchestrator plans against, declared
  in ``m365/appPackage/ai-plugin.json``.
- Auth: setting ``ACADEMY_API_KEY`` requires an ``X-Api-Key`` header — the
  minimum bar for a test-tenant deployment. Production at a customer site
  should move to Entra ID (OAuthPluginVault); see docs/07.
"""

from __future__ import annotations

import os

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

import academy_hrsd  # noqa: F401  (import = scenario registration)
from academy_core.models import ChainRequest, Scenario
from academy_core.registry import all_scenarios, get
from academy_core.runtime import ChainRunner
from academy_services.hub import ServiceHub

app = FastAPI(
    title="AI Academy · HR Service Delivery API",
    version="0.1.0",
    description=(
        "Runs HR Service Delivery (Tier-0) scenario chains: grounded agents with a "
        "human-in-the-loop gate at step 16, a full audit ledger, and named KPIs. "
        "Backend for the 'HR Service Delivery' M365 Copilot declarative agent."
    ),
)

# The training decks embed a live-agent panel that calls this API from the
# browser (file:// or any host), so cross-origin must be open. Teaching API,
# synthetic data, optional X-Api-Key — CORS is not the security boundary here.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

_hub = ServiceHub()


def require_api_key(x_api_key: str | None = Header(default=None, alias="X-Api-Key")) -> None:
    """Enforce the shared key only when one is configured (mock/dev stays open)."""
    expected = os.getenv("ACADEMY_API_KEY")
    if expected and x_api_key != expected:
        raise HTTPException(status_code=401, detail="missing or invalid X-Api-Key header")


class ScenarioSummary(BaseModel):
    scenario_id: str = Field(description="Scenario id, e.g. hr-hrsd-01")
    name: str
    tagline: str
    service: str
    chain_focus: str
    hitl_mode: str = Field(description="ZERO_TOUCH, ACK_ONLY, ESCALATION or HITL")
    lead_agent: str


class KpiOut(BaseModel):
    name: str
    owner: str
    baseline: str
    target: str


class ScenarioDetail(ScenarioSummary):
    area: str
    maf_pattern: str
    personas: list[str]
    azure_services: list[str]
    kpis: list[KpiOut]
    sample_text: str


class GateOut(BaseModel):
    mode: str
    approved: bool
    escalated: bool
    actor: str
    note: str


class LedgerRowOut(BaseModel):
    seq: int
    step: int = Field(description="Canonical 1..24 chain step")
    stage: str
    action: str
    detail: str
    outcome: str
    confidence: float | None = None


class RunIn(BaseModel):
    scenario_id: str = Field(description="Scenario to run, e.g. hr-hrsd-01")
    employee_id: str | None = Field(
        default=None, description="Requesting employee id (defaults to the scenario's sample)"
    )
    text: str | None = Field(
        default=None, description="The employee's question or request in their own words"
    )


class RunOut(BaseModel):
    scenario_id: str
    scenario_name: str
    answer: str = Field(description="The grounded answer to show the employee")
    gate: GateOut = Field(description="What happened at the step-16 HITL gate")
    escalation_route: str | None = Field(
        default=None, description="Where the request was routed if the gate escalated"
    )
    kpis: list[KpiOut] = Field(description="The KPIs this run moves (synthetic reference figures)")
    ledger: list[LedgerRowOut] = Field(description="The run's audit trail, one row per step")


def _summary(s: Scenario) -> ScenarioSummary:
    spec = s.spec
    return ScenarioSummary(
        scenario_id=spec.scenario_id, name=spec.name, tagline=spec.tagline,
        service=spec.service, chain_focus=spec.chain_focus,
        hitl_mode=spec.hitl_mode.value, lead_agent=spec.lead_agent,
    )


@app.get("/healthz", include_in_schema=False)
def healthz() -> dict[str, str]:
    return {"status": "ok", "runtime": _hub.runtime}


@app.get(
    "/scenarios",
    operation_id="listScenarios",
    summary="List the HR Service Delivery scenarios",
    response_model=list[ScenarioSummary],
    dependencies=[Depends(require_api_key)],
)
def list_scenarios() -> list[ScenarioSummary]:
    """List every registered scenario with its chain shape and HITL mode."""
    return [_summary(s) for s in all_scenarios()]


@app.get(
    "/scenarios/{scenario_id}",
    operation_id="getScenario",
    summary="Get one scenario's full specification",
    response_model=ScenarioDetail,
    dependencies=[Depends(require_api_key)],
)
def get_scenario(scenario_id: str) -> ScenarioDetail:
    """Full spec: personas, KPIs, Azure services, and a sample request."""
    try:
        spec = get(scenario_id).spec
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc.args[0])) from None
    return ScenarioDetail(
        **_summary(get(scenario_id)).model_dump(),
        area=spec.area, maf_pattern=spec.maf_pattern,
        personas=list(spec.personas),
        azure_services=list(spec.azure_services),
        kpis=[KpiOut(name=k.name, owner=k.owner, baseline=k.baseline, target=k.target)
              for k in spec.kpis],
        sample_text=spec.sample_text,
    )


@app.post(
    "/runs",
    operation_id="runScenario",
    summary="Run a scenario chain for an employee request",
    response_model=RunOut,
    dependencies=[Depends(require_api_key)],
)
def run_scenario(body: RunIn) -> RunOut:
    """Execute the six-role chain (Assess → Classify → Quantify → Decide →
    HITL gate → Act → Learn) and return the answer, the gate outcome, the KPIs
    moved, and the 14-field audit ledger."""
    try:
        scenario = get(body.scenario_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc.args[0])) from None
    spec = scenario.spec
    request = None
    if body.text or body.employee_id:
        request = ChainRequest(body.employee_id or spec.sample_employee,
                               body.text or spec.sample_text)
    report = ChainRunner(_hub).run(scenario, request)
    gate = report.gate
    assert gate is not None  # the runner always gates
    return RunOut(
        scenario_id=spec.scenario_id,
        scenario_name=spec.name,
        answer=report.answer,
        gate=GateOut(mode=gate.mode.value, approved=gate.approved,
                     escalated=gate.escalated, actor=gate.actor, note=gate.note),
        escalation_route=report.escalation_route,
        kpis=[KpiOut(name=k.name, owner=k.owner, baseline=k.baseline, target=k.target)
              for k in spec.kpis],
        ledger=[
            LedgerRowOut(seq=r.seq, step=r.step, stage=r.stage, action=r.action,
                         detail=r.detail, outcome=r.outcome, confidence=r.confidence)
            for r in report.ledger.rows
        ],
    )
