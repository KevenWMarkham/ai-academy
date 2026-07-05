"""Scenario registry — scenario packages register themselves on import."""

from __future__ import annotations

from academy_core.models import Scenario

_REGISTRY: dict[str, Scenario] = {}


def register(scenario: Scenario) -> Scenario:
    """Register a scenario by its id (idempotent; later registration wins)."""
    _REGISTRY[scenario.spec.scenario_id] = scenario
    return scenario


def get(scenario_id: str) -> Scenario:
    try:
        return _REGISTRY[scenario_id]
    except KeyError:
        known = ", ".join(sorted(_REGISTRY)) or "(none registered)"
        raise KeyError(f"unknown scenario {scenario_id!r} — known: {known}") from None


def all_scenarios() -> list[Scenario]:
    return [_REGISTRY[k] for k in sorted(_REGISTRY)]
