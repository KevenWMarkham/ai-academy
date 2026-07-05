"""Synthetic-data access: employees (gold_hr_worker_v2), cases (gold_hr_case_v1), routing.

Stand-ins for the Gold agent-safe views a production chain reads. Everything
is scoped: an agent asks for *one* employee's record, never the table.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


def find_data_dir() -> Path:
    """Locate the repo's ``data/`` folder: env var, then cwd ancestors, then module ancestors."""
    env = os.getenv("ACADEMY_DATA_DIR")
    if env:
        return Path(env)
    marker = "employees.json"
    candidates = [Path.cwd(), *Path.cwd().parents, *Path(__file__).resolve().parents]
    for base in candidates:
        candidate = base / "data"
        if (candidate / marker).is_file():
            return candidate
    raise FileNotFoundError(
        "could not locate the AI-Academy data/ folder — set ACADEMY_DATA_DIR or run from the repo"
    )


class EmployeeDirectory:
    """gold_hr_worker_v2 — one scoped worker record per lookup."""

    def __init__(self, data_dir: Path) -> None:
        self._records: dict[str, dict[str, Any]] = json.loads(
            (data_dir / "employees.json").read_text(encoding="utf-8")
        )

    def get(self, employee_id: str) -> dict[str, Any]:
        record = dict(self._records.get(employee_id, {}))
        if record:
            record["employee_id"] = employee_id
        return record


class CaseStore:
    """gold_hr_case_v1 — HR cases/requests, scoped to the asking employee."""

    def __init__(self, data_dir: Path) -> None:
        self._cases: list[dict[str, Any]] = json.loads(
            (data_dir / "cases.json").read_text(encoding="utf-8")
        )

    def for_employee(self, employee_id: str) -> list[dict[str, Any]]:
        return [c for c in self._cases if c.get("employee_id") == employee_id]

    def open_case(self, case: dict[str, Any]) -> dict[str, Any]:
        """Simulate the ACT-stage mutation: write a new case row (in memory only)."""
        case = {"case_id": f"HRC-{20000 + len(self._cases) + 1}", "status": "open", **case}
        self._cases.append(case)
        return case


class RoutingMap:
    """Which specialist team owns which topic — the smart-routing destination table."""

    def __init__(self, data_dir: Path) -> None:
        self._map: dict[str, dict[str, Any]] = json.loads(
            (data_dir / "routing-map.json").read_text(encoding="utf-8")
        )

    def route_for(self, text: str) -> dict[str, Any]:
        lowered = text.lower()
        best: dict[str, Any] | None = None
        best_hits = 0
        for team in self._map.values():
            hits = sum(1 for kw in team.get("keywords", []) if kw in lowered)
            if hits > best_hits:
                best, best_hits = team, hits
        return best or self._map["hr-shared-services"]
