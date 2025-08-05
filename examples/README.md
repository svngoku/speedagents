# DeepAgents Examples

This directory contains examples demonstrating how to use the DeepAgents framework.

## Prerequisites

Before running any examples, you need to set up your API keys for the language models.

### Setting up Anthropic API Key (Default)

The default model uses Anthropic's Claude. Set your API key:

```bash
export ANTHROPIC_API_KEY="your-api-key-here"
```

### Using OpenRouter or Other Models

To use OpenRouter models, you'll need to:

1. Set your OpenRouter API key:
```bash
export OPENROUTER_API_KEY="your-api-key-here"
```

2. Modify the examples to use a different model. For example:
```python
from langchain_openai import ChatOpenAI

# In the create_agent function, specify the model:
agent = create_deep_agent(
    tools=[...],
    instructions="...",
    model=ChatOpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=os.getenv("OPENROUTER_API_KEY"),
        model="meta-llama/llama-3.1-8b-instruct"
    )
)
```

## Available Examples

### 1. Research Agent (`research/research_agent.py`)

A sophisticated research agent that can search the web and compile detailed reports.

**Requirements:**
- Tavily API key for web search: `export TAVILY_API_KEY="your-key"`

**Run:**
```bash
cd research
python research_agent.py
```

### 2. Simple Coding Agent (`coding/simple_coding_agent.py`)

A basic coding assistant that analyzes code and suggests improvements.

**Run:**
```bash
cd coding
python simple_coding_agent.py
```

### 3. Advanced Coding Agent (`coding/coding_agent.py`)

A complex coding agent with multiple subagents for refactoring, testing, and code review.

**Note:** This example may hit recursion limits with complex tasks. Adjust the recursion limit if needed.

**Run:**
```bash
cd coding
python coding_agent.py
```

## Troubleshooting

### Recursion Limit Error

If you encounter a `GraphRecursionError`, try:

1. Increase the recursion limit in the agent configuration:
```python
agent.with_config({"recursion_limit": 100})
```

2. Simplify the task or break it into smaller subtasks

3. Use the simpler examples first to understand the framework

### API Key Errors

If you see authentication errors:

1. Ensure your API key is set correctly
2. Check that the API key has the necessary permissions
3. Verify you're using the correct environment variable name

### Timeout Errors

Some tasks may take longer to complete. You can:

1. Increase the timeout in async operations
2. Use simpler prompts
3. Monitor the agent's progress through the todos it creates

## Creating Your Own Examples

To create your own agent:

1. Import the necessary modules:
```python
from deepagents import create_deep_agent, SubAgent
from langchain_core.tools import tool
```

2. Define custom tools:
```python
@tool
def my_custom_tool(param: str) -> str:
    """Tool description."""
    return f"Processed: {param}"
```

3. Create the agent:
```python
agent = create_deep_agent(
    tools=[my_custom_tool],
    instructions="Your agent instructions here",
    use_default_prompt=True
)
```

4. Run the agent:
```python
result = await agent.ainvoke({
    "messages": [{"role": "user", "content": "Your task here"}]
})
```

## Best Practices

1. **Start Simple**: Begin with basic tools and simple tasks
2. **Use Todos**: Leverage the todo system for complex multi-step tasks
3. **Monitor Progress**: Watch the agent's todo list to understand its progress
4. **Set Limits**: Use recursion limits and timeouts to prevent infinite loops
5. **Test Tools**: Test your custom tools independently before using them in agents
