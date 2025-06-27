from argparse import ArgumentParser

import matplotlib.pyplot as plt

from life.animator import Animator
from life.engine import *
from life.life import Life

parser = ArgumentParser()

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
parser.add_argument("--interval", type=int, default=350)
parser.add_argument("--seed", type=str, default="noise")
parser.add_argument("--size", type=int, default=100)

args = parser.parse_args()

life = Life(size=args.size, seed=args.seed, func=eval(args.func))
animator = Animator(
    life=life, cmap=args.cmap, interval=args.interval, figsize=args.figsize
)
ani = animator()
plt.show()  # type: ignore
