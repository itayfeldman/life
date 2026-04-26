from argparse import ArgumentParser, Namespace

import matplotlib.pyplot as plt

from life import logger
from life.engines import ENGINE_REGISTRY
from life.infrastructure import CellsPatternRepository
from life.presentation import MatplotlibAnimator, PygameVisualizer
from life.simulation import LifeSimulation

# Converts display-size inches to pygame window pixels (100 px per inch).
PYGAME_DPI = 100


def build_parser() -> ArgumentParser:
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
    parser.add_argument("--cmap", type=str, default="binary")
    parser.add_argument(
        "--display-size",
        dest="display_size",
        type=int,
        default=10,
        metavar="N",
        help=(
            "Display size in inches. "
            "Matplotlib uses this directly as figsize; "
            "pygame multiplies by 100 to get window pixels."
        ),
    )
    parser.add_argument(
        "--engine",
        dest="engine",
        type=str,
        default="fast",
        choices=list(ENGINE_REGISTRY.keys()),
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()

    repository = CellsPatternRepository()
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

    if args.frontend == "pygame":
        PygameVisualizer(
            simulation=sim,
            interval=args.interval,
            window_size=args.display_size * PYGAME_DPI,
        )()
    else:
        animator = MatplotlibAnimator(
            simulation=sim,
            cmap=args.cmap,
            interval=args.interval,
            figsize=args.display_size,
        )
        ani = animator()  # must stay referenced; GC would stop the animation
        plt.show()  # type: ignore


if __name__ == "__main__":
    main()
