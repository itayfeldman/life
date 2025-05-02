from importlib import import_module
import os
import inspect


# Dictionary to store all oscillator classes
oscillators = {}


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
