import timeit
import statistics
from life.life import Life
from life.counters import convolution, window, loop


from typing import Callable, Dict, Any


def benchmark_function(
    func_name: str,
    func: Callable[..., Any],
    size: int = 100,
    iterations: int = 1000,
    runs: int = 5,
) -> Dict[str, float]:
    """Run multiple benchmark runs and return statistics"""
    times: list[float] = []

    for _ in range(runs):
        life = Life(size=size, seed="noise", func=func)
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


if __name__ == "__main__":
    funcs = {"convolution": convolution, "window": window, "loop": loop}

    print(f"{'Function':<12} {'Mean':<10} {'StdDev':<10} {'Min':<10} {'Max':<10}")
    print("-" * 60)

    for func_name, func in funcs.items():
        stats = benchmark_function(func_name, func)
        print(
            f"{func_name:<12} {stats['mean']:<10.4f} {stats['stdev']:<10.4f} "
            f"{stats['min']:<10.4f} {stats['max']:<10.4f}"
        )
