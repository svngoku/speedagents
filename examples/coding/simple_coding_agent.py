"""Simple example of a deep coding agent that avoids recursion issues."""

import asyncio
from typing import Dict, Any
from deepagents import create_deep_agent
from langchain_core.tools import tool


# Simple coding tools
@tool
def analyze_code_simple(code: str) -> Dict[str, Any]:
    """Analyze code and provide basic metrics."""
    lines = code.strip().split('\n')
    return {
        "lines_of_code": len(lines),
        "functions": len([l for l in lines if 'def ' in l]),
        "classes": len([l for l in lines if 'class ' in l]),
        "comments": len([l for l in lines if '#' in l])
    }


@tool  
def suggest_improvements(code_analysis: Dict[str, Any]) -> str:
    """Suggest improvements based on code analysis."""
    suggestions = []
    
    if code_analysis.get("lines_of_code", 0) > 50:
        suggestions.append("Consider breaking this into smaller modules")
    
    if code_analysis.get("comments", 0) < code_analysis.get("lines_of_code", 0) * 0.1:
        suggestions.append("Add more comments to improve documentation")
    
    if code_analysis.get("functions", 0) == 0:
        suggestions.append("Consider organizing code into functions")
    
    return "\n".join(suggestions) if suggestions else "Code looks good!"


# Create a simple coding agent
def create_simple_coding_agent():
    """Create a simple coding agent without subagents."""
    
    instructions = """You are a helpful coding assistant. 
    
    When given code to analyze:
    1. Use analyze_code_simple to get basic metrics
    2. Use suggest_improvements to provide feedback
    3. Write a summary using write_todos
    
    Keep your analysis brief and focused."""
    
    agent = create_deep_agent(
        tools=[analyze_code_simple, suggest_improvements],
        instructions=instructions,
        use_default_prompt=True
    )
    
    # Configure with lower recursion limit to avoid issues
    return agent.with_config({"recursion_limit": 10})


# Simple example usage
async def example_simple_task():
    """Run a simple coding analysis task."""
    agent = create_simple_coding_agent()
    
    # Simple task
    task = {
        "messages": [{
            "role": "user",
            "content": """Please analyze this Python code and suggest improvements:

def calculate_total(items):
    total = 0
    for item in items:
        total += item['price'] * item['quantity']
    return total

def apply_discount(total, discount_percent):
    return total * (1 - discount_percent / 100)

# Calculate final price
items = [{'price': 10, 'quantity': 2}, {'price': 5, 'quantity': 3}]
total = calculate_total(items)
final_price = apply_discount(total, 10)
print(f"Final price: ${final_price}")
"""
        }]
    }
    
    result = None
    try:
        # Run the agent with timeout
        result = await asyncio.wait_for(
            agent.ainvoke(task),
            timeout=30.0  # 30 second timeout
        )
        
        print("\n✅ Task completed successfully!")
        print(f"Messages: {len(result.get('messages', []))}")
        print(f"Todos created: {len(result.get('todos', []))}")
        
        # Print todos if any
        if result.get('todos'):
            print("\n📝 Todos:")
            for todo in result['todos']:
                print(f"  - [{todo['status']}] {todo['content']}")
                
    except asyncio.TimeoutError:
        print("\n⏱️ Task timed out after 30 seconds")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    return result


# More complex example with file handling
async def example_file_analysis():
    """Example analyzing code from files."""
    agent = create_simple_coding_agent()
    
    # Task with file
    task = {
        "messages": [{
            "role": "user", 
            "content": "Please analyze the code in utils.py and suggest improvements."
        }],
        "files": {
            "utils.py": """# Utility functions

def format_date(date_str):
    # Convert date string to formatted date
    parts = date_str.split('-')
    return f"{parts[2]}/{parts[1]}/{parts[0]}"

def calculate_age(birth_year, current_year):
    return current_year - birth_year

def is_valid_email(email):
    return '@' in email and '.' in email

def get_file_extension(filename):
    parts = filename.split('.')
    if len(parts) > 1:
        return parts[-1]
    return ''
"""
        }
    }
    
    result = None
    try:
        result = await asyncio.wait_for(
            agent.ainvoke(task),
            timeout=30.0
        )
        
        print("\n✅ File analysis completed!")
        
        # Check if any files were modified
        if result.get('files'):
            print(f"\n📁 Files modified: {len(result['files'])}")
            for filename in result['files']:
                print(f"  - {filename}")
                
    except asyncio.TimeoutError:
        print("\n⏱️ Task timed out")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    return result


if __name__ == "__main__":
    print("🚀 Running simple coding agent example...")
    
    # Run the simple example
    asyncio.run(example_simple_task())
    
    print("\n" + "="*50 + "\n")
    print("🚀 Running file analysis example...")
    
    # Run the file analysis example
    asyncio.run(example_file_analysis())
