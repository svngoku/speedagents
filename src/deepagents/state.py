from langgraph.prebuilt.chat_agent_executor import AgentState
from typing import NotRequired, Annotated, Dict, List, Optional
from typing import Literal
from typing_extensions import TypedDict
from datetime import datetime
import os


class Todo(TypedDict):
    """Todo to track."""

    content: str
    status: Literal["pending", "in_progress", "completed"]
    created_at: NotRequired[str]
    completed_at: NotRequired[Optional[str]]


class FileMetadata(TypedDict):
    """Metadata for virtual files."""

    created_at: str
    modified_at: str
    size: int
    permissions: str
    version: int


class VirtualFile(TypedDict):
    """Enhanced virtual file with metadata."""

    content: str
    metadata: FileMetadata
    history: NotRequired[List[Dict[str, str]]]


class VirtualFileSystem(TypedDict):
    """Enhanced virtual filesystem with directory support."""

    files: Dict[str, VirtualFile]
    directories: List[str]
    current_directory: str


def file_reducer(left: Optional[Dict], right: Optional[Dict]) -> Dict:
    """Enhanced file reducer that handles virtual filesystem."""
    if left is None:
        return right or {}
    elif right is None:
        return left
    else:
        # Merge files with proper version control
        merged = left.copy()
        for path, file_data in right.items():
            if isinstance(file_data, str):
                # Convert simple string content to VirtualFile
                now = datetime.now().isoformat()
                merged[path] = {
                    "content": file_data,
                    "metadata": {
                        "created_at": now,
                        "modified_at": now,
                        "size": len(file_data),
                        "permissions": "rw-r--r--",
                        "version": 1,
                    },
                }
            elif isinstance(file_data, dict) and "content" in file_data:
                # Update existing file with version increment
                if path in merged and isinstance(merged[path], dict):
                    old_content = merged[path].get("content", "")
                    if old_content != file_data["content"]:
                        # Add to history
                        history = merged[path].get("history", [])
                        history.append(
                            {
                                "content": old_content,
                                "modified_at": merged[path]["metadata"]["modified_at"],
                                "version": merged[path]["metadata"]["version"],
                            }
                        )
                        file_data["history"] = history[:10]  # Keep last 10 versions
                        file_data["metadata"]["version"] = (
                            merged[path]["metadata"]["version"] + 1
                        )
                merged[path] = file_data
            else:
                merged[path] = file_data
        return merged


class DeepAgentState(AgentState):
    """Enhanced agent state with robust features."""

    todos: NotRequired[List[Todo]]
    files: Annotated[NotRequired[Dict[str, str]], file_reducer]  # Legacy support
    virtual_fs: NotRequired[VirtualFileSystem]
    benchmarks: NotRequired[Dict[str, float]]  # Store benchmark results
    human_feedback: NotRequired[List[Dict[str, str]]]  # Store human feedback
