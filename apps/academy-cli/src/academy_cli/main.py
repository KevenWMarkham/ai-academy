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


def cmd_kb(args: argparse.Namespace) -> int:
    from pathlib import Path

    from academy_services.data import find_data_dir
    from academy_services.kb import KnowledgeBase

    data_dir = find_data_dir()
    kb = KnowledgeBase(data_dir)
    hub = ServiceHub(data_dir=data_dir, runtime=args.runtime)

    if args.kb_action == "stats":
        by_type: dict[str, int] = {}
        for meta in kb.documents.values():
            key = str(meta.get("doc_type", "article"))
            by_type[key] = by_type.get(key, 0) + 1
        mode = "live" if hub.embeddings.live else "mock"
        print(f"\nknowledge base: {len(kb.documents)} documents · {len(kb.chunks)} chunks "
              f"· vector dims {hub.embeddings.dimensions} ({mode})")
        for doc_type, count in sorted(by_type.items()):
            print(f"  {doc_type:<10} {count}")
        print("\nscenario coverage (docs that ground each scenario):")
        for scenario_id, docs in kb.scenario_coverage().items():
            print(f"  {scenario_id}  {len(docs):>2} docs · {', '.join(docs[:4])}"
                  + (" …" if len(docs) > 4 else ""))
        print()
        return 0

    if args.kb_action == "build":
        out = Path(args.out or data_dir / "kb" / "index" / "chunks.jsonl")
        embedder = hub.embeddings if args.vectors else None
        path = kb.build_jsonl(out, embedder)
        note = (f"with {hub.embeddings.dimensions}-dim content_vector" if args.vectors
                else "without vectors (pass --vectors to embed)")
        print(f"{len(kb.chunks)} chunks → {path} {note}")
        return 0

    if args.kb_action == "search":
        hits = (hub.search.vector_query(args.query, top=args.top) if args.vector
                else hub.search.query(args.query, top=args.top))
        mode = "vector (cosine over content_vector)" if args.vector else "keyword"
        print(f"\n{mode} search: {args.query!r}")
        for i, h in enumerate(hits, 1):
            print(f"  {i}. [{h.score:.3f}] {h.title} · {h.section}  ({h.doc_id})")
            print(f"     {h.snippet[:140]}…")
        print()
        return 0

    if args.kb_action == "push":
        from academy_services.azure_search import ensure_index, search_configured, upload_chunks

        if not search_configured():
            print("set AZURE_SEARCH_ENDPOINT and AZURE_SEARCH_KEY first (see .env.example)",
                  file=sys.stderr)
            return 2
        embedder = hub.embeddings
        name = ensure_index(embedder.dimensions)
        count = upload_chunks(kb.chunks, embedder)
        print(f"index '{name}' ready · {count} chunks uploaded "
              f"({embedder.dimensions}-dim vectors, {'live AOAI' if embedder.live else 'mock'})")
        return 0

    return 2


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

    p_kb = sub.add_parser("kb", help="knowledge base: stats / build / search / push")
    kb_sub = p_kb.add_subparsers(dest="kb_action", required=True)
    p_stats = kb_sub.add_parser("stats", help="corpus counts and per-scenario coverage")
    p_build = kb_sub.add_parser("build", help="write the chunked index as JSONL")
    p_build.add_argument("--out", help="output path (default data/kb/index/chunks.jsonl)")
    p_build.add_argument("--vectors", action="store_true",
                         help="embed each chunk into the content_vector column")
    p_search = kb_sub.add_parser("search", help="query the KB locally")
    p_search.add_argument("query")
    p_search.add_argument("--vector", action="store_true",
                          help="pure vector search instead of keyword")
    p_search.add_argument("--top", type=int, default=3)
    p_push = kb_sub.add_parser("push", help="create the Azure AI Search index and upload chunks")
    for p in (p_stats, p_build, p_search, p_push):
        p.add_argument("--runtime", choices=["mock", "live", "maf"], default=None)
        p.set_defaults(func=cmd_kb)

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
