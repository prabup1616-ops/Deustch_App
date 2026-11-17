"""
German B1 Goethe Prep & Duel - Core Package
"""
import sys
import os

_SRC_DIR = os.path.dirname(os.path.abspath(__file__))
if _SRC_DIR not in sys.path:
    sys.path.insert(0, _SRC_DIR)

_ROOT_DIR = os.path.dirname(_SRC_DIR)
if _ROOT_DIR not in sys.path:
    sys.path.insert(0, _ROOT_DIR)

__version__ = "2.0.0"
