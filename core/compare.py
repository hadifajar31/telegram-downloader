"""
core/compare.py
Compare engine untuk Teleoder.
Menyimpan index file existing per channel folder.
Foundation untuk dedup & sync system.
"""

import os

from core.logger import log_info


class CompareIndex:
    """
    Index file existing scoped per channel folder.

    Simpan relative path dari channel_base, bukan absolute path.
    Contoh entry: "photo/photo_123.jpg", "video/video_99.mp4"

    Scan dilakukan sekali saat build().
    Update manual via add() setelah download sukses.
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
        Simpan sebagai relative path dari channel_base.

        Aman dipanggil berkali-kali (reset index dulu).
        """
        self._index = set()

        if not os.path.isdir(self._channel_base):
            log_info(f"Compare index: folder not found, starting empty ({self._channel_base})")
            return

        for dirpath, _dirnames, filenames in os.walk(self._channel_base):
            for filename in filenames:
                abs_path = os.path.join(dirpath, filename)
                rel_path = os.path.relpath(abs_path, self._channel_base)
                self._index.add(rel_path)

        log_info(f"Compare index built: {len(self._index)} files ({self._channel_base})")

    def exists(self, output_path: str) -> bool:
        """
        Cek apakah file sudah ada di index.

        Parameters
        ----------
        output_path : str
            Absolute path file output.
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

    # Future: add remove(path) untuk cleanup file corrupt / partial download
    def __len__(self) -> int:
        return len(self._index)
