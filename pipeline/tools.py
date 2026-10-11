from crewai.tools import tool
from ddgs import DDGS


def search_web(query: str, max_results: int = 5) -> str:
    """Search DuckDuckGo and return results as readable text."""
    try:
        results = DDGS().text(query, max_results=max_results)
    except Exception as error:
        return f"Search failed ({error}). Try a shorter or different query."

    if not results:
        return "No results found. Try a different query."

    formatted = []
    for result in results:
        formatted.append(
            f"Title: {result['title']}\n"
            f"URL: {result['href']}\n"
            f"Snippet: {result['body']}"
        )
    return "\n\n".join(formatted)


@tool("web_search")
def web_search_tool(query: str) -> str:
    """Search the web for current information. Input: a short, specific search query
    (e.g. 'RAG hallucination reduction study'). Returns titles, URLs and snippets."""
    return search_web(query)