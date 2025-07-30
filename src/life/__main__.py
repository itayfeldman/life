from argparse import ArgumentParser

import matplotlib.pyplot as plt
from life.animator import Animator
from life.visualizer import EnhancedVisualizer
from life.engine import *
from life.life import Life

def main():
    parser = ArgumentParser(description="Conway's Game of Life Simulator")
    parser.add_argument("--size", type=int, default=100, help="Grid size (default: 100)")
    parser.add_argument("--seed", type=str, default="noise", help="Seed type or pattern name (default: noise)")
    parser.add_argument("--interval", type=int, default=350, help="Animation interval in ms (default: 350)")
    parser.add_argument("--cmap", type=str, default="binary", help="Matplotlib colormap (default: binary)")
    parser.add_argument("--figsize", type=int, default=8, help="Figure size (default: 8)")
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
        help="Algorithm to use (default: fast)"
    )
    parser.add_argument(
        "--enhanced", 
        action="store_true", 
        help="Use enhanced visualizer with statistics and controls"
    )
    parser.add_argument(
        "--show-grid", 
        action="store_true", 
        help="Show grid lines (enhanced visualizer only)"
    )
    parser.add_argument(
        "--no-stats", 
        action="store_true", 
        help="Hide statistics panel (enhanced visualizer only)"
    )
    parser.add_argument(
        "--title", 
        type=str, 
        help="Custom title for the visualization"
    )
    
    args = parser.parse_args()

    # Create Life instance
    life = Life(size=args.size, seed=args.seed, func=eval(args.func))
    
    if args.enhanced:
        # Use enhanced visualizer
        visualizer = EnhancedVisualizer(
            life=life,
            cmap=args.cmap,
            interval=args.interval,
            figsize=(args.figsize, args.figsize),
            show_grid=args.show_grid,
            show_stats=not args.no_stats,
            title=args.title
        )
        ani = visualizer.animate()
    else:
        # Use original animator
        animator = Animator(
            life=life, cmap=args.cmap, interval=args.interval, figsize=args.figsize
        )
        ani = animator()
    
    plt.show()

if __name__ == "__main__":
    main()
