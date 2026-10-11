from types import SimpleNamespace

import pytest

from pipeline import graph, nodes, publish
from pipeline.nodes import MAX_LOOPS, Critique


class FakeWriter:
    """Pretends to be the writer LLM. Records every prompt it receives."""

    def __init__(self):
        self.prompts = []

    def invoke(self, prompt):
        self.prompts.append(prompt)
        return SimpleNamespace(text=f"# Draft {len(self.prompts)}\n\nBody text.")


class FakeCritic:
    """Pretends to be the critic LLM. Returns pre-scripted scores in order."""

    def __init__(self, scores):
        self.scores = list(scores)

    def with_structured_output(self, schema, **kwargs):
        return self

    def with_retry(self, **kwargs):
        return self

    def invoke(self, prompt):
        score = self.scores.pop(0)
        return Critique(problems=["Too vague"], feedback="Be more specific.", score=score)


@pytest.fixture
def run_pipeline(tmp_path, monkeypatch):
    """Returns a function that runs the real graph with fakes and given critic scores."""

    def _run(scores):
        writer = FakeWriter()
        critic = FakeCritic(scores)
        monkeypatch.setattr(graph, "run_research", lambda topic: "- Fact A [https://example.com]")
        monkeypatch.setattr(nodes, "get_llm", lambda: writer)
        monkeypatch.setattr(nodes, "get_critic_llm", lambda: critic)
        monkeypatch.setattr(publish, "OUTPUT_DIR", tmp_path)

        start = {
            "topic": "Test topic", "research": "", "draft": "", "score": 0,
            "feedback": "", "loops": 0, "flagged": False, "output_path": "", "history": [],
        }
        final = graph.build_graph().invoke(start)
        return final, writer

    return _run


def test_publishes_after_first_draft_when_it_passes(run_pipeline):
    final, _ = run_pipeline(scores=[9])
    assert final["loops"] == 1
    assert final["flagged"] is False
    assert "needs-review" not in final["output_path"]


def test_revises_until_score_passes(run_pipeline):
    final, _ = run_pipeline(scores=[5, 7, 9])
    assert final["loops"] == 3
    assert [entry["score"] for entry in final["history"]] == [5, 7, 9]
    assert final["flagged"] is False


def test_stops_at_max_loops_and_flags(run_pipeline):
    final, _ = run_pipeline(scores=[4] * 10)
    assert final["loops"] == MAX_LOOPS
    assert final["flagged"] is True
    assert "needs-review" in final["output_path"]


def test_critic_feedback_reaches_the_writer(run_pipeline):
    _, writer = run_pipeline(scores=[5, 9])
    assert "Be more specific." not in writer.prompts[0]
    assert "Be more specific." in writer.prompts[1]