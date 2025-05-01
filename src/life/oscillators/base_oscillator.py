import numpy as np

Oscillator = np.ndarray


class BaseOscillator:
    """Base class for all oscillators"""

    is_oscillator = True

    def __init__(self, frequency=440):
        self.frequency = frequency

    def generate(self, time):
        """Generate oscillator output at the given time"""
        raise NotImplementedError("Subclasses must implement generate method")
