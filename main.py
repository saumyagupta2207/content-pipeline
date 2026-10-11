import sys

from pipeline.graph import build_graph


def main() -> None:
    topic = sys.argv[1] if len(sys.argv) > 1 else "Why AI agents need guardrails"

    state = {
        "topic": topic,
        "research": "",
        "draft": "",
        "score": 0,
        "feedback": "",
        "loops": 0,
        "flagged": False,
    }

    app = build_graph()

    for step in app.stream(state, stream_mode="updates"):
        for node_name, update in step.items():
            state.update(update)
            print(f"[{node_name}] done", end="")
            if node_name == "writer":
                print(f"  -> draft #{state['loops']}", end="")
            if node_name == "critic":
                print(f"  -> score {state['score']}/10", end="")
            print()

    print("\n" + "=" * 60)
    print(f"Topic:   {state['topic']}")
    print(f"Drafts:  {state['loops']}")
    print(f"Score:   {state['score']}/10")
    print(f"Flagged: {state['flagged']}")
    print("=" * 60 + "\n")
    print(state["draft"])


if __name__ == "__main__":
    main()