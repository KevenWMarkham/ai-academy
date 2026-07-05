"""Azure AI Translator adapter — the wrapper around hr-hrsd-09 multilingual support.

Mock mode does not pretend to translate: it tags the text with the language
pair so the chain's plumbing is honest and visible. Live mode calls the
Translator REST API when ``AZURE_TRANSLATOR_KEY`` is set.
"""

from __future__ import annotations

import json
import os
import urllib.request


class TranslatorService:
    def __init__(self, runtime: str) -> None:
        self.runtime = runtime

    @property
    def live(self) -> bool:
        return self.runtime in ("live", "maf") and bool(os.getenv("AZURE_TRANSLATOR_KEY"))

    def translate(self, text: str, to_lang: str, from_lang: str = "en") -> str:
        if from_lang == to_lang:
            return text
        if self.live:
            try:
                return self._translate_azure(text, to_lang, from_lang)
            except Exception:
                pass  # degrade gracefully to the tagged mock
        return f"[{from_lang}→{to_lang}] {text}"

    @staticmethod
    def _translate_azure(text: str, to_lang: str, from_lang: str) -> str:
        url = (
            "https://api.cognitive.microsofttranslator.com/translate"
            f"?api-version=3.0&from={from_lang}&to={to_lang}"
        )
        request = urllib.request.Request(
            url,
            data=json.dumps([{"text": text}]).encode("utf-8"),
            headers={
                "Ocp-Apim-Subscription-Key": os.environ["AZURE_TRANSLATOR_KEY"],
                "Ocp-Apim-Subscription-Region": os.getenv("AZURE_TRANSLATOR_REGION", "eastus2"),
                "Content-Type": "application/json",
            },
        )
        with urllib.request.urlopen(request, timeout=15) as response:
            payload = json.loads(response.read().decode("utf-8"))
        return payload[0]["translations"][0]["text"]
