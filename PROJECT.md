# PROJECT.md - Conway's Game of Life

Project-specific technical guidance for the Life codebase.

## Quick Start Commands

```bash
# Install the package in development mode
pip install -e .

# Run the Game of Life with default settings
python -m life

# Run with custom parameters
python -m life --size 100 --seed noise --interval 350 --cmap binary --figsize 8 --func fast

# Run benchmarks (compares different engine implementations)
python tests/test_timeit.py

# Run via the shell script (assumes ~/.virtualenvs/life/bin/activate exists)
./scripts/run.sh --size 100 --seed noise
```

## Project Overview

A NumPy-oriented implementation of [Conway's Game of Life](https://conwaylife.com/). The main innovation is multiple pluggable computation strategies for game state updates, ranging from simple Python loops to highly optimized NumPy operations.

## Architecture

### Core Components

1. **`Life` class** (`src/life/life.py`):
   - Main iterator that drives the simulation
   - Takes `size`, `seed`, and `func` (computation strategy)
   - `__next__()` applies the state updater function and returns the new state
   - Manages grid state as NDArray[int8]

2. **Engine functions** (`src/life/engine.py`):
   - Multiple pluggable implementations for computing the next generation
   - Available strategies (exposed via `--func` parameter):
     - `convolution`: Uses scipy.signal.convolve2d
     - `window`: Uses np.roll with itertools.product
     - `loop`: Pure Python nested loops (pedagogical, slow)
     - `fast`: Optimized slicing with np.pad (recommended)
     - `ultra_fast`: Advanced NumPy indexing with np.ix_
     - `vectorized`: Uses np.roll with axis parameter
   - Performance: loop >> convolution ≈ ultra_fast > window > vectorized > fast

3. **`Animator` class** (`src/life/animator.py`):
   - Creates matplotlib FuncAnimation for real-time visualization
   - Consumes the Life iterator to animate state changes
   - Configurable: color map, frame interval (ms), figure size

4. **Seed generators** (`src/life/seeds.py`):
   - `new_seed_generator()` creates initial board state
   - Supports: "noise" (random), "symmetric", and pattern names
   - Validated via `exceptions.validate_args()`

5. **Type system** (`src/life/__init__.py`):
   - `State`: NDArray[int8] - 2D numpy array of cell states
   - `StateUpdater`: Callable[[State], State]
   - `StateIterator`: Iterator[State]

### Execution Flow

```
__main__.py (argparse)
    ↓
Life(size, seed, func) - iterator created
    ↓
Animator(life, cmap, interval, figsize) - visualization setup
    ↓
FuncAnimation - consumes Life iterator frame by frame
    ↓
matplotlib.pyplot.show() - displays animation
```

## Key Design Decisions

- **Pluggable state updaters**: The `func` parameter allows swapping computation strategies at runtime without changing the simulation logic
- **Iterator pattern**: Life implements `__iter__` and `__next__`, making it compatible with matplotlib's FuncAnimation
- **NumPy-first**: All state is managed as numpy arrays; boundary conditions use wrap mode for toroidal grid
- **Validation at entry**: Game of Life rules are enforced in engine functions; input validation in seeds.py

## Testing & Benchmarking

**`tests/test_timeit.py`**:
- Benchmarks each engine function (configurable grid size and iterations)
- Computes statistics across multiple runs (mean, stddev, min, max)
- Used for regression testing when optimizing engine implementations
- Run: `python tests/test_timeit.py` (no pytest required)

## Dependencies

- **numpy**: Grid state and array operations
- **scipy**: `convolve2d` for convolution-based engine
- **matplotlib**: Visualization and FuncAnimation
- **python-dotenv**: Environment configuration (`.env` file)

## Code Style

- Type hints throughout using `# type: ignore` for matplotlib compatibility
- Docstrings follow NumPy documentation style (Parameters/Returns/Examples)
- Engine functions include usage examples in docstrings
- Logging configured via `logging.conf`, debug level via `.env` file

## Important Notes for Development

- **Boundary conditions**: All engine functions use wrap-around (toroidal) for edge cases - this is critical for proper Game of Life behavior
- **Performance matters here**: This project benchmarks computation strategies, so changes to engine functions should be measured
- **Command-line interface**: The `--func` parameter is the main user-facing way to select computation strategies
