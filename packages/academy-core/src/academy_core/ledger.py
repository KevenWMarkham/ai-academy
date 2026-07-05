"""The LEDGER — one 14-field audit row per chain step.

The ledger is the evidence plane: if a step didn't write a row, it didn't
happen. It is what lets an auditor, a regulator, or a grader replay a run.
"""

from __future__ import annotations

import json
import uuid
from dataclasses import asdict, dataclass, fields
from datetime import UTC, datetime
from pathlib import Path


@dataclass(frozen=True)
class LedgerRow:
    """Exactly 14 fields. Do not add or remove without updating docs/04-hitl-and-ledger.md."""

    run_id: str  # 1  one chain execution
    seq: int  # 2  order within the run
    timestamp: str  # 3  UTC ISO-8601
    scenario_id: str  # 4  e.g. hr-hrsd-01
    step: int  # 5  canonical 1..24 step number
    stage: str  # 6  role name or "hitl-gate" / "trigger" / "orchestrate" / "kpi-rollup"
    agent: str  # 7  which agent acted
    persona: str  # 8  which persona the step served
    action: str  # 9  short verb phrase of what happened
    detail: str  # 10 human-readable evidence
    confidence: float | None  # 11 model confidence, if the stage produced one
    hitl_mode: str  # 12 the scenario's gate mode
    actor: str  # 13 "system" or the human who approved/acknowledged
    outcome: str  # 14 ok / approved / acknowledged / escalated / skipped / pending


LEDGER_FIELD_COUNT = len(fields(LedgerRow))
assert LEDGER_FIELD_COUNT == 14, "the LEDGER row is defined as exactly 14 fields"


class Ledger:
    """An append-only row store for one run (in memory, exportable as JSONL)."""

    def __init__(self, run_id: str | None = None) -> None:
        self.run_id = run_id or uuid.uuid4().hex[:12]
        self.rows: list[LedgerRow] = []

    def append(
        self,
        *,
        scenario_id: str,
        step: int,
        stage: str,
        agent: str,
        persona: str,
        action: str,
        detail: str,
        hitl_mode: str,
        confidence: float | None = None,
        actor: str = "system",
        outcome: str = "ok",
    ) -> LedgerRow:
        row = LedgerRow(
            run_id=self.run_id,
            seq=len(self.rows) + 1,
            timestamp=datetime.now(UTC).isoformat(timespec="seconds"),
            scenario_id=scenario_id,
            step=step,
            stage=stage,
            agent=agent,
            persona=persona,
            action=action,
            detail=detail,
            confidence=confidence,
            hitl_mode=hitl_mode,
            actor=actor,
            outcome=outcome,
        )
        self.rows.append(row)
        return row

    def to_jsonl(self, path: str | Path) -> Path:
        """Export the run's evidence as one JSON object per line."""
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("w", encoding="utf-8") as fh:
            for row in self.rows:
                fh.write(json.dumps(asdict(row), ensure_ascii=False) + "\n")
        return target
