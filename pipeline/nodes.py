from pydantic import BaseModel, Field

from pipeline.llm import get_llm
from pipeline.state import ContentState

MAX_LOOPS = 3     # most drafts we'll ever write
PASS_SCORE = 8    # score needed to publish without a flag

class Critique(BaseModel):
    problems: list[str] = Field(description="Every concrete problem found, most serious first")
    feedback: str = Field(description="Specific changes the writer should make")
    score: int = Field(description="Quality score from 1 to 10, decided after listing the problems")

def draft_node(state: ContentState) -> dict:
    """Write the first draft, or revise using the critic's feedback."""
    llm = get_llm()

    if state["feedback"]:
        prompt = f"""Revise this blog article using the editor's feedback.

Research (the only source of facts):
{state["research"]}

Current draft:
{state["draft"]}

Editor feedback:
{state["feedback"]}

Return only the revised article in Markdown."""
    else:
        prompt = f"""Write a blog article of about 600 words on "{state["topic"]}".
Use only facts from this research:
{state["research"]}

Return only the article in Markdown."""

    response = llm.invoke(prompt)
    return {"draft": response.text, "loops": state["loops"] + 1}

RUBRIC = """Start at 10 and deduct points:
- Generic or cliche opening (e.g. "The world of X is rapidly evolving"): -2
- Any claim NOT supported by the research: -3 each
- Filler sentences that add no information: -1 each (max -3)
- No clear conclusion or takeaway: -1
- Weak structure (no headings, rambling paragraphs): -1
A 9 or 10 should be rare: publish-ready with nothing worth changing.
Feedback must list specific changes, not praise."""


def critique_node(state: ContentState) -> dict:
    """Score the draft against the rubric and explain what to fix."""
    critic = get_llm().with_structured_output(Critique, method="json_schema").with_retry(
        stop_after_attempt=3
    )

    result = critic.invoke(f"""You are a strict editor.
{RUBRIC}

Research the article should be based on:
{state["research"]}

Article:
{state["draft"]}""")
    print("Problems found:", result.problems)

    score = max(1, min(10, result.score))
    return {"score": score, "feedback": result.feedback}

def should_revise(state: ContentState) -> str:
    """Decide where to go after critique: 'publish' or 'revise'."""
    if state["score"] >= PASS_SCORE:
        return "publish"
    if state["loops"] >= MAX_LOOPS:
        return "publish"
    return "revise"


def publish_node(state: ContentState) -> dict:
    """Final step. Flag the article if it never reached the pass score."""
    return {"flagged": state["score"] < PASS_SCORE}