from pydantic import BaseModel, Field
import logging

from pipeline.llm import get_critic_llm, get_llm
from pipeline.state import ContentState
from pipeline.publish import save_article
logger = logging.getLogger(__name__)

MAX_LOOPS = 3     # most drafts we'll ever write
PASS_SCORE = 8    # score needed to publish without a flag

WRITER_RULES = """Rules:
- Start with a single "# " title, then directly explain the topic. Do not change or broaden it.
- Specific facts (numbers, study results, named findings) must come from the research brief.
  Attribute them naturally, e.g. "The OWASP entry describes...".
- You may explain mechanisms, give illustrative examples and use analogies in your own words.
- Do not present anything the brief marks as uncertain as settled fact.
- Do not add disclaimers about your own writing (e.g. "this example is illustrative",
  "this is my view", "not from the sources"). Write like a confident, careful journalist.
- End with a "## Sources" section listing the URLs you actually used."""

class Critique(BaseModel):
    problems: list[str] = Field(description="Every concrete problem found, most serious first")
    feedback: str = Field(description="Specific changes the writer should make")
    score: int = Field(description="Quality score from 1 to 10, decided after listing the problems")

def draft_node(state: ContentState) -> dict:
    """Write the first draft, or revise using the critic's feedback."""
    llm = get_llm()

    if state["feedback"]:
            prompt = f"""Revise this blog article on "{state["topic"]}" using the editor's feedback.

{WRITER_RULES}

Research brief:
{state["research"]}

Current draft:
{state["draft"]}

Editor feedback:
{state["feedback"]}

Return only the revised article in Markdown."""
    else:
        prompt = f"""Write a blog article of about 600 words on "{state["topic"]}".

{WRITER_RULES}

Research brief:
{state["research"]}

Return only the article in Markdown."""

    response = llm.invoke(prompt)
    return {"draft": response.text, "loops": state["loops"] + 1}

RUBRIC = """First check: does the article directly explain the topic "{topic}"?
If it avoids the topic, changes it, or only covers it loosely, the score is AT MOST 3.

Otherwise start at 10 and deduct points:
- A specific factual claim (number, study result, named finding, date) that is NOT in
  the research, or that contradicts it: -3 each
- Presenting something the research marks as uncertain or unverified as settled fact: -2
- Generic or cliche opening: -2
- Filler sentences that add no information: -1 each (max -3)
- No clear conclusion or takeaway: -1
- Weak structure (no headings, rambling paragraphs): -1

Do NOT deduct for:
- Explaining how something works, illustrative examples, or analogies,
  as long as they do not introduce new factual claims
- Reasonable reasoning that connects facts from the research
- The required "## Sources" section at the end

A 9 or 10 should be rare. Feedback must list specific changes, not praise.
Never ask for anything that the rules above would penalise.
Only report problems that match a rule above AND that a reader would actually notice.
Do not invent new categories of problems."""

def critique_node(state: ContentState) -> dict:
    """Score the draft against the rubric and explain what to fix."""
    critic = get_critic_llm().with_structured_output(Critique, method="json_schema").with_retry(
        stop_after_attempt=3
    )

    result = critic.invoke(f"""You are a strict editor.
{RUBRIC.format(topic=state["topic"])}

Research the article should be based on:
{state["research"]}

Article:
{state["draft"]}""")

    score = max(1, min(10, result.score))
    logger.info("Draft %d scored %d/10 (%d problems)", state["loops"], score, len(result.problems))
    for problem in result.problems:
        logger.debug("  problem: %s", problem)

    return {
        "score": score,
        "feedback": result.feedback,
        "history": [{"draft": state["loops"], "score": score, "problems": result.problems}],
    }

def should_revise(state: ContentState) -> str:
    """Decide where to go after critique: 'publish' or 'revise'."""
    if state["score"] >= PASS_SCORE:
        return "publish"
    if state["loops"] >= MAX_LOOPS:
        return "publish"
    return "revise"


def publish_node(state: ContentState) -> dict:
    """Final step: save the article. Flagged articles go to needs-review."""
    flagged = state["score"] < PASS_SCORE
    path = save_article(state, flagged)
    return {"flagged": flagged, "output_path": path}