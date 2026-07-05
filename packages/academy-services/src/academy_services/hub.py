"""ServiceHub — one lazy facade over every AI-service adapter and data store.

Scenarios never construct clients; they ask the hub. This is the academy's
stand-in for the MCP capability registry (canonical step 7): a governed,
discoverable set of tools the agents are allowed to call.
"""

from __future__ import annotations

import os
from functools import cached_property
from pathlib import Path

from academy_services.data import CaseStore, EmployeeDirectory, RoutingMap, find_data_dir
from academy_services.documents import TemplateStore
from academy_services.embeddings import EmbeddingService
from academy_services.foundry import ChatService
from academy_services.language import LanguageService
from academy_services.search import KBSearch
from academy_services.translator import TranslatorService


class ServiceHub:
    def __init__(self, data_dir: str | Path | None = None, runtime: str | None = None) -> None:
        self.data_dir = Path(data_dir) if data_dir else find_data_dir()
        self.runtime = (runtime or os.getenv("ACADEMY_RUNTIME", "mock")).lower()

    @cached_property
    def employees(self) -> EmployeeDirectory:
        return EmployeeDirectory(self.data_dir)

    @cached_property
    def cases(self) -> CaseStore:
        return CaseStore(self.data_dir)

    @cached_property
    def routing(self) -> RoutingMap:
        return RoutingMap(self.data_dir)

    @cached_property
    def chat(self) -> ChatService:
        return ChatService(self.runtime)

    @cached_property
    def embeddings(self) -> EmbeddingService:
        return EmbeddingService(self.runtime)

    @cached_property
    def search(self) -> KBSearch:
        return KBSearch(self.data_dir, self.runtime, self.embeddings)

    @cached_property
    def language(self) -> LanguageService:
        return LanguageService(self.runtime)

    @cached_property
    def translator(self) -> TranslatorService:
        return TranslatorService(self.runtime)

    @cached_property
    def documents(self) -> TemplateStore:
        return TemplateStore(self.data_dir)
