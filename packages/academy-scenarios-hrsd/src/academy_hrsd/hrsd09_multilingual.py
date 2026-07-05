"""hr-hrsd-09 · Multilingual employee support — answers in the employee's language.

Translator wraps the chain: detect the language, translate in, run the same
grounded answer path, translate out. The chain itself is language-agnostic —
that's the teaching point.
Brief: scenarios/hr-service-delivery/hr-hrsd-09-multilingual.md
"""

from __future__ import annotations

from academy_core.models import (
    ChainContext,
    HitlMode,
    Kpi,
    Role,
    Scenario,
    ScenarioSpec,
    StageResult,
)
from academy_core.registry import register

SPEC = ScenarioSpec(
    scenario_id="hr-hrsd-09",
    name="Multilingual employee support",
    tagline="The same grounded answers, in the employee's own language.",
    service="HR-HRSD-04 · Ticket Deflection",
    chain_focus="Classify",
    hitl_mode=HitlMode.ZERO_TOUCH,
    lead_agent="Multilingual",
    personas=("Lucía Álvarez", "Sofia Ramos"),
    kpis=(
        Kpi("Non-English deflection rate", "Sofia Ramos (HR Ops)", "0%", "50%",
            "language ceases to be a support barrier"),
        Kpi("Employee CSAT (non-English)", "Sofia Ramos (HR Ops)", "3.1", "4.5 / 5",
            "native-language answers, 24×7"),
    ),
    azure_services=("Azure AI Translator", "Azure AI Language (detection)",
                    "Azure OpenAI (Foundry)"),
    data_tools=("gold_hr_worker_v2", "policy KB", "MCP translate tool"),
    sample_text="¿Cuántos días de vacaciones me quedan este año?",
    sample_employee="E1003",
)

INTENTS: dict[str, tuple[str, ...]] = {
    "pto_balance": ("vacaciones", "vacation", "urlaub", "pto", "días", "days left", "quedan"),
    "payslip": ("nómina", "payslip", "gehaltsabrechnung", "paycheck"),
    "leave": ("licencia", "leave", "krankmeldung", "absence"),
}


def assess(ctx: ChainContext) -> StageResult:
    lang = ctx.services.language.detect_language(ctx.request.text)
    ctx.state["lang"] = lang
    emp = ctx.employee
    return StageResult(
        Role.ASSESS,
        f"Detected language '{lang}'; read {emp['name']}'s record "
        f"(preferred language '{emp['language']}', PTO balance {emp['pto_balance_days']}d).",
    )


def classify(ctx: ChainContext) -> StageResult:
    lang = ctx.state["lang"]
    english = (ctx.services.translator.translate(ctx.request.text, "en", lang)
               if lang != "en" else ctx.request.text)
    ctx.state["english_text"] = english
    intent = ctx.services.language.classify_intent(ctx.request.text + " " + english, INTENTS)
    ctx.state["intent"] = intent.intent
    return StageResult(
        Role.CLASSIFY,
        f"Translated {lang}→en for processing; intent: {intent.intent} "
        f"(evidence: {', '.join(intent.evidence) or '—'}).",
        confidence=intent.confidence,
    )


def quantify(ctx: ChainContext) -> StageResult:
    hits = ctx.services.search.query("PTO accrual balance carry over vacation days")
    ctx.state["hits"] = hits
    return StageResult(
        Role.QUANTIFY,
        f"Grounded on '{hits[0].title}'; personal balance read from the worker record."
        if hits else "No grounding found.",
    )


def decide(ctx: ChainContext) -> StageResult:
    emp = ctx.employee
    hits = ctx.state.get("hits") or []
    cite = f" [source: {hits[0].doc_id}]" if hits else ""
    if ctx.state["intent"] == "pto_balance":
        english_answer = (
            f"You have {emp['pto_balance_days']} PTO days remaining this year. "
            f"Accrual scales with tenure and appears on each payslip.{cite}"
        )
    else:
        english_answer = (
            f"Here is what I found:{cite} "
            + (hits[0].snippet if hits else "please contact HR shared services.")
        )
    lang = ctx.state["lang"]
    answer = (ctx.services.translator.translate(english_answer, lang, "en")
              if lang != "en" else english_answer)
    ctx.state["answer"] = answer
    return StageResult(
        Role.DECIDE,
        f"Composed the grounded answer in English, translated back en→{lang}.",
        confidence=ctx.results[Role.CLASSIFY].confidence,
    )


def act(ctx: ChainContext) -> StageResult:
    return StageResult(
        Role.ACT,
        f"Answer delivered in Teams in '{ctx.state['lang']}' — the employee's own language.",
    )


def learn(ctx: ChainContext) -> StageResult:
    return StageResult(
        Role.LEARN,
        "Language mix of inbound questions steers which policies get human-reviewed "
        "translations next.",
    )


SCENARIO = register(Scenario(SPEC, {
    Role.ASSESS: assess, Role.CLASSIFY: classify, Role.QUANTIFY: quantify,
    Role.DECIDE: decide, Role.ACT: act, Role.LEARN: learn,
}))
