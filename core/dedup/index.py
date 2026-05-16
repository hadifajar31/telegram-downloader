"""
core/dedup/index.py
Global media index untuk dedup engine Teleoder.

Menyimpan relasi hash → set[path] secara global,
sebagai fondasi smart skip dan multi-source dedup.
"""

from collections import defaultdict
from core.dedup.models import IndexStats


class GlobalMediaIndex:
    """
    In-memory index untuk melacak hash file secara global.

    Struktur internal: hash (str) → set of absolute paths (str).
    Semua operasi O(1) rata-rata.
    """

    def __init__(self):
        self._index: dict[str, set[str]] = defaultdict(set)
        self._reverse: dict[str, str] = {}

    # ─── Write API ────────────────────────────────────────────────────

    def add(self, hash: str, path: str) -> None:
        """
        Tambah path ke index dengan hash-nya.

        Kalau path sudah ada dengan hash berbeda,
        path lama di-remove dulu sebelum ditambah ulang.
        """
        if path in self._reverse and self._reverse[path] != hash:
            self._remove_path(path)

        self._index[hash].add(path)
        self._reverse[path] = hash

    def remove(self, path: str) -> bool:
        """
        Hapus path dari index.

        Hash yang sudah tidak punya path manapun ikut di-cleanup otomatis.

        Returns True kalau path ditemukan dan dihapus, False kalau tidak ada.
        """
        if path not in self._reverse:
            return False
        self._remove_path(path)
        return True

    def clear(self) -> None:
        """Kosongkan seluruh index."""
        self._index.clear()
        self._reverse.clear()

    # ─── Read API ─────────────────────────────────────────────────────

    def get(self, hash: str) -> set[str]:
        """
        Ambil semua path yang punya hash ini.

        Returns set kosong kalau hash tidak ada.
        """
        return set(self._index.get(hash, set()))

    def exists(self, hash: str) -> bool:
        """
        Cek apakah hash sudah ada di index.

        Returns True kalau hash ada dan punya minimal 1 path.
        """
        return hash in self._index and len(self._index[hash]) > 0

    # ─── Stats ────────────────────────────────────────────────────────

    @property
    def total_hashes(self) -> int:
        """Jumlah hash unik di index."""
        return len(self._index)

    @property
    def total_files(self) -> int:
        """Jumlah total path di index."""
        return len(self._reverse)

    @property
    def duplicate_hashes(self) -> int:
        """Jumlah hash yang punya lebih dari 1 path."""
        return sum(1 for paths in self._index.values() if len(paths) > 1)

    def stats(self) -> IndexStats:
        """Ringkasan statistik index saat ini."""
        from core.dedup.models import IndexStats
        return IndexStats(
            total_hashes=self.total_hashes,
            total_files=self.total_files,
            duplicate_hashes=self.duplicate_hashes,
        )

    # ─── Internal ─────────────────────────────────────────────────────

    def _remove_path(self, path: str) -> None:
        """Hapus path dari index dan reverse map. Cleanup hash kosong."""
        hash = self._reverse.pop(path)
        self._index[hash].discard(path)
        if not self._index[hash]:
            del self._index[hash]

    def __repr__(self) -> str:
        return (
            f"GlobalMediaIndex("
            f"hashes={self.total_hashes}, "
            f"files={self.total_files}, "
            f"duplicates={self.duplicate_hashes})"
        )