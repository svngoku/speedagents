"""Enhanced virtual filesystem tools for deep agents."""

from typing import Dict, List, Optional, Annotated
from langchain_core.tools import tool
from langgraph.prebuilt import InjectedState
from langgraph.types import Command
from langchain_core.messages import ToolMessage
from langchain_core.tools import InjectedToolCallId
from deepagents.state import DeepAgentState, VirtualFile, FileMetadata
from datetime import datetime
import os


@tool
def mkdir(
    path: str,
    state: Annotated[DeepAgentState, InjectedState],
    tool_call_id: Annotated[str, InjectedToolCallId],
) -> Command:
    """Create a directory in the virtual filesystem."""
    vfs = state.get(
        "virtual_fs", {"files": {}, "directories": [], "current_directory": "/"}
    )

    # Normalize path
    if not path.startswith("/"):
        path = os.path.join(vfs["current_directory"], path)

    if path in vfs["directories"]:
        return Command(
            update={
                "messages": [
                    ToolMessage(
                        f"Directory {path} already exists", tool_call_id=tool_call_id
                    )
                ],
            }
        )

    vfs["directories"].append(path)
    # Create parent directories if needed
    parent = os.path.dirname(path)
    while parent and parent != "/" and parent not in vfs["directories"]:
        vfs["directories"].append(parent)
        parent = os.path.dirname(parent)

    return Command(
        update={
            "virtual_fs": vfs,
            "messages": [
                ToolMessage(f"Created directory {path}", tool_call_id=tool_call_id)
            ],
        }
    )


@tool
def cd(
    path: str,
    state: Annotated[DeepAgentState, InjectedState],
    tool_call_id: Annotated[str, InjectedToolCallId],
) -> Command:
    """Change current directory in the virtual filesystem."""
    vfs = state.get(
        "virtual_fs", {"files": {}, "directories": ["/"], "current_directory": "/"}
    )

    # Handle relative and absolute paths
    if path == "..":
        new_path = os.path.dirname(vfs["current_directory"])
    elif path.startswith("/"):
        new_path = path
    else:
        new_path = os.path.join(vfs["current_directory"], path)

    # Normalize path
    new_path = os.path.normpath(new_path)

    # Check if directory exists
    if new_path != "/" and new_path not in vfs["directories"]:
        return Command(
            update={
                "messages": [
                    ToolMessage(
                        f"Directory {new_path} does not exist",
                        tool_call_id=tool_call_id,
                    )
                ],
            }
        )

    vfs["current_directory"] = new_path
    return Command(
        update={
            "virtual_fs": vfs,
            "messages": [
                ToolMessage(
                    f"Changed directory to {new_path}", tool_call_id=tool_call_id
                )
            ],
        }
    )


@tool
def pwd(
    state: Annotated[DeepAgentState, InjectedState],
) -> str:
    """Print working directory."""
    vfs = state.get("virtual_fs", {"current_directory": "/"})
    return vfs["current_directory"]


@tool
def ls_enhanced(
    state: Annotated[DeepAgentState, InjectedState],
    path: Optional[str] = None,
) -> str:
    """List files and directories with metadata."""
    vfs = state.get(
        "virtual_fs", {"files": {}, "directories": [], "current_directory": "/"}
    )

    # Use current directory if no path specified
    if path is None:
        path = vfs["current_directory"]
    elif not path.startswith("/"):
        path = os.path.join(vfs["current_directory"], path)

    # Normalize path
    path = os.path.normpath(path)

    # List contents
    contents = []

    # Add directories
    for dir_path in sorted(vfs["directories"]):
        if os.path.dirname(dir_path) == path:
            contents.append(f"d rwxr-xr-x  {os.path.basename(dir_path)}/")

    # Add files
    for file_path, file_data in sorted(vfs["files"].items()):
        if os.path.dirname(file_path) == path:
            if isinstance(file_data, dict) and "metadata" in file_data:
                metadata = file_data["metadata"]
                size = metadata.get("size", 0)
                perms = metadata.get("permissions", "rw-r--r--")
                contents.append(f"- {perms}  {size:8d}  {os.path.basename(file_path)}")
            else:
                # Legacy file format
                size = len(file_data) if isinstance(file_data, str) else 0
                contents.append(
                    f"- rw-r--r--  {size:8d}  {os.path.basename(file_path)}"
                )

    if not contents:
        return f"Directory {path} is empty"

    return "\n".join(contents)


@tool
def file_history(
    file_path: str,
    state: Annotated[DeepAgentState, InjectedState],
) -> str:
    """Show version history of a file."""
    vfs = state.get("virtual_fs", {"files": {}})

    # Normalize path
    if not file_path.startswith("/"):
        current_dir = vfs.get("current_directory", "/")
        file_path = os.path.join(current_dir, file_path)

    if file_path not in vfs["files"]:
        # Check legacy files
        files = state.get("files", {})
        if file_path in files:
            return "File exists but has no version history (legacy format)"
        return f"File {file_path} not found"

    file_data = vfs["files"][file_path]
    if not isinstance(file_data, dict) or "metadata" not in file_data:
        return "File has no version history"

    metadata = file_data["metadata"]
    history = file_data.get("history", [])

    result = [f"Current version: {metadata['version']}"]
    result.append(f"Modified: {metadata['modified_at']}")
    result.append(f"Size: {metadata['size']} bytes")

    if history:
        result.append("\nVersion history:")
        for i, version in enumerate(reversed(history[-5:])):  # Show last 5 versions
            result.append(
                f"  v{version['version']}: {version['modified_at']} ({len(version['content'])} bytes)"
            )

    return "\n".join(result)


@tool
def cp(
    source: str,
    destination: str,
    state: Annotated[DeepAgentState, InjectedState],
    tool_call_id: Annotated[str, InjectedToolCallId],
) -> Command:
    """Copy a file in the virtual filesystem."""
    vfs = state.get("virtual_fs", {"files": {}, "current_directory": "/"})
    files = state.get("files", {})

    # Normalize paths
    if not source.startswith("/"):
        source = os.path.join(vfs.get("current_directory", "/"), source)
    if not destination.startswith("/"):
        destination = os.path.join(vfs.get("current_directory", "/"), destination)

    # Check source exists
    content = None
    if source in vfs.get("files", {}):
        file_data = vfs["files"][source]
        if isinstance(file_data, dict):
            content = file_data.get("content", "")
        else:
            content = file_data
    elif source in files:
        content = files[source]
    else:
        return Command(
            update={
                "messages": [
                    ToolMessage(
                        f"Source file {source} not found", tool_call_id=tool_call_id
                    )
                ],
            }
        )

    # Create copy
    now = datetime.now().isoformat()
    new_file = {
        "content": content,
        "metadata": {
            "created_at": now,
            "modified_at": now,
            "size": len(content),
            "permissions": "rw-r--r--",
            "version": 1,
        },
    }

    if "files" not in vfs:
        vfs["files"] = {}
    vfs["files"][destination] = new_file

    # Also update legacy files for compatibility
    files[destination] = content

    return Command(
        update={
            "virtual_fs": vfs,
            "files": files,
            "messages": [
                ToolMessage(
                    f"Copied {source} to {destination}", tool_call_id=tool_call_id
                )
            ],
        }
    )


@tool
def human_input(
    prompt: str,
    state: Annotated[DeepAgentState, InjectedState],
    tool_call_id: Annotated[str, InjectedToolCallId],
    context: Optional[str] = None,
) -> Command:
    """Request input from a human operator."""
    feedback_entry = {
        "timestamp": datetime.now().isoformat(),
        "prompt": prompt,
        "context": context,
        "response": None,  # This would be filled by the human-in-the-loop callback
        "tool_call_id": tool_call_id,
    }

    human_feedback = state.get("human_feedback", [])
    human_feedback.append(feedback_entry)

    # In a real implementation, this would trigger a callback to get human input
    # For now, we'll return a placeholder response
    response_msg = f"Human input requested: {prompt}"
    if context:
        response_msg += f"\nContext: {context}"

    return Command(
        update={
            "human_feedback": human_feedback,
            "messages": [ToolMessage(response_msg, tool_call_id=tool_call_id)],
        }
    )
