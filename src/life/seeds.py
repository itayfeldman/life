import random
from typing import Iterator, Tuple, Union

import numpy as np
from oscillators_factory import oscillators
from tiles import TileMaker, TilePattern

ArrayShape = Tuple[int, int]
LifeSeed = Tile = np.ndarray


class SeedGenerators:
    @staticmethod
    def symmetric(n: int) -> np.ndarray:
        """
        Taking `n` as the desired dimensions of the final seed, this generator
        first breaks down `n` by half into `k`, and then `k` into a tuple
        randomly chosen from the matched divisors of `k` such that the
        product of the tuple is `k`.

        This tuple gives a pattern number and initial size which are passed
        to the seed tile creator and tiling method static classes.

        The larger of the two divisors of `k` that were chosen is assigned
        to `tile_size` while the smaller is assigned to `num_tiles`.

        The `tile_size` is used as the shape for the base binary tile unit,
        and after a tiling method is chosen, the pattern number determines
        how many times the binary tile unit should be repeated.

        After the dust settles, the final seed is of the correct shape.
        """
        k = n // 2
        tile_maker, tile_pattern = TileMaker(), TilePattern()
        d = [(x, k // x) for x in range(2, k + 1) if k % x == 0]
        num_tiles, tile_size = sorted(random.choice(d))
        return tile_pattern(tile_maker(tile_size), num_tiles)

    @staticmethod
    def noise(size: int) -> np.ndarray:
        return TileMaker.noise((size, size))

    @staticmethod
    def oscillator(size: int, seed: str) -> np.ndarray:
        state = TileMaker.zeros((size, size))
        oscillator = oscillators[seed]()  # () to make sure you get the instance
        n, m = oscillator.shape
        state[0:n, 0:m] = oscillator.generate()
        return state


def new_seed_generator(size: int, seed: str) -> np.ndarray:
    if seed == "noise":
        return SeedGenerators.noise(size)
    elif seed == "symmetric":
        return SeedGenerators.symmetric(size)
    return SeedGenerators.oscillator(size, seed)
