from importlib import import_module
import os
import inspect

# Dictionary to store all oscillator classes
oscillators = {}


def register_oscillator(cls):
    """Decorator to register oscillator classes in the oscillators dictionary"""
    oscillators[cls.__name__] = cls
    return cls


def load_oscillators():
    """Load all oscillator modules from the oscillators directory"""
    oscillator_dir = os.path.join(os.path.dirname(__file__), "oscillators")

    # Get all Python files in the oscillators directory
    for filename in os.listdir(oscillator_dir):
        if filename.endswith(".py") and filename != "__init__.py":
            module_name = filename[:-3]  # Remove .py extension
            module_path = f"oscillators.{module_name}"

            # Import the module
            module = import_module(module_path)

            # Find all classes in the module and register them if they're oscillators
            for name, obj in inspect.getmembers(module):
                if (
                    inspect.isclass(obj)
                    and hasattr(obj, "is_oscillator")
                    and obj.is_oscillator
                ):
                    oscillators[name] = obj


# Load all oscillators when this module is imported
load_oscillators()


def create_oscillator(oscillator_type, *args, **kwargs):
    """Factory function to create oscillator instances"""
    if oscillator_type not in oscillators:
        raise ValueError(f"Unknown oscillator type: {oscillator_type}")

    return oscillators[oscillator_type](*args, **kwargs)
