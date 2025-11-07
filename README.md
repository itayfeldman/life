# life

## What is this?

A NumPy-oriented implementation of [Conway's Game of Life](https://conwaylife.com/).


## Setup

To run the code, you need to have Python 3.7+ and create a virtual environment. You can use `venv` or `conda` for this.  Install the required packages using `pip`:

```bash
python -m venv life
source life/bin/activate  # On Windows use `life\Scripts\activate`

pip install -r life/src/life/requirements.txt
pip install -e life
```


## To Run

In linux or macOS, you can run the script from the command line:

```bash
%\> ./life/scripts/run.sh --size 100 --seed noise --interval 350 --cmap binary --figsize 8 --func fast
```

You can also run the module directly using Python:

```bash
source life/bin/activate  # On Windows use `life\Scripts\activate`
%\> python -m life --size 100 --seed noise --interval 350 --cmap binary --figsize 8 --func fast
```


## Usage

The program can take a few command line arguments:

* `--size`: the size of the grid (default: 100, min: 10, max: 1000)
* `--seed`: the seed for the random number generator (default: noise)
* `--interval`: the interval between generations in milliseconds (default: 350)
* `--cmap`: the matplotlib [color map](https://matplotlib.org/stable/users/explain/colors/colormaps.html) to use (default: 'binary')
* `--figsize`: the size of the figure (default: 8)
* `--func`: the function to use (default: fast - see below for options)


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
