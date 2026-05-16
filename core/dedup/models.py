"""
core/dedup/models.py
Data models untuk dedup engine Teleoder.
"""

from dataclasses import dataclass, field


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
