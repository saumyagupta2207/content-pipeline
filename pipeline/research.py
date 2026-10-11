from crewai import Agent, Crew, Process, Task

from pipeline.llm import get_crew_llm
from pipeline.tools import web_search_tool


def build_research_crew(verbose: bool = False) -> Crew:
    llm = get_crew_llm()

    searcher = Agent(
        role="Web Researcher",
        goal="Find 4-6 reliable, relevant sources about: {topic}",
        backstory=(
            "You are a careful researcher. You prefer primary sources such as papers, "
            "official documentation and engineering blogs over generic marketing pages."
        ),
        tools=[web_search_tool],
        llm=llm,
        max_iter=6,
        allow_delegation=False,
        verbose=verbose,
    )

    analyst = Agent(
        role="Fact Analyst",
        goal="Extract specific, verifiable facts about {topic} from the sources found",
        backstory=(
            "You are skeptical. You only keep facts that a source actually states, "
            "you drop duplicates and vague claims, and you note where sources disagree."
        ),
        llm=llm,
        allow_delegation=False,
        verbose=verbose,
    )

    brief_writer = Agent(
        role="Research Brief Writer",
        goal="Turn verified facts about {topic} into a clear research brief for a writer",
        backstory="You write concise, well-organised briefs. Every fact keeps its source URL.",
        llm=llm,
        allow_delegation=False,
        verbose=verbose,
    )
    search_task = Task(
        description=(
            "Search the web for information on: {topic}. "
            "Run 2-4 different, specific queries (not the same query reworded). "
            "Pick the 4-6 most relevant and reliable results."
        ),
        expected_output=(
            "A list of 4-6 sources. For each: title, URL, and the key points from its snippet."
        ),
        agent=searcher,
    )

    analysis_task = Task(
        description=(
            "From the sources provided, extract 8-12 specific facts that help explain {topic}. "
            "Keep only facts a source actually states. Remove duplicates "
            "(the same paper at two URLs counts once). Note any disagreements between sources."
        ),
        expected_output="A list of facts, each followed by its source URL in brackets.",
        agent=analyst,
        context=[search_task],
    )

    brief_task = Task(
        description=(
            "Write a research brief on {topic} for an article writer, using only the analyst's facts."
        ),
        expected_output=(
            "A Markdown brief with three sections:\n"
            "## Key facts: bullet points, each ending with [source URL]\n"
            "## Disagreements or uncertainties: bullets, or 'None found'\n"
            "## Sources: numbered list of titles and URLs"
        ),
        agent=brief_writer,
        context=[analysis_task],
    )

    return Crew(
        agents=[searcher, analyst, brief_writer],
        tasks=[search_task, analysis_task, brief_task],
        process=Process.sequential,
        verbose=verbose,
    )

def run_research(topic: str, verbose: bool = False) -> str:
    """Run the research crew and return the brief as text."""
    crew = build_research_crew(verbose=verbose)
    result = crew.kickoff(inputs={"topic": topic})
    return result.raw