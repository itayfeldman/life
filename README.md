# life

A NumPy-oriented implementation of [Conway's Game of Life](https://conwaylife.com/) with six interchangeable computation engines and two visualization frontends.


## Setup

```bash
uv sync
```

Or with pip:

```bash
pip install -e .
```

Requires Python 3.10+.


## Run

```bash
python -m life [options]
```

### Options

| Flag | Default | Description |
|---|---|---|
| `--size N` | `100` | Grid dimension (N×N). Min 10, max 1000. |
| `--seed NAME` | `noise` | Initial state. `noise`, `symmetric`, `scattered`, or any named pattern (e.g. `glider`, `blinker`). |
| `--engine NAME` | `pad_slice` | Computation engine. See [Performance](#performance) below. |
| `--frontend NAME` | `pygame` | `pygame` or `matplotlib`. |
| `--interval MS` | `100` | Milliseconds between generations. |
| `--display-size N` | `10` | Display size in inches. Matplotlib uses this as `figsize`; pygame multiplies by 100 to get window pixels (so `10` → 1000 px). |
| `--cmap NAME` | `binary` | Matplotlib [colormap](https://matplotlib.org/stable/users/explain/colors/colormaps.html) (matplotlib only). |
| `--bench N` | `None` | Run N generations headlessly and print a timing summary instead of launching a frontend. |

### Examples

```bash
# Default: pygame window, 100×100 noise grid, pad_slice engine
python -m life

# Pygame with a glider pattern, 600 px window
python -m life --seed glider --size 50 --display-size 6

# Matplotlib frontend
python -m life --frontend matplotlib --size 100 --cmap inferno

# Slow it down, use the loop engine
python -m life --interval 500 --engine loop --size 30
```


## Pygame controls

| Key | Action |
|---|---|
| `Space` | Pause / resume |
| `→` | Step one generation (while paused) |
| `+` / `-` | Speed up / slow down (±25 ms per press) |
| `Q` / `Esc` | Quit |


## Performance

Benchmark: 100×100 grid, 1000 generations.

| Engine | Mean (s) | StdDev | Min | Max |
|---|---|---|---|---|
| pad_slice | 0.1279 | 0.0206 | 0.1085 | 0.1590 |
| roll | 0.3997 | 0.0647 | 0.3523 | 0.4995 |
| ix_index | 0.5883 | 0.0044 | 0.5833 | 0.5934 |
| bitpack | 0.5155 | 0.0282 | 0.4823 | 0.5479 |
| convolution | 0.6158 | 0.0106 | 0.6020 | 0.6277 |
| loop | 37.9015 | 0.9250 | 37.1816 | 39.3115 |

Run benchmarks yourself:

```bash
python tests/test_timeit.py          # prints table
pytest tests/test_timeit.py -v       # pytest mode
```


## References

- [Conway's Game of Life — ddejohn](https://ddejohn.github.io/2021/08/20/life.html)
- [Game of Life in NumPy — Jake VanderPlas](https://jakevdp.github.io/blog/2013/08/07/conways-game-of-life/)
- [Game of Life in NumPy — drsfenner (part 1)](https://drsfenner.org/blog/2015/07/game-life-numpy-preliminaries-2/)
- [Game of Life in NumPy — drsfenner (part 2)](https://drsfenner.org/blog/2015/08/game-life-numpy-2/)
- [NumPy strides](http://scipy-lectures.github.io/advanced/advanced_numpy/#indexing-scheme-strides)
- [NumPy tricks](http://chintaksheth.wordpress.com/2013/07/31/numpy-the-tricks-of-the-trade-part-ii/)
- [Game of Life with strides — SciPy cookbook](https://scipy-cookbook.readthedocs.io/items/GameOfLifeStrides.html)
