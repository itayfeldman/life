from life.domain.protocols import PatternRepository
from life.domain.types import Grid
from life.seeds.noise import NoiseGenerator
from life.seeds.pattern_seed import PatternSeedGenerator
from life.seeds.scattered import ScatteredGenerator
from life.seeds.symmetric import SymmetricGenerator

BUILT_IN_SEEDS: frozenset[str] = frozenset({"noise", "symmetric", "scattered"})

_noise = NoiseGenerator()
_symmetric = SymmetricGenerator()


def new_seed_generator(size: int, seed: str, repository: PatternRepository) -> Grid:
    if seed == "noise":
        return _noise(size)
    if seed == "symmetric":
        return _symmetric(size)
    if seed == "scattered":
        return ScatteredGenerator(repository)(size)
    return PatternSeedGenerator(repository)(size, seed)


__all__ = ["new_seed_generator", "BUILT_IN_SEEDS"]
