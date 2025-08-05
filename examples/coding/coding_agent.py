"""Example of a deep coding agent built on top of deepagents."""

import asyncio
from typing import List, Dict, Any
from deepagents import create_deep_agent, SubAgent
from deepagents.filesystem import mkdir, cd, pwd, ls_enhanced, file_history, cp, human_input
from langchain_core.tools import tool
from dotenv import load_dotenv

# important to keep
load_dotenv()

# Custom coding tools
@tool
def analyze_code(file_path: str) -> Dict[str, Any]:
    """Analyze code quality and provide suggestions."""
    # This is a mock implementation
    return {
        "file": file_path,
        "issues": [
            {"line": 10, "type": "style", "message": "Line too long"},
            {"line": 25, "type": "performance", "message": "Consider using list comprehension"}
        ],
        "complexity": 7.5,
        "maintainability": 8.0
    }


@tool
def refactor_code(file_path: str, refactor_type: str) -> str:
    """Refactor code based on specified type (e.g., 'extract_method', 'rename_variable')."""
    return f"Refactored {file_path} with {refactor_type} refactoring"


@tool
def generate_tests(file_path: str, test_framework: str = "pytest") -> str:
    """Generate unit tests for the given file."""
    return f"""import pytest
from {file_path.replace('.py', '')} import *

class Test{file_path.replace('.py', '').title()}:
    def test_example(self):
        # Generated test
        assert True
"""


@tool
def run_tests(test_path: str = "tests/") -> Dict[str, Any]:
    """Run tests and return results."""
    return {
        "total": 10,
        "passed": 8,
        "failed": 2,
        "coverage": 85.5
    }


# Human-in-the-loop callback
def coding_human_callback(event: str, message: str):
    """Handle human-in-the-loop interactions."""
    print(f"\n🤖 Agent Event: {event}")
    print(f"📝 Message: {message}")
    
    if event == "Task started" and "refactor" in message.lower():
        response = input("Would you like to review the refactoring plan? (y/n): ")
        if response.lower() == 'y':
            print("Proceeding with human review...")
            # In a real implementation, this would trigger a review process
    
    return None


# Define specialized coding subagents
refactoring_agent = SubAgent(
    name="refactoring-expert",
    description="Specializes in code refactoring, optimization, and clean code practices",
    prompt="""You are an expert in code refactoring. Your responsibilities:
    1. Analyze code for refactoring opportunities
    2. Apply design patterns appropriately
    3. Improve code readability and maintainability
    4. Optimize performance where possible
    5. Ensure backward compatibility
    Always explain your refactoring decisions.""",
    tools=["analyze_code", "refactor_code", "write_file", "read_file", "edit_file"]
)

testing_agent = SubAgent(
    name="testing-expert",
    description="Specializes in writing comprehensive tests and improving test coverage",
    prompt="""You are an expert in software testing. Your responsibilities:
    1. Write comprehensive unit tests
    2. Create integration tests where needed
    3. Ensure high test coverage
    4. Use appropriate testing patterns
    5. Write clear test documentation
    Focus on edge cases and error scenarios.""",
    tools=["generate_tests", "run_tests", "write_file", "read_file"]
)

code_review_agent = SubAgent(
    name="code-reviewer",
    description="Performs thorough code reviews and provides constructive feedback",
    prompt="""You are a senior code reviewer. Your responsibilities:
    1. Review code for bugs and security issues
    2. Check adherence to coding standards
    3. Suggest improvements for readability
    4. Identify performance bottlenecks
    5. Ensure proper error handling
    Provide constructive and actionable feedback.""",
    tools=["analyze_code", "read_file", "write_todos"]
)


# Create the main coding agent
def create_coding_agent():
    """Create a deep coding agent with specialized subagents."""
    
    coding_instructions = """You are a senior software engineer with expertise in:
    - Code architecture and design patterns
    - Refactoring and optimization
    - Test-driven development
    - Code review and quality assurance
    
    You work with a team of specialized agents:
    - refactoring-expert: For code refactoring tasks
    - testing-expert: For test creation and coverage
    - code-reviewer: For thorough code reviews
    
    When given a coding task:
    1. First analyze the requirements
    2. Plan your approach using write_todos
    3. Delegate specialized tasks to appropriate subagents
    4. Coordinate the work and ensure quality
    5. Request human input when making critical decisions
    """
    
    agent = create_deep_agent(
        tools=[
            analyze_code, refactor_code, generate_tests, run_tests,
            mkdir, cd, pwd, ls_enhanced, file_history, cp, human_input
        ],
        instructions=coding_instructions,
        subagents=[refactoring_agent, testing_agent, code_review_agent],
        human_in_the_loop=coding_human_callback,
        use_default_prompt=True
    )
    
    # Configure with higher recursion limit
    return agent.with_config({"recursion_limit": 50})


# Example usage
async def example_coding_task():
    """Example of using the coding agent."""
    agent = create_coding_agent()
    
    # Example task: Refactor a Python module
    task = {
        "messages": [{
            "role": "user",
            "content": """Please help me refactor the user_service.py module. 
            The module has grown too large and has multiple responsibilities. 
            I need you to:
            1. Analyze the current structure
            2. Identify refactoring opportunities
            3. Split it into smaller, focused modules
            4. Ensure all functionality is preserved
            5. Write tests for the refactored code
            6. Perform a code review of the changes
            """
        }],
        "files": {
            "user_service.py": """# Large user service module
class UserService:
    def __init__(self, db, cache, email_service):
        self.db = db
        self.cache = cache
        self.email_service = email_service
    
    def create_user(self, user_data):
        # Validation
        if not user_data.get('email'):
            raise ValueError("Email required")
        if not user_data.get('password'):
            raise ValueError("Password required")
        
        # Create user in DB
        user = self.db.create('users', user_data)
        
        # Cache user
        self.cache.set(f"user:{user['id']}", user)
        
        # Send welcome email
        self.email_service.send(
            to=user['email'],
            subject="Welcome!",
            body="Welcome to our service!"
        )
        
        return user
    
    def get_user(self, user_id):
        # Check cache first
        cached = self.cache.get(f"user:{user_id}")
        if cached:
            return cached
        
        # Get from DB
        user = self.db.get('users', user_id)
        if user:
            self.cache.set(f"user:{user_id}", user)
        
        return user
    
    def update_user(self, user_id, updates):
        user = self.db.update('users', user_id, updates)
        self.cache.delete(f"user:{user_id}")
        return user
    
    def delete_user(self, user_id):
        self.db.delete('users', user_id)
        self.cache.delete(f"user:{user_id}")
        
    def authenticate(self, email, password):
        user = self.db.find_one('users', {'email': email})
        if user and self._verify_password(password, user['password']):
            return self._generate_token(user)
        return None
    
    def _verify_password(self, password, hashed):
        # Password verification logic
        return True  # Simplified
    
    def _generate_token(self, user):
        # Token generation logic
        return f"token_for_{user['id']}"
"""
        }
    }
    
    # Run the agent
    result = await agent.ainvoke(task)
    print("\n📊 Task completed!")
    print(f"Files modified: {len(result.get('files', {}))}")
    print(f"Todos: {len(result.get('todos', []))}")
    
    return result


# Benchmarking example
async def benchmark_coding_agent():
    """Benchmark the coding agent performance."""
    import time
    
    agent = create_coding_agent()
    
    tasks = [
        "Analyze code complexity of main.py",
        "Generate unit tests for utils module",
        "Refactor database connection handling"
    ]
    
    results = []
    for task in tasks:
        start_time = time.time()
        
        result = await agent.ainvoke({
            "messages": [{"role": "user", "content": task}]
        })
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        results.append({
            "task": task,
            "execution_time": execution_time,
            "messages_count": len(result.get("messages", [])),
            "files_created": len(result.get("files", {}))
        })
    
    # Print benchmark results
    print("\n📊 Benchmark Results:")
    print("-" * 50)
    for res in results:
        print(f"Task: {res['task']}")
        print(f"  Time: {res['execution_time']:.2f}s")
        print(f"  Messages: {res['messages_count']}")
        print(f"  Files: {res['files_created']}")
        print()
    
    avg_time = sum(r['execution_time'] for r in results) / len(results)
    print(f"Average execution time: {avg_time:.2f}s")


if __name__ == "__main__":
    # Run the example
    asyncio.run(example_coding_task())
