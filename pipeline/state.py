import operator
from typing import Annotated, TypedDict


class ContentState(TypedDict):
    topic: str
    research: str
    draft: str
    score: int
    feedback: str
    loops: int
    flagged: bool
    output_path: str
    history: Annotated[list, operator.add]  # one entry per critique round