# Claude Code Configuration

This file contains configuration and context for Claude Code to help with development tasks in this project.

## Project Overview

A NumPy-oriented implementation of Conway's Game of Life. This is a Python project that simulates Conway's Game of Life using various implementation approaches with performance benchmarking.

## Development Commands

### Setup
```bash
python -m venv life
source life/bin/activate  # On Windows use `life\Scripts\activate`
pip install -r life/src/life/requirements.txt
pip install -e life
```

### Run
```bash
# Using shell script (Linux/macOS)
life/scripts/run.sh --size 100 --seed noise --interval 350 --cmap binary --figsize 8 --func fast

# Using Python module
source life/bin/activate
python -m life --size 100 --seed noise --interval 350 --cmap binary --figsize 8 --func fast
```

### Command Line Arguments
- `--size`: grid size (default: 100, min: 10, max: 1000)
- `--seed`: random seed (default: noise)  
- `--interval`: generation interval in ms (default: 350)
- `--cmap`: matplotlib colormap (default: 'binary')
- `--figsize`: figure size (default: 8)
- `--func`: implementation function (default: fast)
- `--show-stats`: show statistics overlay (default: false)
- `--fullscreen`: run in fullscreen mode (default: false)

### Available Functions (by performance)
1. `fast` - 0.0417s (fastest)
2. `vectorized` - 0.0763s
3. `window` - 0.0920s
4. `ultra_fast` - 0.2371s
5. `convolution` - 0.2436s
6. `loop` - 20.6971s (slowest)

## Project Structure

- `life/src/life/` - Main package directory
- `life/scripts/run.sh` - Shell script runner
- `requirements.txt` - Python dependencies

## Notes

- This project uses Git for version control
- Main branch: `main`
- Python 3.7+ required
- Uses NumPy for high-performance array operations
- Multiple implementation approaches for performance comparison