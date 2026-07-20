from typing import Callable

from life.domain import BUILT_IN_SEEDS, Grid, PatternRepository
from life.seeds.noise import NoiseGenerator
from life.seeds.pattern_seed import PatternSeedGenerator
from life.seeds.scattered import ScatteredGenerator
from life.seeds.symmetric import SymmetricGenerator

_SeedGenerator = Callable[[int, PatternRepository], Grid]

_noise = NoiseGenerator()
_symmetric = SymmetricGenerator()


def _generate_noise(size: int, repository: PatternRepository) -> Grid:
    return _noise(size)


def _generate_symmetric(size: int, repository: PatternRepository) -> Grid:
    return _symmetric(size)


def _generate_scattered(size: int, repository: PatternRepository) -> Grid:
    return ScatteredGenerator(repository)(size)


# Keys must match life.domain.types.BUILT_IN_SEEDS — enforced by
# tests/test_import_conventions.py.
SEED_REGISTRY: dict[str, _SeedGenerator] = {
    "noise": _generate_noise,
    "symmetric": _generate_symmetric,
    "scattered": _generate_scattered,
}


def new_seed_generator(size: int, seed: str, repository: PatternRepository) -> Grid:
    if seed in SEED_REGISTRY:
        return SEED_REGISTRY[seed](size, repository)
    return PatternSeedGenerator(repository)(size, seed)


__all__ = ["new_seed_generator", "BUILT_IN_SEEDS", "SEED_REGISTRY"]
