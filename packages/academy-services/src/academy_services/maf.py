"""Microsoft Agent Framework runtime — run the polish/decide seat as a real MAF Agent.

Mirrors the production pattern in ``scenario_chain/maf.py``: when
``ACADEMY_RUNTIME=maf``, AOAI is configured, and the ``agent-framework`` SDK is
installed, the DECIDE-stage polish runs as a MAF :class:`Agent` whose model is
Azure OpenAI (Foundry). If anything is missing the caller falls back to the
direct-AOAI or mock path, so the chain degrades gracefully.

Requires ``pip install academy-services[agents]``.
"""

from __future__ import annotations

import asyncio
import os

_INSTRUCTIONS = (
    "You are an HR Service Delivery answer-polish agent. You receive a fully "
    "drafted, grounded answer. Rewrite it as warm, concise prose for the named "
    "persona. Keep every fact, figure, citation and caveat exactly as drafted; "
    "never invent policy details."
)


def maf_available() -> bool:
    """Whether the Microsoft Agent Framework SDK is importable."""
    try:
        import agent_framework  # noqa: F401

        return True
    except Exception:
        return False


def _azure_chat_client():
    """Build an Agent Framework chat client backed by Azure OpenAI (Foundry)."""
    from agent_framework.openai import OpenAIChatClient

    return OpenAIChatClient(
        model=os.environ["AOAI_CHAT_DEPLOYMENT"],
        azure_endpoint=os.environ["AOAI_ENDPOINT"].rstrip("/"),
        api_key=os.getenv("AOAI_KEY") or os.environ["AOAI_API_KEY"],
        api_version=os.getenv("AOAI_API_VERSION", "2024-10-21"),
    )


async def _run(draft: str, persona: str) -> str:
    from agent_framework import Agent

    agent = Agent(_azure_chat_client(), _INSTRUCTIONS, name="hrsd-polish")
    result = await agent.run(f"Persona: {persona}\n\nDrafted answer:\n{draft}")
    return getattr(result, "text", None) or str(result)


def polish_via_maf(draft: str, *, persona: str) -> str | None:
    """Polish a draft via a MAF agent; ``None`` if MAF is unavailable."""
    if not maf_available():
        return None
    return asyncio.run(_run(draft, persona)).strip()
