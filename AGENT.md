# Project: Conway's Game of Life

## Commands
- Run: `python -m life` or use script: `./scripts/run.sh`
- Debug: `./scripts/debug.sh` (then attach debugger to port 5678)
- Test: `python -m unittest discover tests`
- Run specific test: `python -m unittest tests.test_specific_module`
- Performance test: `python tests/test_timeit.py`

## Code Style
- Imports: standard library first, then third-party, then local modules (with blank line separations)
- Formatting: Black-compatible, line length 88 characters
- Type hints: Use for function parameters and return values
- Naming: 
  - snake_case for functions, methods, variables
  - CamelCase for classes
  - UPPER_CASE for constants
- Error handling: Use custom exceptions from `life.exceptions` where appropriate
- Docstrings: Google style with type annotations
- Organization: Keep related functionality in dedicated modules
- Testing: Unit tests for core functionality, performance benchmarks with timeit