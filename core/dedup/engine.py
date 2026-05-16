"""
core/dedup/engine.py
Dedup engine dispatcher untuk Teleoder.

Tanggung jawab:
- Routing dedup mode ke engine yang tepat
- Interface tunggal yang dipakai downloader
- Foundation untuk mode berikutnya (smart, content)

Mode yang didukung:
- off   : tidak ada dedup, semua file didownload
- fast  : skip berdasarkan path/index (default)
"""

from typing import Optional

from core.dedup.fast import FastDedup


# Mode yang valid
VALID_DEDUP_MODES = {"off", "fast"}

# Mode default
DEFAULT_DEDUP_MODE = "fast"


class Deduplicator:
    """
    Unified dedup interface untuk downloader.

    Semua interaksi dedup masuk lewat sini.
    Downloader tidak perlu tahu engine mana yang aktif.

    Usage:
        dedup = Deduplicator(mode="fast", channel_base="/path/to/channel")
        dedup.build()

        if dedup.exists(output_path):
            skip
        else:
            download
            dedup.add(output_path)
    """

    def __init__(self, mode: str, channel_base: str):
        """
        Parameters
        ----------
        mode : str
            Dedup mode. Salah satu dari VALID_DEDUP_MODES.
        channel_base : str
            Absolute path ke folder channel.

        Raises
        ------
        ValueError
            Kalau mode tidak valid.
        """
        if mode not in VALID_DEDUP_MODES:
            raise ValueError(
                f"Dedup mode tidak valid: '{mode}'. "
                f"Pilih dari: {sorted(VALID_DEDUP_MODES)}"
            )

        self.mode = mode
        self._engine: Optional[FastDedup] = None

        if mode == "fast":
            self._engine = FastDedup(channel_base)

    def build(self):
        """
        Inisialisasi engine (scan folder, build index, dll).

        Tidak perlu dipanggil kalau mode = off.
        """
        if self._engine is not None:
            self._engine.build()

    def exists(self, output_path: str) -> bool:
        """
        Cek apakah file sudah ada menurut engine yang aktif.

        Parameters
        ----------
        output_path : str
            Absolute path file output.

        Returns
        -------
        bool
            False kalau mode = off (tidak pernah skip).
        """
        if self.mode == "off" or self._engine is None:
            return False

        return self._engine.exists(output_path)

    def add(self, output_path: str):
        """
        Daftarkan file yang baru didownload ke engine.

        No-op kalau mode = off.

        Parameters
        ----------
        output_path : str
            Absolute path file yang berhasil didownload.
        """
        if self._engine is not None:
            self._engine.add(output_path)
