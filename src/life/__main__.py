import time
from argparse import ArgumentParser, RawDescriptionHelpFormatter

from life import logger
from life.engines import ENGINE_REGISTRY
from life.infrastructure import RlePatternRepository
from life.presentation import FRONTEND_REGISTRY
from life.simulation import LifeSimulation


def run_bench(
    generations: int,
    size: int,
    seed: str,
    engine_name: str,
) -> None:
    repository = RlePatternRepository()
    engine = ENGINE_REGISTRY[engine_name]
    sim = LifeSimulation(size=size, seed=seed, engine=engine, repository=repository)

    t0 = time.perf_counter()
    for _ in range(generations):
        next(sim)
    elapsed = time.perf_counter() - t0

    mean_ms = elapsed / generations * 1000
    gens_per_sec = generations / elapsed
    print(f"engine={engine_name}  size={size}x{size}  generations={generations}")
    print(f"  total: {elapsed:.3f}s  |  {mean_ms:.3f} ms/gen  |  {gens_per_sec:.1f} gen/s")


def build_parser() -> ArgumentParser:
    repo = RlePatternRepository()
    pattern_names = sorted(repo.list_names())
    engine_names = sorted(ENGINE_REGISTRY.keys())

    parser = ArgumentParser(
        description="Conway's Game of Life",
        formatter_class=lambda prog: RawDescriptionHelpFormatter(
            prog, max_help_position=28
        ),
    )
    parser.add_argument(
        "--size", type=int, default=100, metavar="N",
        help="Grid side length in cells (default: 100, range: 10–1000).",
    )
    parser.add_argument(
        "--seed", type=str, default="noise", metavar="SEED",
        help=(
            "Initial state. Built-in: noise, symmetric, scattered. "
            f"Patterns: {', '.join(pattern_names)}."
        ),
    )
    parser.add_argument(
        "--interval", type=int, default=100, metavar="MS",
        help="Delay between generations in milliseconds (default: 100).",
    )
    parser.add_argument(
        "--frontend",
        type=str, default="pygame", choices=sorted(FRONTEND_REGISTRY.keys()),
        help="Visualisation frontend (default: pygame).",
    )
    parser.add_argument(
        "--cmap", type=str, default="binary", metavar="NAME",
        help="Matplotlib colormap name, e.g. binary, viridis (default: binary).",
    )
    parser.add_argument(
        "--display-size",
        dest="display_size", type=int, default=10, metavar="N",
        help=(
            "Display size in inches (default: 10). "
            "Matplotlib uses this as figsize; pygame multiplies by 100 for pixels."
        ),
    )
    parser.add_argument(
        "--engine",
        dest="engine", type=str, default="pad_slice",
        choices=list(ENGINE_REGISTRY.keys()),
        help=f"Next-state engine (default: pad_slice). Choices: {', '.join(engine_names)}.",
    )
    parser.add_argument(
        "--bench",
        type=int, default=None, metavar="N",
        help="Run N generations headlessly and print timing summary.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()

    if args.bench is not None:
        run_bench(
            generations=args.bench,
            size=args.size,
            seed=args.seed,
            engine_name=args.engine,
        )
        return

    repository = RlePatternRepository()
    engine = ENGINE_REGISTRY[args.engine]

    logger.info(
        "Starting simulation: size=%s, seed=%s, engine=%s, "
        "interval=%s, frontend=%s, display_size=%s",
        args.size,
        args.seed,
        args.engine,
        args.interval,
        args.frontend,
        args.display_size,
    )

    sim = LifeSimulation(
        size=args.size,
        seed=args.seed,
        engine=engine,
        repository=repository,
    )

    visualizer = FRONTEND_REGISTRY[args.frontend](
        sim, args.interval, args.display_size, args.cmap
    )
    visualizer()


if __name__ == "__main__":
    main()
