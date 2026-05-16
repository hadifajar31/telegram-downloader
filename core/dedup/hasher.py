"""
core/dedup/hasher.py
Hash generator untuk Teleoder dedup engine.

Baca file per chunk biar aman untuk file besar.
Pakai SHA256 sebagai hash algorithm.
"""

import hashlib
import os

# Ukuran chunk per baca: 1 MB
CHUNK_SIZE = 1024 * 1024


def hash_file(path: str) -> str:
    """
    Hitung SHA256 hash dari satu file.

    Baca per chunk (1 MB) biar aman untuk file besar.

    Parameters
    ----------
    path : str
        Absolute path ke file.

    Returns
    -------
    str
        SHA256 hex digest.

    Raises
    ------
    FileNotFoundError
        Kalau file tidak ditemukan.
    PermissionError
        Kalau file tidak bisa dibaca.
    OSError
        Error filesystem lainnya.
    """
    hasher = hashlib.sha256()

    with open(path, "rb") as f:
        while True:
            chunk = f.read(CHUNK_SIZE)
            if not chunk:
                break
            hasher.update(chunk)

    return hasher.hexdigest()


def hash_file_safe(path: str) -> str | None:
    """
    Versi aman dari hash_file. Return None kalau ada error.

    Cocok untuk scanner yang tidak mau crash saat ada file bermasalah.

    Parameters
    ----------
    path : str
        Absolute path ke file.

    Returns
    -------
    str | None
        SHA256 hex digest, atau None kalau gagal.
    """
    try:
        return hash_file(path)
    except (OSError, PermissionError):
        return None


def is_same_file(path_a: str, path_b: str) -> bool:
    """
    Cek apakah dua file memiliki konten yang sama berdasarkan hash.

    Quick check: bandingkan ukuran dulu sebelum hash.

    Parameters
    ----------
    path_a : str
        Path file pertama.
    path_b : str
        Path file kedua.

    Returns
    -------
    bool
        True kalau isi file sama.
    """
    # Ukuran berbeda → pasti beda
    try:
        if os.path.getsize(path_a) != os.path.getsize(path_b):
            return False
    except OSError:
        return False

    hash_a = hash_file_safe(path_a)
    hash_b = hash_file_safe(path_b)

    if hash_a is None or hash_b is None:
        return False

    return hash_a == hash_b
