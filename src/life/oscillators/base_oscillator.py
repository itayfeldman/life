import numpy as np

Oscillator = np.ndarray


class BaseOscillator:
    """Base class for all oscillators"""

    is_oscillator = True

    @property
    def shape(self):
        return self.generate().shape

    def generate(self) -> Oscillator:
        """Generate oscillator output at the given time"""
        raise NotImplementedError("Subclasses must implement generate method")
