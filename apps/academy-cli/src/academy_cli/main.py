"""The ``academy`` command: list / show / run / chain / kpi.

Deliberately dependency-free (argparse + print) so students can read the whole
front door in one sitting.
"""

from __future__ import annotations

import argparse
import sys

import academy_hrsd  # noqa: F401  (import = scenario registration)
from academy_core.chain import CANONICAL_24_STEP_CHAIN, EXECUTED_STEPS, HITL_GATE_STEP
from academy_core.models import ChainRequest
from academy_core.registry import all_scenarios, get
from academy_core.runtime import ChainRunner
from academy_services.hub import ServiceHub

WIDTH = 100


def _rule(char: str = "─") -> str:
    return char * WIDTH


def cmd_list(_: argparse.Namespace) -> int:
    print(f"{'ID':<12} {'Scenario':<34} {'Chain':<20} {'HITL':<12} Lead agent")
    print(_rule())
    for s in all_scenarios():
        spec = s.spec
        print(f"{spec.scenario_id:<12} {spec.name:<34} {spec.chain_focus:<20} "
              f"{spec.hitl_mode.value:<12} {spec.lead_agent}")
    print(f"\n{len(all_scenarios())} scenarios · area: HR Service Delivery (Tier-0) · "
          "MAF pattern: Sequential")
    return 0


def cmd_show(args: argparse.Namespace) -> int:
    spec = get(args.scenario_id).spec
    print(f"\n{spec.scenario_id} · {spec.name}\n{_rule('═')}")
    print(f"{spec.tagline}\n")
    rows = [
        ("Service", spec.service), ("Area", spec.area),
        ("MAF pattern", spec.maf_pattern), ("Chain focus", spec.chain_focus),
        ("HITL mode", spec.hitl_mode.value), ("Lead agent", spec.lead_agent),
        ("Personas", ", ".join(spec.personas)),
        ("Azure services", ", ".join(spec.azure_services)),
        ("Data & tools", ", ".join(spec.data_tools)),
        ("Sample ask", f'"{spec.sample_text}" (as {spec.sample_employee})'),
    ]
    for label, value in rows:
        print(f"  {label:<16} {value}")
    print("\n  KPIs moved (synthetic reference figures):")
    for k in spec.kpis:
        print(f"    · {k.name:<32} {k.baseline} → {k.target:<12} owner: {k.owner}")
    print()
    return 0


def cmd_run(args: argparse.Namespace) -> int:
    scenario = get(args.scenario_id)
    spec = scenario.spec
    hub = ServiceHub(runtime=args.runtime)
    runner = ChainRunner(hub, approver=(lambda _p: True) if args.approve else None)
    request = None
    if args.text or args.employee:
        request = ChainRequest(args.employee or spec.sample_employee,
                               args.text or spec.sample_text)
    report = runner.run(scenario, request)

    print(f"\n▶ {spec.scenario_id} · {spec.name}   "
          f"[{spec.maf_pattern} · {spec.chain_focus} · {spec.hitl_mode.value} · "
          f"runtime {hub.runtime}]")
    print(_rule("═"))
    print(f'  ask ({report.request.employee_id}): "{report.request.text}"\n')

    for row in report.ledger.rows:
        conf = f"  conf {row.confidence:.2f}" if row.confidence is not None else ""
        gate_mark = " ★" if row.step == HITL_GATE_STEP and row.stage == "hitl-gate" else ""
        print(f"  [{row.step:>2}]{gate_mark} {row.stage:<12} {row.detail}{conf}"
              + (f"  → {row.outcome}" if row.outcome != "ok" else ""))

    if report.gate:
        print(f"\n  gate: {report.gate.mode.value} · "
              + ("ESCALATED → " + (report.escalation_route or "") if report.gate.escalated
                 else "approved" if report.gate.approved else "pending approval")
              + f" · {report.gate.note}")

    print(f"\n{_rule()}\n  ANSWER\n{_rule()}")
    for line in report.answer.splitlines():
        print(f"  {line}")

    print(f"\n{_rule()}\n  KPIs this run moves (synthetic reference figures)\n{_rule()}")
    for k in report.kpis:
        print(f"  · {k.name:<32} {k.baseline} → {k.target:<12} owner: {k.owner}")
    print(f"\n  ledger: {len(report.ledger.rows)} × 14-field rows · run {report.ledger.run_id}")
    if args.ledger:
        path = report.ledger.to_jsonl(args.ledger)
        print(f"  ledger exported → {path}")
    print()
    return 0


def cmd_chain(_: argparse.Namespace) -> int:
    print("\nThe canonical 24-step chain — W1 foundation · W2 pilot · W3 scale & fuse")
    print(_rule("═"))
    for step in CANONICAL_24_STEP_CHAIN:
        marker = " ★ HITL GATE" if step["step"] == HITL_GATE_STEP else ""
        executed = " ·  executed by this academy" if step["step"] in EXECUTED_STEPS else ""
        print(f"  [{step['step']:>2}] {step['wave']}  {step['title']:<46} "
              f"{step['layer']}{marker}{executed}")
    print("\n  Scenarios specialize titles and purposes but keep 1..24 and exactly one "
          "HITL gate at step 16.\n")
    return 0


def cmd_kpi(_: argparse.Namespace) -> int:
    print(f"\n{'KPI':<34} {'Baseline → Target':<22} {'Owner':<26} Scenario")
    print(_rule())
    for s in all_scenarios():
        for k in s.spec.kpis:
            print(f"{k.name:<34} {k.baseline + ' → ' + k.target:<22} {k.owner:<26} "
                  f"{s.spec.scenario_id}")
    print("\nAll figures are synthetic reference figures — never client claims.\n")
    return 0


def main(argv: list[str] | None = None) -> int:
    # Windows consoles often default to cp1252, which can't print the chain glyphs (★ · →).
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, OSError):
        pass
    parser = argparse.ArgumentParser(
        prog="academy",
        description="AI Academy — run HR Service Delivery scenario chains.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("list", help="list all registered scenarios").set_defaults(func=cmd_list)

    p_show = sub.add_parser("show", help="show a scenario's full spec")
    p_show.add_argument("scenario_id")
    p_show.set_defaults(func=cmd_show)

    p_run = sub.add_parser("run", help="run a scenario chain end to end")
    p_run.add_argument("scenario_id")
    p_run.add_argument("--text", help="override the sample request text")
    p_run.add_argument("--employee", help="override the requesting employee id (E1001…)")
    p_run.add_argument("--runtime", choices=["mock", "live", "maf"], default=None,
                       help="override ACADEMY_RUNTIME")
    p_run.add_argument("--approve", action="store_true",
                       help="auto-approve a hard HITL gate (grader mode)")
    p_run.add_argument("--ledger", help="export the run's ledger to this JSONL path")
    p_run.set_defaults(func=cmd_run)

    p_chain = sub.add_parser("chain", help="print the canonical 24-step chain")
    p_chain.set_defaults(func=cmd_chain)
    p_kpi = sub.add_parser("kpi", help="print the KPI table across all scenarios")
    p_kpi.set_defaults(func=cmd_kpi)

    args = parser.parse_args(argv)
    try:
        return int(args.func(args))
    except KeyError as exc:
        print(f"error: {exc.args[0]}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
