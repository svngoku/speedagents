"""Unit tests for the state module."""

import pytest
from datetime import datetime
from deepagents.state import (
    Todo, FileMetadata, VirtualFile, VirtualFileSystem,
    file_reducer, DeepAgentState
)


@pytest.mark.unit
def test_todo_creation():
    """Test Todo TypedDict creation."""
    todo = Todo(
        content="Test task",
        status="pending"
    )
    assert todo["content"] == "Test task"
    assert todo["status"] == "pending"


@pytest.mark.unit
def test_todo_with_timestamps():
    """Test Todo with optional timestamps."""
    now = datetime.now().isoformat()
    todo = Todo(
        content="Test task",
        status="completed",
        created_at=now,
        completed_at=now
    )
    assert todo["created_at"] == now
    assert todo["completed_at"] == now


@pytest.mark.unit
def test_file_metadata():
    """Test FileMetadata creation."""
    now = datetime.now().isoformat()
    metadata = FileMetadata(
        created_at=now,
        modified_at=now,
        size=100,
        permissions="rw-r--r--",
        version=1
    )
    assert metadata["size"] == 100
    assert metadata["version"] == 1


@pytest.mark.unit
def test_virtual_file():
    """Test VirtualFile creation."""
    now = datetime.now().isoformat()
    vfile = VirtualFile(
        content="Test content",
        metadata={
            "created_at": now,
            "modified_at": now,
            "size": 12,
            "permissions": "rw-r--r--",
            "version": 1
        }
    )
    assert vfile["content"] == "Test content"
    assert vfile["metadata"]["size"] == 12


@pytest.mark.unit
def test_file_reducer_with_none():
    """Test file reducer with None values."""
    result = file_reducer(None, {"test.txt": "content"})
    assert result == {"test.txt": "content"}
    
    result = file_reducer({"test.txt": "content"}, None)
    assert result == {"test.txt": "content"}


@pytest.mark.unit
def test_file_reducer_merge_simple():
    """Test file reducer merging simple files."""
    left = {"file1.txt": "content1"}
    right = {"file2.txt": "content2"}
    result = file_reducer(left, right)
    
    assert "file1.txt" in result
    assert "file2.txt" in result


@pytest.mark.unit
def test_file_reducer_convert_string_to_virtual_file():
    """Test file reducer converting string content to VirtualFile."""
    left = {}
    right = {"test.txt": "simple content"}
    result = file_reducer(left, right)
    
    assert "test.txt" in result
    assert isinstance(result["test.txt"], dict)
    assert result["test.txt"]["content"] == "simple content"
    assert "metadata" in result["test.txt"]
    assert result["test.txt"]["metadata"]["size"] == len("simple content")


@pytest.mark.unit
def test_file_reducer_version_history():
    """Test file reducer maintaining version history."""
    # Create initial file
    now1 = datetime.now().isoformat()
    left = {
        "test.txt": {
            "content": "version 1",
            "metadata": {
                "created_at": now1,
                "modified_at": now1,
                "size": 9,
                "permissions": "rw-r--r--",
                "version": 1
            }
        }
    }
    
    # Update file
    now2 = datetime.now().isoformat()
    right = {
        "test.txt": {
            "content": "version 2",
            "metadata": {
                "created_at": now1,
                "modified_at": now2,
                "size": 9,
                "permissions": "rw-r--r--",
                "version": 1
            }
        }
    }
    
    result = file_reducer(left, right)
    
    assert result["test.txt"]["content"] == "version 2"
    assert result["test.txt"]["metadata"]["version"] == 2
    assert "history" in result["test.txt"]
    assert len(result["test.txt"]["history"]) == 1
    assert result["test.txt"]["history"][0]["content"] == "version 1"
