from .base_oscillator import BaseOscillator
import math


class SquareOscillator(BaseOscillator):
    """Square wave oscillator"""

    def generate(self, time):
        """Generate a square wave at the given time"""
        sine_val = math.sin(2 * math.pi * self.frequency * time)
        return 1 if sine_val >= 0 else -1
