# DeepAgents Installation Guide

## Prerequisites

- Python 3.11 or higher
- uv (for package management) or pip

## Installation

### Using uv (Recommended)

```bash
# Clone the repository
git clone [your-repo-url]
cd deepagents

# Install with uv
uv sync --frozen

# Install development dependencies
uv sync --frozen --all-extras
```

### Using pip

```bash
# Clone the repository
git clone [your-repo-url]
cd deepagents

# Install in development mode
pip install -e .

# Install with development dependencies
pip install -e ".[dev]"

# Install with example dependencies
pip install -e ".[examples]"

# Install all extras
pip install -e ".[dev,test,examples]"
```

## Additional Dependencies

For the research agent example:
```bash
pip install tavily-python
```

## Verify Installation

```bash
# Test basic import
python -c "import deepagents; print('DeepAgents imported successfully!')"

# Test enhanced features
python -c "from deepagents import create_deep_agent; from deepagents.filesystem import mkdir; print('Enhanced features available!')"
```

## Running Tests

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=src/deepagents

# Run specific test file
pytest tests/unit/test_graph.py -v
```

## Running Examples

### Research Agent Example
```bash
cd examples/research
python research_agent.py
```

### Coding Agent Example
```bash
cd examples/coding
python coding_agent.py
```

## Troubleshooting

### Import Errors
If you encounter import errors, ensure the package is installed in development mode:
```bash
pip install -e .
```

### Dependency Resolution Issues
If uv has issues resolving dependencies, use the `--frozen` flag:
```bash
uv sync --frozen
```

### Missing Dependencies
Some examples require additional dependencies. Install them as needed:
```bash
pip install tavily-python  # For research agent
```
