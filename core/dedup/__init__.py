"""
core/dedup/__init__.py
Public API untuk dedup module Teleoder.

Usage:
    from core.dedup import HashScanner, hash_file, is_same_file
    from core.dedup import HashEntry, DuplicateGroup
"""

from core.dedup.hasher import hash_file, hash_file_safe, is_same_file
from core.dedup.models import DuplicateGroup, HashEntry
from core.dedup.scanner import HashScanner

__all__ = [
    "HashScanner",
    "HashEntry",
    "DuplicateGroup",
    "hash_file",
    "hash_file_safe",
    "is_same_file",
]
