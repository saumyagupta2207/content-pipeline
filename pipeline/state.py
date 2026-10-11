from typing import TypedDict


class ContentState(TypedDict):
    topic: str        # what the article is about (the input)
    research: str     # findings from the research crew
    draft: str        # the current article draft
    score: int        # critic's score out of 10
    feedback: str     # critic's notes on what to improve
    loops: int        # how many revision rounds have run
    flagged: bool     # True if we published only because we hit the loop limit