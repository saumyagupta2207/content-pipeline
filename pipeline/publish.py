import os
import re
from datetime import datetime
from pathlib import Path


OUTPUT_DIR = Path("output")

def slugify(text: str) -> str:
    """'How RAG reduces hallucinations?' -> 'how-rag-reduces-hallucinations'"""
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")[:60]

def extract_title(draft: str, fallback: str) -> str:
    """Return the text of the first '# ' heading, or the fallback."""
    for line in draft.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return fallback

def save_article(state: dict, flagged: bool) -> str:
    """Write the article with frontmatter. Returns the file path as text."""
    now = datetime.now()
    title = extract_title(state["draft"], state["topic"]).replace('"', '\\"')
    topic = state["topic"].replace('"', '\\"')

    folder = OUTPUT_DIR / "needs-review" if flagged else OUTPUT_DIR
    folder.mkdir(parents=True, exist_ok=True)

    filename = f"{now:%Y-%m-%d-%H%M}-{slugify(state['topic'])}.md"
    path = folder / filename

    frontmatter = (
        "---\n"
        f'title: "{title}"\n'
        f"date: {now:%Y-%m-%d}\n"
        f'topic: "{topic}"\n'
        f"score: {state['score']}\n"
        f"drafts: {state['loops']}\n"
        f"flagged: {str(flagged).lower()}\n"
        f"model: {os.getenv('MODEL_NAME')}\n"
        f"critic_model: {os.getenv('CRITIC_MODEL') or os.getenv('MODEL_NAME')}\n"
        "---\n\n"
    )

    path.write_text(frontmatter + state["draft"], encoding="utf-8")
    return str(path)