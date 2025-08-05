from deepagents.sub_agent import _create_task_tool, SubAgent
from deepagents.model import get_default_model, get_model
from deepagents.tools import write_todos, write_file, read_file, ls, edit_file
from deepagents.state import DeepAgentState
from typing import Sequence, Union, Callable, Any, TypeVar, Type, Optional, Dict, List
from langchain_core.tools import BaseTool
from langchain_core.language_models import LanguageModelLike
from langgraph.graph import StateGraph
from langgraph.prebuilt import create_react_agent
from dotenv import load_dotenv

load_dotenv()

StateSchema = TypeVar("StateSchema", bound=DeepAgentState)
StateSchemaType = Type[StateSchema]

DEFAULT_BASE_PROMPT = """You have access to a number of standard tools

## `write_todos`

You have access to the `write_todos` tools to help you manage and plan tasks. Use these tools VERY frequently to ensure that you are tracking your tasks and giving the user visibility into your progress.
These tools are also EXTREMELY helpful for planning tasks, and for breaking down larger complex tasks into smaller steps. If you do not use this tool when planning, you may forget to do important tasks - and that is unacceptable.

It is critical that you mark todos as completed as soon as you are done with a task. Do not batch up multiple tasks before marking them as completed.
## `task`

- When doing web search, prefer to use the `task` tool in order to reduce context usage."""


def create_deep_agent(
    tools: Sequence[Union[BaseTool, Callable, Dict[str, Any]]],
    instructions: str,
    model: Optional[Union[str, LanguageModelLike]] = None,
    subagents: Optional[List[SubAgent]] = None,
    state_schema: Optional[StateSchemaType] = None,
    system_prompt: Optional[str] = None,
    use_default_prompt: bool = True,
    human_in_the_loop: Optional[Callable] = None,
) -> StateGraph:
    """Create a deep agent with enhanced capabilities.

    This agent will by default have access to a tool to write todos (write_todos),
    and then four file editing tools: write_file, ls, read_file, edit_file.

    Args:
        tools: The additional tools the agent should have access to.
        instructions: The additional instructions the agent should have. Will go in
            the system prompt.
        model: The model to use. If None, uses the default model.
        subagents: The subagents to use. Each subagent should be a dictionary with the
            following keys:
                - `name`: Name of the subagent
                - `description`: Used by the main agent to decide whether to call the sub agent
                - `prompt`: Used as the system prompt in the subagent
                - `tools` (optional): List of tool names available to this subagent
        state_schema: The schema of the deep agent. Should subclass from DeepAgentState.
        system_prompt: Custom system prompt to completely override the default.
        use_default_prompt: Whether to append the default base prompt to instructions.
        human_in_the_loop: Optional callback for human intervention during execution.

    Returns:
        StateGraph: A configured LangGraph agent.
    """
    # Build the prompt based on configuration
    if system_prompt is not None:
        # Use custom system prompt entirely
        prompt = system_prompt
    elif use_default_prompt:
        # Combine instructions with default base prompt
        prompt = instructions + "\n\n" + DEFAULT_BASE_PROMPT
    else:
        # Use only the provided instructions
        prompt = instructions

    # Initialize built-in tools
    built_in_tools = [write_todos, write_file, read_file, ls, edit_file]

    # Initialize model if not provided
    if model is None:
        model = get_model(provider="cerebras")

    # Initialize state schema if not provided
    state_schema = state_schema or DeepAgentState

    # Create task tool with subagents
    task_tool = _create_task_tool(
        list(tools) + built_in_tools,
        instructions,
        subagents or [],
        model,
        state_schema,
        human_in_the_loop=human_in_the_loop,
    )

    # Combine all tools
    all_tools = built_in_tools + list(tools) + [task_tool]

    # Create and return the agent
    return create_react_agent(
        model,
        prompt=prompt,
        tools=all_tools,
        state_schema=state_schema,
    )
