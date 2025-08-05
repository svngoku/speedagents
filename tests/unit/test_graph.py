"""Unit tests for the graph module."""

import pytest
from deepagents import create_deep_agent
from deepagents.state import DeepAgentState
from deepagents.sub_agent import SubAgent


@pytest.mark.unit
def test_create_deep_agent_basic():
    """Test basic creation of a deep agent."""
    agent = create_deep_agent(
        tools=[],
        instructions="Test agent"
    )
    assert agent is not None


@pytest.mark.unit
def test_create_deep_agent_with_custom_prompt():
    """Test creation with custom system prompt."""
    custom_prompt = "You are a custom agent with specific instructions."
    agent = create_deep_agent(
        tools=[],
        instructions="Base instructions",
        system_prompt=custom_prompt,
        use_default_prompt=False
    )
    assert agent is not None


@pytest.mark.unit
def test_create_deep_agent_with_subagents():
    """Test creation with subagents."""
    test_subagent = SubAgent(
        name="test-agent",
        description="A test subagent",
        prompt="You are a test agent"
    )
    
    agent = create_deep_agent(
        tools=[],
        instructions="Main agent instructions",
        subagents=[test_subagent]
    )
    assert agent is not None


@pytest.mark.unit
def test_create_deep_agent_with_human_in_the_loop():
    """Test creation with human-in-the-loop callback."""
    def human_callback(event: str, message: str):
        print(f"Human callback: {event} - {message}")
    
    agent = create_deep_agent(
        tools=[],
        instructions="Agent with human feedback",
        human_in_the_loop=human_callback
    )
    assert agent is not None


@pytest.mark.unit
def test_create_deep_agent_without_default_prompt():
    """Test creation without default prompt."""
    agent = create_deep_agent(
        tools=[],
        instructions="Only these instructions",
        use_default_prompt=False
    )
    assert agent is not None
