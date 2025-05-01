from .base_oscillator import BaseOscillator
import math


class SineOscillator(BaseOscillator):
    """Sine wave oscillator"""

    def generate(self, time):
        """Generate a sine wave at the given time"""
        return math.sin(2 * math.pi * self.frequency * time)
