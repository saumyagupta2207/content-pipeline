from pathlib import Path

from pipeline import publish
from pipeline.publish import extract_title, save_article, slugify


def test_slugify_removes_unsafe_characters():
    assert slugify('What is "RAG"? A guide: part 1') == "what-is-rag-a-guide-part-1"


def test_slugify_limits_length():
    assert len(slugify("word " * 50)) <= 60


def test_extract_title_finds_h1():
    assert extract_title("Intro\n# My Title\nBody", "fallback") == "My Title"


def test_extract_title_uses_fallback():
    assert extract_title("No heading here", "fallback") == "fallback"


def test_save_article_routes_flagged_and_writes_frontmatter(tmp_path, monkeypatch):
    monkeypatch.setattr(publish, "OUTPUT_DIR", tmp_path)
    state = {
        "topic": "Test topic",
        "draft": '# A "quoted" title\n\nBody with an em dash \u2014 here.',
        "score": 6,
        "loops": 3,
    }

    path = save_article(state, flagged=True)
    content = Path(path).read_text(encoding="utf-8")

    assert "needs-review" in path
    assert content.startswith("---\n")
    assert 'title: "A \\"quoted\\" title"' in content
    assert "flagged: true" in content
    assert "em dash \u2014 here" in content