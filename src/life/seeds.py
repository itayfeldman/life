import random

from life import LifeState
from life.pattern_factory import patterns
from life.tiles import TileMaker, TilePattern


class SeedGenerators:
    @staticmethod
    def symmetric(n: int) -> LifeState:
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
    def noise(size: int) -> LifeState:
        return TileMaker.noise((size, size))

    @staticmethod
    def pattern(size: int, seed: str) -> LifeState:
        state = TileMaker.zeros((size, size))
        pattern = patterns[seed]
        n, m = pattern.shape
        state[0:n, 0:m] = pattern
        return state


def new_seed_generator(size: int, seed: str) -> LifeState:
    if seed == "noise":
        return SeedGenerators.noise(size)
    elif seed == "symmetric":
        return SeedGenerators.symmetric(size)
    return SeedGenerators.pattern(size, seed)
