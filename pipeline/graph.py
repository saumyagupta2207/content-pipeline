from langgraph.graph import END, START, StateGraph
from pipeline.research import run_research
from pipeline.nodes import critique_node, draft_node, publish_node, should_revise
from pipeline.state import ContentState



def research_node(state: ContentState) -> dict:
    """Run the CrewAI research crew and store its brief in the state."""
    return {"research": run_research(state["topic"])}


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