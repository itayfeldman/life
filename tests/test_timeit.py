"""
Benchmarking suite for Game of Life engine implementations.

This module provides pytest-compatible benchmarks for all engine functions
(convolution, loop, pad_slice, ix_index, roll). Each test measures
execution time over multiple runs and collects statistics (mean, stdev, min, max).

Can be run as:
- pytest tests/test_timeit.py -v          (pytest mode with individual test results)
- python tests/test_timeit.py              (standalone mode with formatted table)
"""
import statistics
import timeit
from typing import Any, Callable

try:
    import pytest
except ImportError:
    pytest = None  # type: ignore

from life.engines import bitpack, convolution, ix_index, loop, pad_slice, roll
from life.infrastructure import RlePatternRepository
from life.simulation import LifeSimulation as Life

_repository = RlePatternRepository()


ALL_ENGINES = {
    "bitpack": bitpack,
    "convolution": convolution,
    "loop": loop,
    "pad_slice": pad_slice,
    "ix_index": ix_index,
    "roll": roll,
}


if pytest:

    @pytest.fixture
    def benchmark_params() -> dict[str, int]:
        """Benchmark configuration parameters."""
        return {
            "size": 100,
            "iterations": 1000,
            "runs": 5,
        }

    @pytest.fixture(params=sorted(ALL_ENGINES.keys()), ids=lambda x: x)
    def engine_func(request) -> tuple[str, Callable[[Any], Any]]:
        """Parametrized fixture providing all engine functions with their names."""
        func_name = request.param
        return func_name, ALL_ENGINES[func_name]


def run_benchmark(
    func: Callable[[Any], Any],
    size: int = 100,
    iterations: int = 1000,
    runs: int = 5,
) -> dict[str, float]:
    """
    Run multiple benchmark runs and return statistics.

    Parameters
    ----------
    func : Callable
        The engine function to benchmark.
    size : int, optional
        Grid size for Life instance (default: 100).
    iterations : int, optional
        Number of iterations per run (default: 1000).
    runs : int, optional
        Number of independent runs to average (default: 5).

    Returns
    -------
    dict[str, float]
        Statistics: mean, stdev, min, max execution times in seconds.
    """
    times: list[float] = []

    for _ in range(runs):
        life = Life(size=size, seed="noise", engine=func, repository=_repository)
        time_taken = timeit.timeit(
            stmt="next(life)",
            globals={"life": life},
            number=iterations,
        )
        times.append(time_taken)

    return {
        "mean": statistics.mean(times),
        "stdev": statistics.stdev(times) if len(times) > 1 else 0,
        "min": min(times),
        "max": max(times),
    }


if pytest:

    def test_engine_performance(
        engine_func: tuple[str, Callable[[Any], Any]],
        benchmark_params: dict[str, int],
    ) -> None:
        """
        Benchmark an engine function and verify execution completes.

        This test runs the benchmark and asserts that all statistical measures
        are non-negative (valid timings). Used to verify all engines execute.

        Parameters
        ----------
        engine_func : tuple[str, Callable]
            Engine name and function from fixture.
        benchmark_params : dict[str, int]
            Benchmark parameters from fixture.
        """
        func_name, func = engine_func
        stats = run_benchmark(
            func,
            size=benchmark_params["size"],
            iterations=benchmark_params["iterations"],
            runs=benchmark_params["runs"],
        )

        # Verify all statistics are valid (non-negative)
        assert stats["mean"] >= 0, f"{func_name}: mean time should be non-negative"
        assert stats["stdev"] >= 0, f"{func_name}: stdev should be non-negative"
        assert stats["min"] >= 0, f"{func_name}: min time should be non-negative"
        assert stats["max"] >= 0, f"{func_name}: max time should be non-negative"
        assert (
            stats["min"] <= stats["mean"] <= stats["max"]
        ), f"{func_name}: mean should be between min and max"


def print_benchmark_results(
    results: dict[str, dict[str, float]],
) -> None:
    """
    Pretty-print benchmark results as a formatted table.

    Parameters
    ----------
    results : dict[str, dict[str, float]]
        Mapping of engine names to their benchmark statistics.
    """
    header = f"{'Function':<12} {'Mean':<10} {'StdDev':<10} {'Min':<10} {'Max':<10}"
    print(header)
    print("-" * 60)

    for func_name in sorted(results.keys()):
        stats = results[func_name]
        print(
            f"{func_name:<12} {stats['mean']:<10.4f} {stats['stdev']:<10.4f} "
            f"{stats['min']:<10.4f} {stats['max']:<10.4f}"
        )


def run_standalone_benchmarks() -> None:
    """
    Run benchmarks in standalone mode (when script is executed directly).

    Runs all engine benchmarks with fixed parameters and prints a formatted
    table of results. This provides an alternative to pytest for quick
    performance checking.
    """
    print("Running benchmark suite (standalone mode)...\n")

    benchmark_params = {
        "size": 100,
        "iterations": 1000,
        "runs": 5,
    }

    results: dict[str, dict[str, float]] = {}

    for func_name, func in sorted(ALL_ENGINES.items()):
        print(f"Benchmarking {func_name}...", end=" ", flush=True)
        stats = run_benchmark(
            func,
            size=benchmark_params["size"],
            iterations=benchmark_params["iterations"],
            runs=benchmark_params["runs"],
        )
        results[func_name] = stats
        print("done")

    print("\n")
    print_benchmark_results(results)


if __name__ == "__main__":
    run_standalone_benchmarks()
