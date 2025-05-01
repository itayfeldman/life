from life.oscillators_factory import create_oscillator, oscillators


def main():
    # Print all available oscillator types
    print("Available oscillator types:")
    for name in oscillators:
        print(f"- {name}")

    # Create oscillators using the factory
    sine_osc = create_oscillator("SineOscillator", frequency=440)
    square_osc = create_oscillator("SquareOscillator", frequency=220)

    # Generate some values
    time = 0.001
    print(f"Sine oscillator output at t={time}: {sine_osc.generate(time)}")
    print(f"Square oscillator output at t={time}: {square_osc.generate(time)}")


if __name__ == "__main__":
    main()
