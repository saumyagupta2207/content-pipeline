from pipeline.llm import get_llm
from pipeline.state import ContentState

llm = get_llm()
reply = llm.invoke("Reply with exactly these words: pipeline online")
print("Gemini says:", reply.content)

state: ContentState = {
    "topic": "AI agents",
    "research": "",
    "draft": "",
    "score": 0,
    "feedback": "",
    "loops": 0,
    "flagged": False,
}
print("Starting state:", state)