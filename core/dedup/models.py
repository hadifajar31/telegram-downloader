"""
core/dedup/models.py
Data models untuk dedup engine Teleoder.
"""

from dataclasses import dataclass, field


@dataclass
class CacheEntry:
    """
    Metadata cache untuk satu file.

    Dipakai untuk validasi apakah file berubah sejak terakhir di-hash.
    Cache dianggap valid kalau size dan mtime masih sama.

    Attributes
    ----------
    hash : str
        SHA256 hex digest file.
    size : int
        Ukuran file dalam bytes saat di-hash.
    mtime : float
        Modified time (os.path.getmtime) saat di-hash.
    """

    hash: str
    size: int
    mtime: float


@dataclass
class HashEntry:
    """
    Representasi satu file beserta hash-nya.

    Attributes
    ----------
    path : str
        Absolute path ke file.
    hash : str
        SHA256 hex digest file.
    size : int
        Ukuran file dalam bytes.
    """

    path: str
    hash: str
    size: int


@dataclass
class DuplicateGroup:
    """
    Kumpulan file yang memiliki hash sama (duplicate).

    Attributes
    ----------
    hash : str
        Hash yang sama untuk semua file di group ini.
    files : list[HashEntry]
        Daftar file duplicate.
    """

    hash: str
    files: list[HashEntry] = field(default_factory=list)

    @property
    def count(self) -> int:
        """Jumlah file di group ini."""
        return len(self.files)

    @property
    def size(self) -> int:
        """Ukuran satu file (semua file di group ukurannya sama)."""
        return self.files[0].size if self.files else 0

    @property
    def wasted_bytes(self) -> int:
        """Estimasi space yang terbuang karena duplicate."""
        if self.count <= 1:
            return 0
        return self.size * (self.count - 1)

@dataclass
class IndexStats:
    """
    Statistik global media index.

    Attributes
    ----------
    total_hashes : int
        Jumlah hash unik di index.
    total_files : int
        Jumlah total path yang terdaftar.
    duplicate_hashes : int
        Jumlah hash yang punya lebih dari 1 path.
    """

    total_hashes: int
    total_files: int
    duplicate_hashes: int