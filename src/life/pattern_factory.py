from importlib import import_module
import os
import inspect

from life import logger
from life.patterns import Pattern

# Dictionary to store all pattern objects
patterns = {}


def load_objects_from_directory(directory, base_package, filter=None):
    """
    Load object from modules in a directory that match a filter

    Args:
        directory: Directory to scan for modules
        base_package: Base package name for imports
        filter: Function that takes an object and returns True if it should be included

    Returns:
        Dictionary mapping object names to objects
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
                        if filter and callable(filter) and filter(obj):
                            result[name] = obj
                except ImportError as e:
                    logger.error(f"Error importing {module_path}: {e}")
    except Exception as e:
        logger.error(f"Error loading patterns from {directory}: {e}")

    return result


def load_patterns():
    pattern_dir = os.path.join(os.path.dirname(__file__), "patterns")
    patterns.update(
        load_objects_from_directory(
            pattern_dir,
            "life.patterns",
            lambda obj: type(obj) == Pattern,
        )
    )


# Replace direct loading with a function
def get_patterns():
    """Get all pattern classes, loading them if necessary"""
    if not patterns:
        load_patterns()
    return patterns


get_patterns()


if __name__ == "__main__":
    get_patterns()
