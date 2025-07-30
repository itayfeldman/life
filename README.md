# Conway's Game of Life 🧬

A high-performance, feature-rich implementation of [Conway's Game of Life](https://conwaylife.com/) with multiple algorithms, extensive pattern library, and enhanced visualization capabilities.

## ✨ Features

- **6 Optimized Algorithms**: From simple loops to ultra-fast NumPy implementations
- **Rich Pattern Library**: Classic patterns including gliders, oscillators, spaceships, and more
- **Enhanced Visualization**: Statistics tracking, population graphs, and interactive controls
- **Comprehensive Testing**: Full test coverage for reliability
- **Type Safety**: Complete type hints for better development experience
- **Flexible Seeding**: Noise, symmetric, and pattern-based initialization

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/itayfeldman/life.git
cd life

# Create virtual environment
python -m venv life_env
source life_env/bin/activate  # On Windows: life_env\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -e .
```

### Basic Usage

```bash
# Run with default settings
python -m life

# Use enhanced visualizer with statistics
python -m life --enhanced --show-grid

# Try different patterns
python -m life --seed glider --enhanced
python -m life --seed acorn --size 150 --enhanced

# Compare algorithms
python -m life --func ultra_fast --size 200
```

## 📊 Algorithm Performance

Benchmark results for 100×100 grid, 1000 generations:

| Algorithm     | Mean (s) | StdDev   | Min (s)  | Max (s)  | Description |
|---------------|----------|----------|----------|----------|-------------|
| **fast**      | 0.0417   | 0.0027   | 0.0403   | 0.0465   | ⚡ Fastest - NumPy slicing |
| vectorized    | 0.0763   | 0.0036   | 0.0745   | 0.0828   | 🔄 np.roll operations |
| window        | 0.0920   | 0.0027   | 0.0894   | 0.0964   | 🪟 Rolling window approach |
| ultra_fast    | 0.2371   | 0.0150   | 0.2296   | 0.2640   | 🎯 Advanced indexing |
| convolution   | 0.2436   | 0.0062   | 0.2355   | 0.2509   | 🧮 SciPy convolution |
| loop          | 20.6971  | 0.2437   | 20.3488  | 20.9214  | 🐌 Pure Python loops |

## 🎮 Usage Examples

### Command Line Options

```bash
# Basic options
python -m life --size 100 --seed noise --interval 350 --cmap binary --figsize 8 --func fast

# Enhanced visualizer options
python -m life --enhanced --show-grid --title "My Life Simulation"
python -m life --enhanced --no-stats  # Hide statistics panel

# Pattern examples
python -m life --seed glider --enhanced
python -m life --seed lightweight_spaceship --size 50 --enhanced
python -m life --seed acorn --size 200 --interval 100 --enhanced
```

### Available Patterns

#### 🚀 Spaceships
- `glider` - The classic moving pattern
- `lightweight_spaceship` - Fast orthogonal spaceship
- `middleweight_spaceship` - Medium-sized spaceship  
- `heavyweight_spaceship` - Large spaceship

#### 🔄 Oscillators
- `blinker` - Simple period-2 oscillator
- `toad` - Period-2 oscillator
- `beacon` - Period-2 oscillator
- `clock` - Period-2 oscillator
- `pulsar` - Period-3 oscillator

#### 🏠 Still Lifes
- `block` - 2×2 stable pattern
- `beehive` - 6-cell stable pattern
- `loaf` - 7-cell stable pattern
- `boat` - 5-cell stable pattern

#### 🌱 Methuselahs
- `acorn` - Evolves for 5,206 generations
- `diehard` - Dies after 130 generations
- `rpentomino` - Stabilizes after 1,103 generations

### Programmatic Usage

```python
from life.life import Life
from life.engine import fast
from life.visualizer import EnhancedVisualizer

# Create a Life instance
life = Life(size=100, seed="glider", func=fast)

# Use enhanced visualizer
visualizer = EnhancedVisualizer(
    life=life,
    show_stats=True,
    show_grid=True,
    title="Glider Demo"
)
animation = visualizer.animate()

# Get statistics
stats = visualizer.get_statistics()
print(f"Generation: {stats['generation']}")
print(f"Population: {stats['current_population']}")
```

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Run all tests
pytest

# Run specific test files
pytest tests/test_engine.py
pytest tests/test_patterns.py
pytest tests/test_seeds.py

# Run with coverage
pytest --cov=life tests/
```

## 🎨 Enhanced Visualizer Features

The enhanced visualizer (`--enhanced` flag) includes:

- **📈 Real-time Statistics**: Generation counter and population tracking
- **📊 Population Graph**: Historical population visualization
- **⌨️ Interactive Controls**:
  - `SPACE`: Pause/Resume animation
  - `S`: Save current frame as PNG
  - `Q`: Quit application
- **🎯 Grid Lines**: Optional grid overlay (`--show-grid`)
- **💾 Export Capabilities**: Save frames and animations

## 🔧 Development

### Project Structure

```
life/
├── src/life/
│   ├── engine.py          # Core algorithms
│   ├── life.py           # Main Life class
│   ├── visualizer.py     # Enhanced visualization
│   ├── animator.py       # Original animator
│   ├── seeds.py          # Seed generation
│   ├── pattern_factory.py # Pattern loading
│   └── patterns/         # Pattern library
│       ├── Spaceships/
│       ├── Oscillators/
│       ├── StillLifes/
│       ├── Metuselah/
│       └── ...
├── tests/                # Comprehensive test suite
└── scripts/              # Utility scripts
```

### Adding New Patterns

Create a `.cells` file in the appropriate pattern directory:

```
!Name: My Pattern
!Author: Your Name
!Description: Pattern description
.O.
O.O
.O.
```

## 📚 Algorithm Details

### Fast Algorithm (Recommended)
Uses NumPy array slicing with padding for optimal performance:
- Memory efficient with minimal allocations
- Cache-friendly access patterns
- Handles boundary wrapping correctly

### Vectorized Algorithm
Employs `np.roll` operations for neighbor counting:
- Good balance of speed and readability
- Excellent for educational purposes
- Handles wrapping naturally

### Other Algorithms
- **Convolution**: Uses SciPy's `convolve2d`
- **Window**: Rolling window approach
- **Ultra Fast**: Advanced NumPy indexing
- **Loop**: Pure Python for reference


## Performance

Benchmark to run 100x100 grid for 1000 generations (in seconds)


func          |     Mean |    StdDev|       Min|       Max|
--------------|----------|----------|----------|----------|
convolution   |    0.2436|    0.0062|    0.2355|    0.2509|
window        |    0.0920|    0.0027|    0.0894|    0.0964|
loop          |   20.6971|    0.2437|   20.3488|   20.9214|
fast          |    0.0417|    0.0027|    0.0403|    0.0465|
ultra_fast    |    0.2371|    0.0150|    0.2296|    0.2640|
vectorized    |    0.0763|    0.0036|    0.0745|    0.0828|


## To Dos

* Improve the seed_generation using the Patterns
* Add Patterns ...


## References

### Game of Life
* https://ddejohn.github.io/2021/08/20/life.html
* https://jakevdp.github.io/blog/2013/08/07/conways-game-of-life/
* https://drsfenner.org/blog/2015/07/game-of-life-in-numpy-preliminaries-2/
* https://drsfenner.org/blog/2015/08/game-of-life-in-numpy-2/
### NumPy
* http://scipy-lectures.github.io/advanced/advanced_numpy/#indexing-scheme-strides
* http://chintaksheth.wordpress.com/2013/07/31/numpy-the-tricks-of-the-trade-part-ii/
* https://scipy-cookbook.readthedocs.io/items/GameOfLifeStrides.html
* http://www.rigtorp.se/2011/01/01/rolling-statistics-numpy.html
