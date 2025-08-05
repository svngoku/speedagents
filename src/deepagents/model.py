from langchain_anthropic import ChatAnthropic
from langchain_cerebras import ChatCerebras
from typing import Literal, Optional
from dotenv import load_dotenv

load_dotenv()

def get_default_model():
    """Get the default model (Claude)."""
    return ChatAnthropic(model_name="claude-sonnet-4-20250514", max_tokens=64000)


def get_cerebras_model(model: str = "qwen-3-235b-a22b-instruct-2507", **kwargs):
    """Get a Cerebras model instance.
    
    Args:
        model: The Cerebras model to use (default: qwen-3-235b-a22b-instruct-2507)
        **kwargs: Additional parameters to pass to ChatCerebras
    
    Returns:
        ChatCerebras instance
    """
    return ChatCerebras(model=model, **kwargs)


def get_model(
    provider: Literal["claude", "cerebras"] = "claude",
    model: Optional[str] = None,
    **kwargs
):
    """Get a model instance from the specified provider.
    
    Args:
        provider: The model provider to use ("claude" or "cerebras")
        model: Specific model name (uses provider defaults if not specified)
        **kwargs: Additional parameters to pass to the model
    
    Returns:
        Model instance from the specified provider
    """
    if provider == "claude":
        if model is None:
            model = "claude-sonnet-4-20250514"
        return ChatAnthropic(model_name=model, max_tokens=64000, **kwargs)
    elif provider == "cerebras":
        if model is None:
            model = "qwen-3-235b-a22b-instruct-2507"
        return ChatCerebras(model=model, max_tokens=64000, **kwargs)
    else:
        raise ValueError(f"Unsupported provider: {provider}. Use 'claude' or 'cerebras'.")