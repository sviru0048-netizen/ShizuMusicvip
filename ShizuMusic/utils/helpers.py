"""
ShizuMusic/utils/helpers.py
Common helper functions shared across modules.
"""
import os


def delete_file(path: str) -> None:
    """Silently delete a file if it exists."""
    try:
        if path and os.path.exists(path):
            os.remove(path)
    except Exception:
        pass
