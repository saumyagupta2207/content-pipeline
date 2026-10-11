"""Quick check that your API key and model settings work (1 cheap API call)."""

from pipeline.llm import get_llm

reply = get_llm().invoke("Reply with exactly these words: pipeline online")
print("Model says:", reply.text)