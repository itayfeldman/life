import random
from typing import cast

import numpy as np

from life.domain.types import Grid

ArrayShape = tuple[int, int]


class _TileMaker:
    """Random binary tile generator."""

    def __call__(self, tile_size: int) -> Grid:
        rotator = random.choice((np.fliplr, np.flipud, np.rot90, None))
        maker = random.choice(
            (self.diagonal, self.inverted_diagonal, self.quilt)
        )
        array = maker((tile_size, tile_size))
        return rotator(array) if rotator else array

    @staticmethod
    def noise(shape: ArrayShape) -> Grid:
        return np.random.randint(2, size=shape, dtype=np.int8)

    @staticmethod
    def quilt(shape: ArrayShape) -> Grid:
        return np.triu(_TileMaker.noise(shape=shape))

    @staticmethod
    def diagonal(shape: ArrayShape) -> Grid:
        tri = _TileMaker.quilt(shape=shape)
        return cast(Grid, np.clip(tri * tri.T, 0, 1))

    @staticmethod
    def inverted_diagonal(shape: ArrayShape) -> Grid:
        tri = _TileMaker.quilt(shape=shape)
        return cast(Grid, np.triu(np.where(tri, 0, 1)).T * tri)


class _TilePattern:
    """Tile an array with various symmetry patterns."""

    def __call__(self, array: Grid, pattern_number: int) -> Grid:
        tiling = random.choice(
            (self.four_corners, self.book_match, self.hamburger, self.repeat)
        )
        return np.tile(tiling(array), (pattern_number,) * 2)

    @staticmethod
    def four_corners(nw: Grid) -> Grid:
        ne = np.fliplr(nw)
        sw = np.flipud(nw)
        se = np.flipud(ne)
        return np.block([[nw, ne], [sw, se]])

    @staticmethod
    def book_match(left: Grid) -> Grid:
        right = np.fliplr(left)
        return np.block([[left, right], [left, right]])

    @staticmethod
    def hamburger(top: Grid) -> Grid:
        bottom = np.flipud(top)
        return np.block([[top, top], [bottom, bottom]])

    @staticmethod
    def repeat(x: Grid) -> Grid:
        return np.tile(x, (2, 2))


class SymmetricGenerator:
    def __call__(self, size: int) -> Grid:
        k = size // 2
        tile_maker = _TileMaker()
        tile_pattern = _TilePattern()
        divisors = [(x, k // x) for x in range(2, k + 1) if k % x == 0]
        num_tiles, tile_size = sorted(random.choice(divisors))
        tiled = tile_pattern(tile_maker(tile_size), num_tiles)
        result = np.zeros((size, size), dtype=np.int8)
        h, w = tiled.shape
        result[:h, :w] = np.clip(tiled, 0, 1).astype(np.int8)
        # For odd sizes the tiled block is (size-1)×(size-1); copy row/col 0 into
        # the last row/col so the grid wraps symmetrically on a toroidal surface.
        if size % 2 == 1:
            result[-1, :] = result[0, :]
            result[:, -1] = result[:, 0]
        return result
