from langgraph.graph import END, START, StateGraph

from pipeline.nodes import critique_node, draft_node, publish_node, should_revise
from pipeline.state import ContentState

SAMPLE_RESEARCH = (
    "- AI agents can call tools and take actions, not just answer questions.\n"
    "- Common failures: looping forever, calling the wrong tool, inventing facts.\n"
    "- Guardrails include step limits, output validation, and human approval for risky actions.\n"
    "- Production teams log every agent step so failures can be traced."
)


def research_node(state: ContentState) -> dict:
    """Placeholder until v0.4, when the CrewAI research crew replaces it."""
    return {"research": SAMPLE_RESEARCH}


def build_graph():
    graph = StateGraph(ContentState)

    graph.add_node("researcher", research_node)
    graph.add_node("writer", draft_node)
    graph.add_node("critic", critique_node)
    graph.add_node("publisher", publish_node)

    graph.add_edge(START, "researcher")
    graph.add_edge("researcher", "writer")
    graph.add_edge("writer", "critic")
    graph.add_conditional_edges(
        "critic",
        should_revise,
        {"revise": "writer", "publish": "publisher"},
    )
    graph.add_edge("publisher", END)

    return graph.compile()