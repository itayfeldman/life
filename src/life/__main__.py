from argparse import ArgumentParser

import matplotlib.pyplot as plt

from life import logger
from life.engines import ENGINE_REGISTRY
from life.infrastructure import CellsPatternRepository
from life.presentation import MatplotlibAnimator, PygameVisualizer
from life.simulation import LifeSimulation


def main() -> None:
    parser = ArgumentParser(description="Conway's Game of Life")
    parser.add_argument("--size", type=int, default=100)
    parser.add_argument("--seed", type=str, default="noise")
    parser.add_argument("--interval", type=int, default=100)
    parser.add_argument(
        "--frontend",
        type=str,
        default="pygame",
        choices=["matplotlib", "pygame"],
    )
    # matplotlib-only options
    parser.add_argument("--cmap", type=str, default="binary")
    parser.add_argument("--figsize", type=int, default=8)
    # pygame-only options
    parser.add_argument("--window", type=int, default=800)
    parser.add_argument(
        "--engine",
        "--func",
        dest="engine",
        type=str,
        default="fast",
        choices=list(ENGINE_REGISTRY.keys()),
    )
    args = parser.parse_args()

    repository = CellsPatternRepository()
    engine = ENGINE_REGISTRY[args.engine]

    logger.info(
        "Starting simulation: size=%s, seed=%s, engine=%s, "
        "interval=%s, frontend=%s",
        args.size, args.seed, args.engine, args.interval, args.frontend,
    )

    sim = LifeSimulation(
        size=args.size,
        seed=args.seed,
        engine=engine,
        repository=repository,
    )

    if args.frontend == "pygame":
        PygameVisualizer(
            simulation=sim,
            interval=args.interval,
            window_size=args.window,
        )()
    else:
        animator = MatplotlibAnimator(
            simulation=sim,
            cmap=args.cmap,
            interval=args.interval,
            figsize=args.figsize,
        )
        ani = animator()  # must stay referenced; GC would stop the animation
        plt.show()  # type: ignore


if __name__ == "__main__":
    main()
