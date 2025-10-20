# Makes runtime a proper importable module
from .config import load_config
#from .cortex import process_input

__all__ = ["load_config", "process_input"]
