"""
core/dedup/__init__.py
Public API untuk dedup module Teleoder.

Usage:
    from core.dedup import HashScanner, HashCache, hash_file, is_same_file
    from core.dedup import HashEntry, DuplicateGroup, CacheEntry
"""

from core.dedup.cache import HashCache
from core.dedup.hasher import hash_file, hash_file_safe, is_same_file
from core.dedup.index import GlobalMediaIndex
from core.dedup.models import CacheEntry, DuplicateGroup, HashEntry, IndexStats
from core.dedup.scanner import HashScanner

__all__ = [
    "HashScanner",
    "HashCache",
    "GlobalMediaIndex",
    "HashEntry",
    "DuplicateGroup",
    "CacheEntry",
    "IndexStats",
    "hash_file",
    "hash_file_safe",
    "is_same_file",
]
