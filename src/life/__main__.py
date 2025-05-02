from argparse import ArgumentParser

import matplotlib.pyplot as plt
from animator import Animator
from count import convolution, loop, window
from life import Life

parser = ArgumentParser()
parser.add_argument("--size", type=int, default=100)
parser.add_argument("--seed", type=str, default="noise")
parser.add_argument("--interval", type=int, default=750)
parser.add_argument("--cmap", type=str, default="binary")
parser.add_argument("--figsize", type=int, default=10)
parser.add_argument(
    "--func", type=str, default="window", choices=["convolution", "window", "loop"]
)
args = parser.parse_args()

func_map = {"convolution": convolution, "window": window, "loop": loop}
selected_func = func_map[args.func]


life = Life(size=args.size, seed=args.seed, func=selected_func)
animator = Animator(
    frames=life, cmap=args.cmap, interval=args.interval, figsize=args.figsize
)
ani = animator()
plt.show()
