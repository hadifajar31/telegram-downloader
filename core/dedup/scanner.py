"""
core/dedup/scanner.py
Folder hash scanner untuk Teleoder dedup engine.

Scan recursive, generate hash tiap file, group duplicate berdasarkan hash.
Support optional HashCache untuk skip re-hash file yang belum berubah.
"""

import os
from collections import defaultdict
from typing import Callable, Optional

from core.dedup.cache import HashCache
from core.dedup.hasher import hash_file_safe
from core.dedup.models import DuplicateGroup, HashEntry


class HashScanner:
    """
    Scanner folder recursive yang generate hash untuk tiap file.

    Gunakan scan() untuk mulai scan.
    Hasilnya bisa diakses via get_duplicates() atau get_all_entries().

    Opsional: pass HashCache untuk reuse hash file yang belum berubah.
    Scan tidak crash saat file bermasalah, tapi catat di error list.
    """

    def __init__(
        self,
        on_progress: Optional[Callable[[int, str], None]] = None,
        cache: Optional[HashCache] = None,
    ):
        """
        Parameters
        ----------
        on_progress : callable | None
            Callback opsional dipanggil tiap file diproses.
            Signature: on_progress(count: int, path: str)

        cache : HashCache | None
            Cache opsional untuk reuse hash file yang belum berubah.
            Kalau None, semua file di-hash ulang setiap scan.
        """
        self._on_progress = on_progress
        self._cache = cache
        self._entries: list[HashEntry] = []
        self._errors: list[str] = []
        self._cache_hits: int = 0
        self._cache_misses: int = 0

    def scan(self, folder: str) -> "HashScanner":
        """
        Scan folder secara recursive.

        Reset state sebelumnya kalau scan dipanggil ulang.
        Kalau cache di-set, reuse hash untuk file yang belum berubah.

        Parameters
        ----------
        folder : str
            Absolute path ke folder yang mau di-scan.

        Returns
        -------
        HashScanner
            Self, biar bisa chaining.

        Raises
        ------
        NotADirectoryError
            Kalau path bukan folder atau tidak ada.
        """
        if not os.path.isdir(folder):
            raise NotADirectoryError(f"Folder tidak ditemukan: {folder}")

        self._entries = []
        self._errors = []
        self._cache_hits = 0
        self._cache_misses = 0

        count = 0

        for dirpath, _dirnames, filenames in os.walk(folder):
            for filename in filenames:
                abs_path = os.path.join(dirpath, filename)

                file_hash = self._resolve_hash(abs_path)

                if file_hash is None:
                    self._errors.append(abs_path)
                    continue

                try:
                    size = os.path.getsize(abs_path)
                except OSError:
                    size = 0

                entry = HashEntry(path=abs_path, hash=file_hash, size=size)
                self._entries.append(entry)

                count += 1
                if self._on_progress:
                    self._on_progress(count, abs_path)

        return self

    def _resolve_hash(self, path: str) -> Optional[str]:
        """
        Ambil hash untuk satu file.

        Urutan:
        1. Cek cache — kalau hit dan valid, reuse
        2. Kalau miss atau tidak ada cache — hash ulang
        3. Kalau berhasil hash — simpan ke cache

        Parameters
        ----------
        path : str
            Absolute path ke file.

        Returns
        -------
        str | None
            Hash file, atau None kalau gagal.
        """
        # Cek cache dulu kalau ada
        if self._cache is not None:
            cached = self._cache.get(path)
            if cached is not None:
                self._cache_hits += 1
                return cached
            self._cache_misses += 1

        # Hash ulang
        file_hash = hash_file_safe(path)

        # Simpan ke cache kalau berhasil
        if file_hash is not None and self._cache is not None:
            self._cache.put(path, file_hash)

        return file_hash

    def get_all_entries(self) -> list[HashEntry]:
        """
        Kembalikan semua file yang berhasil di-hash.

        Returns
        -------
        list[HashEntry]
        """
        return list(self._entries)

    def get_duplicates(self) -> list[DuplicateGroup]:
        """
        Kembalikan hanya file yang duplicate (hash sama, lebih dari 1 file).

        Returns
        -------
        list[DuplicateGroup]
            Diurutkan dari group dengan file terbanyak.
        """
        groups: dict[str, list[HashEntry]] = defaultdict(list)

        for entry in self._entries:
            groups[entry.hash].append(entry)

        duplicates = [
            DuplicateGroup(hash=h, files=entries)
            for h, entries in groups.items()
            if len(entries) > 1
        ]

        duplicates.sort(key=lambda g: g.count, reverse=True)

        return duplicates

    def get_errors(self) -> list[str]:
        """
        Kembalikan daftar file yang gagal di-hash.

        Returns
        -------
        list[str]
            Daftar absolute path file bermasalah.
        """
        return list(self._errors)

    @property
    def total_files(self) -> int:
        """Total file yang berhasil di-scan."""
        return len(self._entries)

    @property
    def total_errors(self) -> int:
        """Total file yang gagal di-scan."""
        return len(self._errors)

    @property
    def cache_hits(self) -> int:
        """Jumlah file yang hash-nya diambil dari cache (scan terakhir)."""
        return self._cache_hits

    @property
    def cache_misses(self) -> int:
        """Jumlah file yang di-hash ulang karena cache miss (scan terakhir)."""
        return self._cache_misses

    def summary(self) -> dict:
        """
        Ringkasan hasil scan.

        Returns
        -------
        dict dengan key:
            total_files     : int
            total_errors    : int
            duplicate_groups: int
            duplicate_files : int
            wasted_bytes    : int
            cache_hits      : int
            cache_misses    : int
        """
        dupes = self.get_duplicates()
        duplicate_files = sum(g.count for g in dupes)
        wasted_bytes = sum(g.wasted_bytes for g in dupes)

        return {
            "total_files": self.total_files,
            "total_errors": self.total_errors,
            "duplicate_groups": len(dupes),
            "duplicate_files": duplicate_files,
            "wasted_bytes": wasted_bytes,
            "cache_hits": self._cache_hits,
            "cache_misses": self._cache_misses,
        }
