"""
core/dedup/fast.py
Fast dedup engine untuk Teleoder.

Berbasis path/index, tidak cek isi file.
Refactor dari core/compare.py sebagai foundation dedup system.

Mode ini:
- Scan folder saat pertama kali dipakai
- Skip file yang sudah ada berdasarkan path
- Update index setiap download sukses
"""

import os

from core.logger import log_info


class FastDedup:
    """
    Fast dedup engine berbasis path index.

    Scan dilakukan sekali saat build().
    Update manual via add() setelah download sukses.

    Index menyimpan relative path dari channel_base,
    bukan absolute path. Biar portable kalau folder dipindah.
    """

    def __init__(self, channel_base: str):
        """
        Parameters
        ----------
        channel_base : str
            Absolute path ke folder channel.
            Contoh: ~/Downloads/Tele/MyChannel
        """
        self._channel_base = channel_base
        self._index: set[str] = set()

    def build(self):
        """
        Scan channel_base secara recursive dan bangun index.

        Aman dipanggil berkali-kali (reset index setiap call).
        """
        self._index = set()

        if not os.path.isdir(self._channel_base):
            log_info(
                f"FastDedup: folder not found, starting empty ({self._channel_base})"
            )
            return

        for dirpath, _dirnames, filenames in os.walk(self._channel_base):
            for filename in filenames:
                abs_path = os.path.join(dirpath, filename)
                rel_path = os.path.relpath(abs_path, self._channel_base)
                self._index.add(rel_path)

        log_info(
            f"FastDedup: index built with {len(self._index)} files ({self._channel_base})"
        )

    def exists(self, output_path: str) -> bool:
        """
        Cek apakah file sudah ada di index.

        Parameters
        ----------
        output_path : str
            Absolute path file output.

        Returns
        -------
        bool
        """
        rel_path = os.path.relpath(output_path, self._channel_base)
        return rel_path in self._index

    def add(self, output_path: str):
        """
        Tambah file ke index setelah download sukses.

        Parameters
        ----------
        output_path : str
            Absolute path file yang baru didownload.
        """
        rel_path = os.path.relpath(output_path, self._channel_base)
        self._index.add(rel_path)

    def __len__(self) -> int:
        return len(self._index)
