import logging
import os
import sys
import time
from datetime import datetime

from pipeline.graph import build_graph
from pipeline.runlog import save_run

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname)-5s %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
for noisy in ("httpx", "httpcore", "anthropic"):
    logging.getLogger(noisy).setLevel(logging.WARNING)

logger = logging.getLogger("main")


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
        "output_path": "",
        "history": [],
    }

    app = build_graph()
    steps = []
    error = None
    started_at = datetime.now()
    started = time.perf_counter()
    last = started

    logger.info("Starting pipeline: %s", topic)
    try:
        for step in app.stream(state, stream_mode="updates"):
            for node_name, update in step.items():
                now = time.perf_counter()
                seconds = round(now - last, 1)
                last = now

                for key, value in update.items():
                    if key == "history":
                        state["history"] = state["history"] + value
                    else:
                        state[key] = value

                steps.append({"node": node_name, "seconds": seconds})
                logger.info("[%s] done in %.1fs", node_name, seconds)
    except Exception as exc:
        error = f"{type(exc).__name__}: {exc}"
        logger.exception("Pipeline failed")
    finally:
        record = {
            "status": "failed" if error else "ok",
            "error": error,
            "topic": topic,
            "started_at": started_at.isoformat(timespec="seconds"),
            "total_seconds": round(time.perf_counter() - started, 1),
            "model": os.getenv("MODEL_NAME"),
            "critic_model": os.getenv("CRITIC_MODEL") or os.getenv("MODEL_NAME"),
            "drafts": state["loops"],
            "scores": [entry["score"] for entry in state["history"]],
            "final_score": state["score"],
            "flagged": state["flagged"],
            "research_chars": len(state["research"]),
            "output_path": state["output_path"],
            "steps": steps,
            "history": state["history"],
        }
        run_path = save_run(record)
        logger.info("Run record saved: %s", run_path)

    if error:
        sys.exit(1)

    scores = " -> ".join(str(s) for s in record["scores"])
    print("\n" + "=" * 60)
    print(f"Topic:    {topic}")
    print(f"Scores:   {scores}")
    print(f"Flagged:  {state['flagged']}")
    print(f"Time:     {record['total_seconds']}s")
    print(f"Article:  {state['output_path']}")
    print(f"Run log:  {run_path}")
    print("=" * 60)


if __name__ == "__main__":
    main()