"""Document generation — templated, jurisdiction-correct HR letters.

The teaching point: letter generation is a *data completeness* problem before
it is a generation problem. QUANTIFY validates the fields; only then does ACT
render. (In production, Azure AI Document Intelligence handles the inbound
side — parsing uploaded documents back into fields.)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from string import Formatter
from typing import Any


@dataclass
class RenderedDocument:
    template: str
    title: str
    body: str
    missing_fields: list[str] = field(default_factory=list)

    @property
    def complete(self) -> bool:
        return not self.missing_fields


class TemplateStore:
    def __init__(self, data_dir: Path) -> None:
        self._dir = data_dir / "letter-templates"

    def available(self) -> list[str]:
        return sorted(p.stem for p in self._dir.glob("*.md"))

    def required_fields(self, template: str) -> list[str]:
        raw = (self._dir / f"{template}.md").read_text(encoding="utf-8")
        return sorted({name for _, name, _, _ in Formatter().parse(raw) if name})

    def render(self, template: str, fields_map: dict[str, Any]) -> RenderedDocument:
        raw = (self._dir / f"{template}.md").read_text(encoding="utf-8")
        missing = [f for f in self.required_fields(template) if not fields_map.get(f)]
        body = raw.format_map(
            {k: fields_map.get(k, f"{{{k}}}") for k in self.required_fields(template)}
        )
        title = body.splitlines()[0].lstrip("# ").strip() if body else template
        return RenderedDocument(template=template, title=title, body=body, missing_fields=missing)
