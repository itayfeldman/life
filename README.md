# life

## What is this?

A NumPy-oriented implementation of [Conway's Game of Life](https://en.wikipedia.org/wiki/Conway's_Game_of_Life).

[Community for Conway's Game of Life](https://conwaylife.com/)


## To Run

%\> python life/src/life

The program can take a few command line arguments:

* `--size`: the size of the grid (default: 100, min: 10, max: 1000)
* `--seed`: the seed for the random number generator (default: noise)
* `--interval`: the interval between generations in milliseconds (default: 750)
* `--cmap`: the color map to use (default: 'binary')
* `--figsize`: the size of the figure (default: 5)
* `--func`: the function to use (default: convolution_fx)


## Performance

Benchmark to run 100x100 grid for 1000 generations

| Function    | Mean    | StdDev  | Min     | Max     |
|-------------|---------|---------|---------|---------|
| convolution |  0.2489 | 0.0115  |  0.2416 |  0.2693 |
| window      |  0.0922 | 0.0076  |  0.0857 |  0.1051 |
| loop        | 20.3257 | 0.4198  | 19.8493 | 20.9317 |


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
