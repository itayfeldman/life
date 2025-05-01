import timeit

for func in ["convolution", "window", "loop"]:
    print(
        func,
        timeit.timeit(
            stmt="next(life)",
            setup=f"from life import Life; from count import {func}; life=Life(size=100, seed='noise', func={func})",
            number=1000,
        ),
    )
