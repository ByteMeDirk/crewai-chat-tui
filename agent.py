"""
agent.py - Build and return the single CrewAI conversational agent.

The agent is constructed once at startup and reused across all turns.
Memory and knowledge base are wired in here; tools are imported from the
tools/ package so adding new tools is a one-line change.
"""
from pathlib import Path

from crewai import Agent, Crew, Task, Process, LLM
from crewai.memory import Memory

from config import CFG
from knowledge import load_knowledge_base
from tools.system_info import SystemInfoTool


def _build_llm() -> LLM:
    """Create the local Ollama LLM instance."""
    return LLM(
        model=f"ollama/{CFG['ollama']['model']}",
        base_url=CFG["ollama"]["base_url"],
        temperature=CFG["ollama"]["temperature"],
    )


def _memory_storage_path() -> str:
    """Resolve a storage path inside the configured memory directory."""
    base = Path(__file__).parent / CFG["memory"]["storage_path"]
    base.mkdir(parents=True, exist_ok=True)
    return str(base)


def build_crew() -> Crew:
    """
    Construct a single-agent Crew configured for conversational use.

    Returns a Crew object. Call crew.kickoff(inputs={"message": user_text})
    to get a response.
    """
    llm = _build_llm()
    kb_text = load_knowledge_base()

    backstory = CFG["agent"]["backstory"]
    if kb_text:
        backstory += (
            "\n\nYou have access to the following knowledge base:\n\n"
            + kb_text
        )

    agent = Agent(
        role=CFG["agent"]["role"],
        goal=CFG["agent"]["goal"],
        backstory=backstory,
        llm=llm,
        tools=[SystemInfoTool()],
        verbose=False,          # set True to see CrewAI internals in console
        allow_delegation=False,
        memory=True,
    )

    # One reusable task template; the actual message is injected at runtime.
    task = Task(
        description="Respond helpfully to the user's message: {message}",
        expected_output="A clear, helpful response to the user.",
        agent=agent,
    )

    # crewai 1.x uses a single unified Memory object with a pluggable embedder.
    memory = Memory(
        embedder={
            "provider": "ollama",
            "config": {
                "model": "nomic-embed-text",
                "url": CFG["ollama"]["base_url"] + "/api/embeddings",
            },
        },
        storage=_memory_storage_path(),
    )

    crew = Crew(
        agents=[agent],
        tasks=[task],
        process=Process.sequential,
        memory=memory,
        verbose=False,
    )

    return crew


def chat(crew: Crew, message: str) -> str:
    """
    Send one message to the crew and return the response string.
    This is the only function the TUI needs to call.
    """
    result = crew.kickoff(inputs={"message": message})
    # CrewAI returns a CrewOutput object; .raw holds the plain text.
    return str(result.raw).strip()
