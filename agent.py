"""
agent.py - Build the conversational agent and manage chat history.

Uses Agent.kickoff() directly (no Crew wrapper) so that:
  - Conversation history is maintained across turns.
  - The redundant post-turn extract_memories() LLM call is suppressed.
  - Memory tools (search_memory / save_to_memory) are still available.
"""
from pathlib import Path
from typing import TypedDict

from crewai import Agent, LLM
from crewai.memory import Memory
from crewai.memory.storage.lancedb_storage import LanceDBStorage

from config import CFG
from knowledge import load_knowledge_base
from log import logger
from tools.system_info import SystemInfoTool


class Message(TypedDict):
    role: str  # "user" or "assistant"
    content: str


def _build_llm() -> LLM:
    return LLM(
        model=f"ollama/{CFG['ollama']['model']}",
        base_url=CFG["ollama"]["base_url"],
        temperature=CFG["ollama"]["temperature"],
    )


def _build_memory_llm() -> LLM:
    """Smaller LLM used only for memory scope/importance analysis."""
    model = CFG["memory"].get("memory_model", CFG["ollama"]["model"])
    return LLM(
        model=f"ollama/{model}",
        base_url=CFG["ollama"]["base_url"],
        temperature=0.0,  # deterministic — memory analysis doesn't benefit from creativity
    )


def _memory_storage_path() -> str:
    base = Path(__file__).parent / CFG["memory"]["storage_path"]
    base.mkdir(parents=True, exist_ok=True)
    return str(base)


def build_agent() -> Agent:
    """
    Build and return a configured Agent ready for direct kickoff().

    Memory tools (search_memory / save_to_memory) are injected automatically.
    The automatic post-turn extract_memories() call is patched out to avoid
    a redundant second LLM inference on every response.
    """
    logger.info(
        "Building agent: model=%s base_url=%s",
        CFG["ollama"]["model"],
        CFG["ollama"]["base_url"],
    )

    llm = _build_llm()
    kb_text = load_knowledge_base()
    logger.info("Knowledge base loaded (%d chars)", len(kb_text))

    backstory = CFG["agent"]["backstory"]
    if kb_text:
        backstory += (
                "\n\nYou have access to the following knowledge base:\n\n" + kb_text
        )

    storage = LanceDBStorage(
        path=_memory_storage_path(),
        vector_dim=768,  # nomic-embed-text output dimension
    )
    memory_llm = _build_memory_llm()
    logger.info("Memory LLM: %s", CFG["memory"].get("memory_model", CFG["ollama"]["model"]))

    memory = Memory(
        llm=memory_llm,
        embedder={
            "provider": "ollama",
            "config": {
                "model_name": "nomic-embed-text",
                "url": CFG["ollama"]["base_url"] + "/api/embeddings",
            },
        },
        storage=storage,
    )

    agent = Agent(
        role=CFG["agent"]["role"],
        goal=CFG["agent"]["goal"],
        backstory=backstory,
        llm=llm,
        tools=[SystemInfoTool()],
        verbose=False,
        allow_delegation=False,
        memory=memory,
    )

    # Suppress the automatic post-turn extract_memories() call on the lite_agent
    # layer. That call makes a second LLM inference after every response, doubling
    # latency. The agent still has save_to_memory / search_memory tools and will
    # save what it decides is worth remembering.
    agent._save_to_memory = lambda *_a, **_kw: None  # type: ignore[method-assign]
    logger.debug("Disabled automatic _save_to_memory on agent")

    return agent


def chat(agent: Agent, history: list[Message], message: str) -> str:
    """
    Send one message, maintain history, return the response string.

    Args:
        agent:   The Agent returned by build_agent().
        history: Running list of {"role": ..., "content": ...} dicts.
                 Modified in-place: the new user message and assistant
                 response are appended before returning.
        message: The user's current message text.

    Returns:
        The agent's response as a plain string.
    """
    logger.info("User message (%d chars): %s", len(message), message[:120])

    history.append({"role": "user", "content": message})

    try:
        # Pass the full conversation history so the agent has context.
        result = agent.kickoff(messages=history)
        response = str(result.raw).strip()
    except Exception:
        history.pop()  # remove the failed user message so history stays clean
        logger.error("agent.kickoff failed", exc_info=True)
        raise

    history.append({"role": "assistant", "content": response})
    logger.info("Agent response (%d chars): %s", len(response), response[:120])
    return response
