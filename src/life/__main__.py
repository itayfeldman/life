from argparse import ArgumentParser

import matplotlib.pyplot as plt

from life import logger
from life.animator import Animator
from life.engine import convolution, window, loop, fast, ultra_fast, vectorized
from life.life import Life

ENGINES = {
    "convolution": convolution,
    "window": window,
    "loop": loop,
    "fast": fast,
    "ultra_fast": ultra_fast,
    "vectorized": vectorized,
}

parser = ArgumentParser()
parser.add_argument("--size", type=int, default=100)
parser.add_argument("--seed", type=str, default="noise")
parser.add_argument("--interval", type=int, default=350)
parser.add_argument("--cmap", type=str, default="binary")
parser.add_argument("--figsize", type=int, default=8)
parser.add_argument(
    "--func",
    type=str,
    default="fast",
    choices=[
        "convolution",
        "window",
        "loop",
        "fast",
        "ultra_fast",
        "vectorized",
    ],
)
args = parser.parse_args()

logger.info(
    f"Starting Life simulation with size={args.size}, seed={args.seed}, func={args.func}, interval={args.interval}, cmap={args.cmap}, figsize={args.figsize}"
)
life = Life(size=args.size, seed=args.seed, func=ENGINES[args.func])
logger.info("Life object created successfully")
animator = Animator(
    life=life, cmap=args.cmap, interval=args.interval, figsize=args.figsize
)
ani = animator()
plt.show()  # type: ignore
