import os

from dotenv import load_dotenv

load_dotenv()


def _require(var_name: str) -> None:
    """Stop early with a clear message if a required key is missing."""
    if not os.getenv(var_name):
        raise RuntimeError(f"{var_name} is missing. Add it to your .env file.")


def get_llm(model_name: str | None = None):
    """Return a chat model for whichever provider .env selects."""
    provider = os.getenv("LLM_PROVIDER", "gemini")
    model_name = model_name or os.getenv("MODEL_NAME")

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


def get_critic_llm():
    """The judge can use a stronger model than the writer (CRITIC_MODEL in .env)."""
    return get_llm(os.getenv("CRITIC_MODEL"))


def get_crew_llm():
    """Return a CrewAI model for whichever provider .env selects."""
    from crewai import LLM

    provider = os.getenv("LLM_PROVIDER", "gemini")
    model_name = os.getenv("MODEL_NAME")

    if provider == "anthropic":
        _require("ANTHROPIC_API_KEY")
        return LLM(
            model=f"anthropic/{model_name or 'claude-sonnet-5-5'}",
            api_key=os.getenv("ANTHROPIC_API_KEY"),
            max_tokens=4000,
        )

    if provider == "gemini":
        _require("GOOGLE_API_KEY")
        return LLM(
            model=f"gemini/{model_name or 'gemini-2.5-flash'}",
            api_key=os.getenv("GOOGLE_API_KEY"),
            max_tokens=8000,
        )

    raise ValueError(f"Unknown LLM_PROVIDER: {provider}. Use 'gemini' or 'anthropic'.")