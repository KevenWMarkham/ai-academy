"""App-package integrity — the cross-references the Copilot platform validates at upload."""

from __future__ import annotations

import json
from pathlib import Path

PKG = Path(__file__).resolve().parents[1] / "m365" / "appPackage"


def _load(name: str) -> dict:
    return json.loads((PKG / name).read_text(encoding="utf-8"))


def test_app_manifest_references_existing_agent_file() -> None:
    manifest = _load("manifest.json")
    agents = manifest["copilotAgents"]["declarativeAgents"]
    assert len(agents) == 1  # the platform supports exactly one per app manifest
    assert (PKG / agents[0]["file"]).is_file()
    for icon in manifest["icons"].values():
        assert (PKG / icon).is_file(), f"missing {icon} — run scripts/make_icons.py"


def test_agent_manifest_shape() -> None:
    agent = _load("declarativeAgent.json")
    assert agent["version"] == "v1.7"
    assert len(agent["instructions"]) <= 8000
    assert 1 <= len(agent["conversation_starters"]) <= 12
    # One starter per scenario — the nine-scenario catalog is the demo script.
    assert len(agent["conversation_starters"]) == 9
    for action in agent["actions"]:
        assert (PKG / action["file"]).is_file()


def test_plugin_functions_match_openapi_operations() -> None:
    plugin = _load("ai-plugin.json")
    assert plugin["schema_version"] == "v2.4"
    spec_ref = plugin["runtimes"][0]["spec"]["url"]
    openapi = _load(spec_ref)
    operation_ids = {
        op["operationId"]
        for path in openapi["paths"].values()
        for op in path.values()
        if isinstance(op, dict) and "operationId" in op
    }
    function_names = {f["name"] for f in plugin["functions"]}
    assert function_names == operation_ids
    assert set(plugin["runtimes"][0]["run_for_functions"]) == function_names


def test_openapi_server_placeholder_present() -> None:
    openapi = _load("openapi.json")
    assert openapi["servers"][0]["url"] == "__ACADEMY_API_BASE_URL__", (
        "the source package must keep the placeholder; m365/package.ps1 stamps the real URL"
    )
