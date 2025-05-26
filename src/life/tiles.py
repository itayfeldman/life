import random
from typing import Iterator, Tuple
from numpy.typing import NDArray

import numpy as np

Tile = NDArray[np.int8]
LifeSeed = NDArray[np.int8]
ArrayShape = Tuple[int, int]
LifeSeedGenerator = Iterator[LifeSeed]


class TileMaker:
    """Static methods for generating random binary tiles"""

    @staticmethod
    def __call__(tile_size: int) -> Tile:
        rotator = random.choice((np.fliplr, np.flipud, np.rot90, None))
        tile_maker = random.choice(
            (TileMaker.diagonal, TileMaker.inverted_diagonal, TileMaker.quilt)
        )
        array = tile_maker((tile_size, tile_size))
        return rotator(array) if rotator else array

    @staticmethod
    def noise(shape: ArrayShape) -> Tile:
        """Binary noise tile, the base working unit for the other methods"""
        return np.random.randint(2, size=shape, dtype=np.int8)

    @staticmethod
    def zeros(shape: ArrayShape) -> Tile:
        """A zeros array"""
        return np.zeros(shape=shape, dtype=np.int8)

    @staticmethod
    def quilt(shape: ArrayShape) -> Tile:
        """A base triangular array"""
        return np.triu(TileMaker.noise(shape=shape))

    @staticmethod
    def diagonal(shape: ArrayShape) -> Tile:
        """A diagonal symmetric array"""
        tri = TileMaker.quilt(shape=shape)
        return np.clip(tri * tri.T, 0, 1)

    @staticmethod
    def inverted_diagonal(shape: ArrayShape) -> Tile:
        """Diagonally symmetric array with flipped bits in lower triangular"""
        tri = TileMaker.quilt(shape=shape)
        return np.triu(np.where(tri, 0, 1)).T * tri


class TilePattern:
    """Static methods for tiling an array with different symmetries"""

    @staticmethod
    def __call__(array: Tile, pattern_number: int) -> LifeSeed:
        tiling_method = random.choice(
            (
                TilePattern.four_corners,
                TilePattern.book_match,
                TilePattern.hamburger,
                TilePattern.repeat,
            )
        )
        return np.tile(tiling_method(array), (pattern_number,) * 2)

    @staticmethod
    def four_corners(NW: Tile) -> LifeSeed:
        """
        Radial symmetry, e.g.:
        ```
        A B B A
        C D D C
        C D D C
        A B B A
        ```
        """
        NE = np.fliplr(NW)
        SW = np.flipud(NW)
        SE = np.flipud(NE)
        return np.block([[NW, NE], [SW, SE]])

    @staticmethod
    def book_match(L: Tile) -> LifeSeed:
        """
        Vertical symmetry, e.g.:
        ```
        A B B A
        A B B A
        A B B A
        A B B A
        ```
        """
        R = np.fliplr(L)
        return np.block([[L, R], [L, R]])

    @staticmethod
    def hamburger(T: Tile) -> LifeSeed:
        """
        Horizontal symmetry, e.g.:
        ```
        A A A A
        B B B B
        B B B B
        A A A A
        ```
        """
        B = np.flipud(T)
        return np.block([[T, T], [B, B]])

    @staticmethod
    def repeat(x: Tile) -> LifeSeed:
        """
        Repeating tiles, e.g.:
        ```
        A A
        A A
        ```
        """
        return np.tile(x, (2, 2))
