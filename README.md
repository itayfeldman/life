# life

## What is this?

A NumPy-oriented implementation of [Conway's Game of Life](https://en.wikipedia.org/wiki/Conway's_Game_of_Life).

[Community for Conway's Game of Life](https://conwaylife.com/)


## To Run

%\> python life/src/life

The program can take a few command line arguments:

* `--size`: the size of the grid (default: 100, min: 10, max: 1000)
* `--seed`: the seed for the random number generator (default: noise)
* `--interval`: the interval between generations in milliseconds (default: 500)
* `--cmap`: the color map to use (default: 'binary')
* `--figsize`: the size of the figure (default: 5)
* `--func`: the function to use (default: fast_neighbors)


## Performance

Benchmark to run 100x100 grid for 1000 generations (in seconds)


Function      |     Mean |    StdDev|       Min|       Max|
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
