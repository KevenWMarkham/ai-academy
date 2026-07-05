"""Azure OpenAI (Foundry) chat adapter — the LLM seat in the DECIDE stage.

Design point for students: the chain composes its facts *deterministically*
(grounding, balances, citations) and hands the LLM a **draft to polish**, not
an open question. In mock mode the polish is the identity function — which is
exactly why every test passes with no credentials.
"""

from __future__ import annotations

import os


def aoai_ready() -> bool:
    """Whether Azure OpenAI (Foundry) is configured via environment variables."""
    return bool(
        os.getenv("AOAI_ENDPOINT")
        and (os.getenv("AOAI_KEY") or os.getenv("AOAI_API_KEY"))
        and os.getenv("AOAI_CHAT_DEPLOYMENT")
    )


class ChatService:
    """Polish a deterministic draft into natural prose (live), or pass it through (mock)."""

    def __init__(self, runtime: str) -> None:
        self.runtime = runtime

    @property
    def live(self) -> bool:
        return self.runtime in ("live", "maf") and aoai_ready()

    def polish(self, draft: str, *, persona: str = "an employee") -> str:
        if not self.live:
            return draft
        try:
            if self.runtime == "maf":
                from academy_services.maf import polish_via_maf

                return polish_via_maf(draft, persona=persona) or draft
            return self._polish_via_aoai(draft, persona=persona)
        except Exception:
            # Degrade gracefully — a broken deployment must never break the chain.
            return draft

    @staticmethod
    def _polish_via_aoai(draft: str, *, persona: str) -> str:
        from openai import AzureOpenAI

        client = AzureOpenAI(
            azure_endpoint=os.environ["AOAI_ENDPOINT"].rstrip("/"),
            api_key=os.getenv("AOAI_KEY") or os.environ["AOAI_API_KEY"],
            api_version=os.getenv("AOAI_API_VERSION", "2024-10-21"),
        )
        response = client.chat.completions.create(
            model=os.environ["AOAI_CHAT_DEPLOYMENT"],
            temperature=0.2,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Rewrite the drafted HR answer as warm, concise prose for "
                        f"{persona}. Keep every fact, figure, citation and caveat exactly "
                        "as drafted — you may not add or invent anything."
                    ),
                },
                {"role": "user", "content": draft},
            ],
        )
        return (response.choices[0].message.content or "").strip()
