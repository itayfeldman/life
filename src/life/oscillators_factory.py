from importlib import import_module
import os
import inspect

# Dictionary to store all oscillator classes
oscillators = {}


def load_classes_from_directory(directory, base_package, class_filter=None):
    """
    Load classes from modules in a directory that match a filter

    Args:
        directory: Directory to scan for modules
        base_package: Base package name for imports
        class_filter: Function that takes a class and returns True if it should be included

    Returns:
        Dictionary mapping class names to class objects
    """
    result = {}
    try:
        for filename in os.listdir(directory):
            if filename.endswith(".py") and filename != "__init__.py":
                module_name = filename[:-3]
                module_path = f"{base_package}.{module_name}"

                try:
                    module = import_module(module_path)

                    for name, obj in inspect.getmembers(module):
                        if inspect.isclass(obj) and (
                            class_filter is None or class_filter(obj)
                        ):
                            result[name] = obj
                except ImportError as e:
                    print(f"Error importing {module_path}: {e}")
    except Exception as e:
        print(f"Error loading classes from {directory}: {e}")

    return result


def load_oscillators():
    oscillator_dir = os.path.join(os.path.dirname(__file__), "oscillators")
    oscillators.update(
        load_classes_from_directory(
            oscillator_dir,
            "oscillators",
            lambda cls: hasattr(cls, "is_oscillator") and cls.is_oscillator,
        )
    )


# Replace direct loading with a function
def get_oscillators():
    """Get all oscillator classes, loading them if necessary"""
    if not oscillators:
        load_oscillators()
    return oscillators


get_oscillators()
