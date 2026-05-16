"""
core/dedup/cache.py
In-memory hash cache untuk Teleoder dedup engine.

Cache valid kalau size dan mtime file tidak berubah sejak terakhir di-hash.
Belum persist ke disk — fondasi untuk JSON/SQLite cache nanti.
"""

import os
from typing import Optional

from core.dedup.models import CacheEntry


class HashCache:
    """
    In-memory cache hash file berbasis path → CacheEntry.

    Validasi cache pakai dua kondisi:
    - size sama
    - mtime sama

    Kalau salah satu berbeda, cache dianggap stale dan file perlu di-hash ulang.

    Usage:
        cache = HashCache()

        # Ambil hash kalau cache valid
        cached_hash = cache.get(path)

        # Simpan hasil hash baru
        cache.put(path, hash_value)

        # Hapus entry
        cache.invalidate(path)
    """

    def __init__(self):
        self._store: dict[str, CacheEntry] = {}

    def get(self, path: str) -> Optional[str]:
        """
        Ambil hash dari cache kalau masih valid.

        Validasi: size dan mtime file saat ini harus sama dengan yang di-cache.

        Parameters
        ----------
        path : str
            Absolute path ke file.

        Returns
        -------
        str | None
            Hash dari cache kalau valid, None kalau miss atau stale.
        """
        entry = self._store.get(path)

        if entry is None:
            return None

        try:
            current_size = os.path.getsize(path)
            current_mtime = os.path.getmtime(path)
        except OSError:
            # File tidak bisa diakses → cache tidak relevan
            self._store.pop(path, None)
            return None

        if current_size != entry.size or current_mtime != entry.mtime:
            # File berubah → invalidate
            del self._store[path]
            return None

        return entry.hash

    def put(self, path: str, file_hash: str) -> bool:
        """
        Simpan hash ke cache dengan metadata file saat ini.

        Parameters
        ----------
        path : str
            Absolute path ke file.
        file_hash : str
            SHA256 hex digest file.

        Returns
        -------
        bool
            True kalau berhasil disimpan, False kalau file tidak bisa diakses.
        """
        try:
            size = os.path.getsize(path)
            mtime = os.path.getmtime(path)
        except OSError:
            return False

        self._store[path] = CacheEntry(hash=file_hash, size=size, mtime=mtime)
        return True

    def invalidate(self, path: str):
        """
        Hapus entry cache untuk path tertentu.

        Aman dipanggil walaupun path tidak ada di cache.

        Parameters
        ----------
        path : str
            Absolute path ke file.
        """
        self._store.pop(path, None)

    def clear(self):
        """Hapus semua entry cache."""
        self._store.clear()

    @property
    def size(self) -> int:
        """Jumlah entry di cache saat ini."""
        return len(self._store)

    def __contains__(self, path: str) -> bool:
        """Cek apakah path ada di cache (tanpa validasi)."""
        return path in self._store
