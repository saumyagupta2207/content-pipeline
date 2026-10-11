import os

from dotenv import load_dotenv

load_dotenv()


def _require(var_name: str) -> None:
    """Stop early with a clear message if a required key is missing."""
    if not os.getenv(var_name):
        raise RuntimeError(f"{var_name} is missing. Add it to your .env file.")


def get_llm():
    """Return a chat model for whichever provider .env selects."""
    provider = os.getenv("LLM_PROVIDER", "gemini")
    model_name = os.getenv("MODEL_NAME")

    if provider == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI

        _require("GOOGLE_API_KEY")
        return ChatGoogleGenerativeAI(
            model=model_name or "gemini-2.5-flash",
            max_output_tokens=8000,
            max_retries=3,
        )

    if provider == "anthropic":
        from langchain_anthropic import ChatAnthropic

        _require("ANTHROPIC_API_KEY")
        return ChatAnthropic(model=model_name or "claude-sonnet-5-5", max_tokens=8000)

    raise ValueError(f"Unknown LLM_PROVIDER: {provider}. Use 'gemini' or 'anthropic'.")