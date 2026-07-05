"""Azure AI Language adapter — language detection, intent classification, PII detection.

Mock mode uses transparent keyword/regex heuristics so students can trace every
classification. The live upgrade points at the Azure AI Language REST API
(``AZURE_LANGUAGE_ENDPOINT``/``KEY``) — left as a lab exercise (docs/06), which
is why mock is the only implementation here.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

_LANGUAGE_MARKERS: dict[str, tuple[str, ...]] = {
    "es": ("¿", "¡", " de ", " que ", "cuántos", "días", "vacaciones", "necesito", "licencia",
           "quedan", "cómo", "años"),
    "de": ("ß", " ich ", " und ", " nicht ", "wieviele", "urlaub", "krankmeldung", "bitte",
           "möchte", "kündigung"),
    "fr": (" je ", " les ", " congé ", "combien", "s'il", "était", "française"),
}

_PII_PATTERNS: dict[str, str] = {
    "email": r"[\w.+-]+@[\w-]+\.[\w.]+",
    "phone": r"(?<!\d)(?:\+?1[ .-]?)?\(?\d{3}\)?[ .-]?\d{3}[ .-]?\d{4}(?!\d)",
    "ssn": r"(?<!\d)\d{3}-\d{2}-\d{4}(?!\d)",
    "street_address": r"\d{1,5}\s+[A-Z][\w.]*(?:\s+[\w.]+){0,4}\s+"
                      r"(?:St|Street|Ave|Avenue|Blvd|Rd|Road|Dr|Drive|Ln|Lane|Way|Ct)\b[^,\n]*",
}


@dataclass(frozen=True)
class IntentResult:
    intent: str
    confidence: float
    evidence: tuple[str, ...]  # the keywords that fired — the "why"


@dataclass(frozen=True)
class PiiEntity:
    category: str
    text: str


class LanguageService:
    def __init__(self, runtime: str) -> None:
        self.runtime = runtime

    def detect_language(self, text: str) -> str:
        lowered = f" {text.lower()} "
        best, best_hits = "en", 0
        for lang, markers in _LANGUAGE_MARKERS.items():
            hits = sum(1 for m in markers if m in lowered)
            if hits > best_hits:
                best, best_hits = lang, hits
        return best if best_hits >= 2 else "en"

    def classify_intent(self, text: str, intents: dict[str, tuple[str, ...]]) -> IntentResult:
        """Pick the best intent from ``{intent: (keyword, …)}`` — a CLU stand-in."""
        lowered = text.lower()
        best_intent, best_evidence = "unknown", ()
        for intent, keywords in intents.items():
            evidence = tuple(kw for kw in keywords if kw in lowered)
            if len(evidence) > len(best_evidence):
                best_intent, best_evidence = intent, evidence
        confidence = 0.0 if not best_evidence else min(0.55 + 0.15 * len(best_evidence), 0.95)
        return IntentResult(best_intent, round(confidence, 2), best_evidence)

    def detect_pii(self, text: str) -> list[PiiEntity]:
        found: list[PiiEntity] = []
        for category, pattern in _PII_PATTERNS.items():
            for match in re.finditer(pattern, text):
                found.append(PiiEntity(category, match.group(0)))
        return found
