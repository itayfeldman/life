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
| `--seed NAME` | `noise` | Initial state. `noise`, `symmetric`, or any named pattern (e.g. `glider`, `blinker`). |
| `--engine NAME` | `fast` | Computation engine. See [Performance](#performance) below. |
| `--frontend NAME` | `pygame` | `pygame` or `matplotlib`. |
| `--interval MS` | `100` | Milliseconds between generations. |
| `--window N` | `800` | Pygame window size in pixels (pygame only). |
| `--cmap NAME` | `binary` | Matplotlib [colormap](https://matplotlib.org/stable/users/explain/colors/colormaps.html) (matplotlib only). |
| `--figsize N` | `8` | Matplotlib figure size in inches (matplotlib only). |

`--func` is accepted as an alias for `--engine` for backwards compatibility.

### Examples

```bash
# Default: pygame window, 100×100 noise grid, fast engine
python -m life

# Pygame with a glider pattern
python -m life --seed glider --size 50 --window 600

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
| fast | 0.0577 | 0.0018 | 0.0562 | 0.0605 |
| vectorized | 0.1192 | 0.0127 | 0.1058 | 0.1363 |
| window | 0.1606 | 0.0081 | 0.1518 | 0.1715 |
| convolution | 0.3822 | 0.0165 | 0.3709 | 0.4097 |
| ultra_fast | 0.3896 | 0.0654 | 0.3434 | 0.4887 |
| loop | 24.7336 | 0.4865 | 24.2138 | 25.4527 |

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
