"""Knowledge-base contract tests — corpus integrity, chunking, vectors, coverage."""

from __future__ import annotations

import json
import math

import pytest

from academy_services.azure_search import index_definition
from academy_services.data import find_data_dir
from academy_services.embeddings import MOCK_DIMENSIONS, EmbeddingService, cosine
from academy_services.hub import ServiceHub
from academy_services.kb import KnowledgeBase, parse_front_matter


@pytest.fixture(scope="module")
def kb() -> KnowledgeBase:
    return KnowledgeBase(find_data_dir())


@pytest.fixture(scope="module")
def hub() -> ServiceHub:
    return ServiceHub(runtime="mock")


def test_corpus_is_extensive(kb) -> None:
    assert len(kb.documents) >= 28
    assert len(kb.chunks) >= 90
    doc_types = {str(m.get("doc_type")) for m in kb.documents.values()}
    assert {"policy", "guide", "faq"} <= doc_types


def test_every_scenario_is_grounded_by_the_kb(kb) -> None:
    coverage = kb.scenario_coverage()
    for n in range(1, 10):
        scenario_id = f"hr-hrsd-0{n}"
        assert coverage.get(scenario_id), f"{scenario_id} has no grounding documents"


def test_front_matter_metadata(kb) -> None:
    pto = kb.documents["pto"]
    assert pto["title"] == "Paid Time Off (PTO) Policy"
    assert "US-CA" in pto["jurisdictions"]  # type: ignore[operator]
    meta, body = parse_front_matter("---\ntitle: X\ntags: [a, b]\n---\n# X\nbody")
    assert meta == {"title": "X", "tags": ("a", "b")}
    assert body.startswith("# X")


def test_localized_documents_carry_language(kb) -> None:
    languages = {c.language for c in kb.chunks}
    assert {"en", "es", "de"} <= languages
    # Localized docs never leak into the default English retrieval path.
    hits = ServiceHub(runtime="mock").search.query("vacaciones días")
    assert all(h.doc_id not in ("politica-de-vacaciones-es",) for h in hits)


def test_mock_embeddings_are_deterministic_and_normalized() -> None:
    a = EmbeddingService.embed_mock("parental leave election window")
    b = EmbeddingService.embed_mock("parental leave election window")
    assert a == b and len(a) == MOCK_DIMENSIONS
    assert math.isclose(sum(x * x for x in a), 1.0, rel_tol=1e-9)
    assert cosine(a, EmbeddingService.embed_mock("parental leave dates")) > cosine(
        a, EmbeddingService.embed_mock("kubernetes cluster autoscaler")
    )


def test_local_vector_search_finds_the_right_document(hub) -> None:
    hits = hub.search.vector_query("unused vacation days carryover into next year", top=3)
    assert hits and hits[0].doc_id == "pto"


@pytest.mark.parametrize(
    ("query", "expected_doc"),
    [
        ("How many unused PTO days can I carry over into next year?", "pto"),
        ("Is there a stipend for home office equipment when working remote?", "remote-work"),
        ("caregiver leave family serious health condition", "caregiver-medical-leave"),
    ],
)
def test_keyword_ranking_regressions(hub, query, expected_doc) -> None:
    # The scenario samples must keep grounding on their intended documents.
    assert hub.search.query(query)[0].doc_id == expected_doc


def test_escalation_sample_stays_ungrounded(hub) -> None:
    # The escalation demo depends on garnishment staying OUT of the KB.
    garnish = hub.search.query(
        "My paycheck was garnished incorrectly after my divorce settlement — who do I talk to?"
    )
    assert not garnish or garnish[0].score < 0.6


def test_build_jsonl_with_vector_column(kb, tmp_path) -> None:
    out = kb.build_jsonl(tmp_path / "chunks.jsonl", EmbeddingService("mock"))
    lines = out.read_text(encoding="utf-8").splitlines()
    assert len(lines) == len(kb.chunks)
    record = json.loads(lines[0])
    assert {"id", "doc_id", "title", "section", "content", "scenarios",
            "content_vector"} <= set(record)
    assert len(record["content_vector"]) == MOCK_DIMENSIONS


def test_azure_index_definition_matches_embedder_dims() -> None:
    definition = index_definition("hr-knowledge-base", MOCK_DIMENSIONS)
    vector_field = next(f for f in definition["fields"] if f["name"] == "content_vector")
    assert vector_field["dimensions"] == MOCK_DIMENSIONS
    assert vector_field["vectorSearchProfile"] == "kb-vector-profile"
    assert any(f.get("key") for f in definition["fields"])
    assert definition["vectorSearch"]["profiles"][0]["name"] == "kb-vector-profile"
