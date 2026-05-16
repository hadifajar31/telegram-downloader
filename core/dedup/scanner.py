"""
core/dedup/scanner.py
Folder hash scanner untuk Teleoder dedup engine.

Scan recursive, generate hash tiap file, group duplicate berdasarkan hash.
"""

import os
from collections import defaultdict
from typing import Callable, Optional

from core.dedup.hasher import hash_file_safe
from core.dedup.models import DuplicateGroup, HashEntry


class HashScanner:
    """
    Scanner folder recursive yang generate hash untuk tiap file.

    Gunakan scan() untuk mulai scan.
    Hasilnya bisa diakses via get_duplicates() atau get_all_entries().

    Scan tidak crash saat file bermasalah, tapi catat di error list.
    """

    def __init__(self, on_progress: Optional[Callable[[int, str], None]] = None):
        """
        Parameters
        ----------
        on_progress : callable | None
            Callback opsional dipanggil tiap file diproses.
            Signature: on_progress(count: int, path: str)
        """
        self._on_progress = on_progress
        self._entries: list[HashEntry] = []
        self._errors: list[str] = []

    def scan(self, folder: str) -> "HashScanner":
        """
        Scan folder secara recursive.

        Reset state sebelumnya kalau scan dipanggil ulang.

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

        count = 0

        for dirpath, _dirnames, filenames in os.walk(folder):
            for filename in filenames:
                abs_path = os.path.join(dirpath, filename)

                file_hash = hash_file_safe(abs_path)

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
        }
