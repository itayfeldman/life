from argparse import ArgumentParser

import matplotlib.pyplot as plt
from life.animator import Animator
from life.engine import convolution, window, loop, fast, ultra_fast, vectorized
from life.life import Life

# Safe function mapping to replace eval()
FUNCTION_MAP = {
    "convolution": convolution,
    "window": window,
    "loop": loop,
    "fast": fast,
    "ultra_fast": ultra_fast,
    "vectorized": vectorized,
}

parser = ArgumentParser(description="Enhanced Conway's Game of Life")

# Core arguments
parser.add_argument("--size", type=int, default=100, help="Grid size")
parser.add_argument("--seed", type=str, default="noise", help="Initial seed pattern")
parser.add_argument("--interval", type=int, default=350, help="Animation interval (ms)")
parser.add_argument("--cmap", type=str, default="binary", help="Matplotlib colormap")
parser.add_argument("--figsize", type=int, default=8, help="Figure size")
parser.add_argument(
    "--func",
    type=str,
    default="fast",
    choices=list(FUNCTION_MAP.keys()),
    help="Life calculation function"
)

# Enhanced visualization arguments
parser.add_argument("--show-stats", action="store_true", help="Show statistics overlay")
parser.add_argument("--fullscreen", action="store_true", help="Run in fullscreen mode")

args = parser.parse_args()

# Use safe function mapping instead of eval()
selected_func = FUNCTION_MAP[args.func]
life = Life(size=args.size, seed=args.seed, func=selected_func)

# Create enhanced animator
animator = Animator(
    life=life, 
    cmap=args.cmap, 
    interval=args.interval, 
    figsize=args.figsize,
    show_stats=args.show_stats
)

# Create animation
ani = animator()

# Fullscreen mode if requested
if args.fullscreen:
    mng = plt.get_current_fig_manager()
    try:
        mng.full_screen_toggle()
    except AttributeError:
        try:
            mng.window.state('zoomed')  # Windows
        except:
            pass  # Backend doesn't support fullscreen

print(f"🎮 Conway's Game of Life - Enhanced Edition")
print(f"📊 Size: {args.size}x{args.size} | Colormap: {args.cmap} | Function: {args.func}")
print(f"🎨 Stats: {'ON' if args.show_stats else 'OFF'}")
print(f"⚡ Press Ctrl+C to stop")

plt.show()
