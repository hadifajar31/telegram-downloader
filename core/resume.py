"""
core/resume.py
Manajemen state resume download per channel.
"""

import os
import json

RESUME_PATH = "data/resume.json"
SAVE_EVERY = 10


def _load_all() -> dict:
    """Baca semua resume dari disk. Return dict kosong kalau tidak ada."""
    if not os.path.exists(RESUME_PATH):
        return {}
    try:
        with open(RESUME_PATH, "r") as f:
            return json.load(f)
    except Exception:
        return {}


def _save_all(data: dict):
    """Tulis semua resume ke disk."""
    os.makedirs("data", exist_ok=True)
    with open(RESUME_PATH, "w") as f:
        json.dump(data, f, indent=2)


class ResumeManager:
    """
    Kelola resume state untuk satu channel.

    Tanggung jawab:
    - Load state awal
    - Update state per message
    - Batching save (tiap N update)
    - Final flush di akhir sesi
    """

    def __init__(self, channel_key: str, batch_size: int = SAVE_EVERY):
        """
        Parameters
        ----------
        channel_key : str
            Key unik untuk channel ini (biasanya username atau ID).
        batch_size : int
            Seberapa sering auto-save. Default setiap 10 update.
        """
        self.channel_key = channel_key
        self.batch_size = batch_size

        self._data = _load_all()
        self._counter = 0
        self._dirty = False

    @property
    def last_id(self) -> int:
        """Message ID terakhir yang tersimpan. 0 kalau belum ada."""
        return self._data.get(self.channel_key, 0)

    def update(self, message_id: int):
        """
        Update state dengan message ID terbaru.
        Auto-save kalau sudah mencapai batch_size.
        """
        self._data[self.channel_key] = message_id
        self._dirty = True
        self._counter += 1

        if self._counter % self.batch_size == 0:
            self._save()

    def flush(self):
        """Paksa simpan state sekarang, terlepas dari counter."""
        if self._dirty:
            self._save()

    def clear(self):
        """Hapus resume untuk channel ini."""
        if self.channel_key in self._data:
            del self._data[self.channel_key]
            self._save()

    def _save(self):
        _save_all(self._data)
        self._dirty = False
        self._counter = 0
