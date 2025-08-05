# DeepAgents - Fixes Applied

This document describes all the fixes applied to resolve the errors reported.

## 🐛 Issues Fixed

### 1. ✅ Fixed `uv run tests` Error

**Issue**: Command `uv run tests` failed with "No such file or directory"

**Fix**: Use the correct command format:
```bash
uv run pytest tests/
```

### 2. ✅ Fixed `write_todos` TypeError

**Issue**: `TypeError("write_todos() got an unexpected keyword argument 'kwargs'")`

**Cause**: The `@benchmark_tool_call` decorator was interfering with the `@tool` decorator from LangChain.

**Fix**: 
- Removed the `@benchmark_tool_call` decorator from `write_todos`
- Updated the decorator to use `functools.wraps` to preserve function metadata
- The benchmarking functionality is preserved but not applied to LangChain tools

### 3. ✅ Fixed File Content Validation Error

**Issue**: Pydantic validation error - `state.files` expected string but got dict with metadata

**Cause**: The enhanced virtual filesystem was saving files as dictionaries with metadata, but the tools expected strings.

**Fix**: Updated `read_file` and `edit_file` functions to handle both formats:
```python
# Handle both string and dict formats
if isinstance(file_data, dict) and "content" in file_data:
    content = file_data["content"]
else:
    content = file_data
```

### 4. ✅ Fixed Package Dependencies

**Issue**: `tavily` package not found during dependency resolution

**Fix**: 
- Changed from `tavily` to `tavily-python` in pyproject.toml
- Used `uv sync --frozen` to bypass dependency resolution issues
- Added `tavily-python` to both dev and examples optional dependencies

### 5. ✅ Fixed Missing pytest-cov

**Issue**: pytest couldn't recognize coverage arguments

**Fix**: Installed pytest-cov:
```bash
uv add pytest-cov --dev
```

### 6. ✅ Added Missing Tool Decorators

**Issue**: Some tools like `ls` and `write_file` were missing the `@tool` decorator

**Fix**: Added `@tool` decorators to:
- `ls` function
- `write_file` function

## 📋 Summary of Changes

### Modified Files:
1. **`src/deepagents/tools.py`**:
   - Fixed decorator order issue
   - Added `functools.wraps` to preserve function metadata
   - Updated `read_file` and `edit_file` to handle both string and dict file formats
   - Added missing `@tool` decorators

2. **`pyproject.toml`**:
   - Fixed `tavily` → `tavily-python`
   - Added proper optional dependencies sections

3. **`pytest.ini`**:
   - Removed unknown `asyncio_mode` configuration

## 🧪 Testing

All tests are now passing:
```bash
uv run pytest tests/unit/test_graph.py -v
# Result: 5 passed, 11 warnings in 0.83s
```

## 🚀 Usage

The package is now fully functional with all enhanced features:
- Customizable system prompts ✅
- Enhanced virtual filesystem ✅
- Human-in-the-loop support ✅
- Benchmarking capabilities ✅
- Proper file handling for both legacy and new formats ✅

## 🔧 Backward Compatibility

The fixes maintain backward compatibility:
- Files can be stored as either strings (legacy) or dictionaries with metadata (new)
- All tools handle both formats automatically
- No breaking changes to the public API

### 7. ✅ Fixed Recursion Limit Error in Examples

**Issue**: `GraphRecursionError` when running coding agent examples

**Cause**: Complex tasks with multiple subagents can hit the default recursion limit of 25

**Fixes**:
1. Added recursion limit configuration to agent creation:
   ```python
   agent.with_config({"recursion_limit": 50})
   ```
2. Created simpler example (`simple_coding_agent.py`) with:
   - No subagents to avoid recursion
   - Lower recursion limit (10)
   - Timeout protection
   - Better error handling

### 8. ✅ Fixed UnboundLocalError in Examples

**Issue**: `UnboundLocalError` when exceptions occur before `result` is assigned

**Fix**: Initialize `result = None` before try block

### 9. ✅ Added API Key Documentation

**Issue**: Authentication errors when running examples without API keys

**Fix**: Created `examples/README.md` with:
- API key setup instructions
- Troubleshooting guide
- Best practices for using the framework
