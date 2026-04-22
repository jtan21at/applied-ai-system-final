"""Add the project root to sys.path so tests can import from the src package."""
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
