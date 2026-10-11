"""Summarise every run record in runs/ into headline metrics."""

import json
from pathlib import Path
from statistics import mean

from pipeline.nodes import PASS_SCORE

RUNS_DIR = Path("runs")


def load_runs() -> list[dict]:
    """Read every JSON run record, oldest first."""
    return [
        json.loads(path.read_text(encoding="utf-8"))
        for path in sorted(RUNS_DIR.glob("*.json"))
    ]


def pct(part: int, whole: int) -> str:
    return f"{part}/{whole} ({part / whole:.0%})"


def main() -> None:
    runs = load_runs()
    ok = [r for r in runs if r["status"] == "ok" and r["scores"]]
    if not ok:
        print("No successful runs found in runs/.")
        return

    revised = [r for r in ok if len(r["scores"]) > 1]
    first_pass = [r for r in ok if r["scores"][0] >= PASS_SCORE]
    flagged = [r for r in ok if r["flagged"]]

    rows = [
        ("Runs analysed", f"{len(ok)} successful of {len(runs)} total"),
        ("Passed on first draft", pct(len(first_pass), len(ok))),
        ("Needed revision", pct(len(revised), len(ok))),
        ("Flagged for human review", pct(len(flagged), len(ok))),
        ("Average drafts per article", f"{mean(r['drafts'] for r in ok):.1f}"),
        ("Average first-draft score", f"{mean(r['scores'][0] for r in ok):.1f}/10"),
        ("Average final score", f"{mean(r['final_score'] for r in ok):.1f}/10"),
    ]
    if revised:
        gain = mean(r["scores"][-1] - r["scores"][0] for r in revised)
        rows.append(("Average score gain when revised", f"{gain:+.1f} points"))
    rows.append(("Average time per article", f"{mean(r['total_seconds'] for r in ok):.0f}s"))

    print("| Metric | Value |")
    print("|---|---|")
    for name, value in rows:
        print(f"| {name} | {value} |")

    totals: dict[str, float] = {}
    for r in ok:
        for step in r["steps"]:
            totals[step["node"]] = totals.get(step["node"], 0) + step["seconds"]
    grand_total = sum(totals.values())

    print("\nTime by step:")
    for node, seconds in sorted(totals.items(), key=lambda item: item[1], reverse=True):
        print(f"  {node:<10} {seconds / grand_total:>5.0%}")


if __name__ == "__main__":
    main()