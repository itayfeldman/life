import numpy as np

from .base_oscillator import BaseOscillator


class Glider(BaseOscillator):
    """Glider oscillator
    shape=(3,3)
    """

    def generate(self):
        return np.array([[0, 1, 0], [0, 0, 1], [1, 1, 1]], dtype="uint8")
