"""
core/naming.py
Filename generation dan naming logic untuk Teleoder.

Tanggung jawab:
- Generate filename berdasarkan tipe media
- Fallback extension per media type
- Duplicate rename handling
- Native vs document filename strategy
"""

import os

from telethon.tl.types import DocumentAttributeFilename

from core.utils import safe_filename


# ─── Constants ────────────────────────────────────────────────────────────────

# Fallback extension per media type
FALLBACK_EXT = {
    "photo": "jpg",
    "photo_document": "jpg",
    "video": "mp4",
    "video_note": "mp4",
    "video_document": "mp4",
    "gif": "mp4",
    "audio": "mp3",
    "voice": "ogg",
    "sticker": "webp",
    "archive": "zip",
    "document": "bin",
}

# Media yang pakai auto-generated filename (bukan nama asli dari Telegram)
NATIVE_FILENAME_TYPES = {
    "photo",
    "photo_document",
    "video",
    "video_note",
    "video_document",
    "gif",
    "voice",
    "sticker",
}


# ─── Filename Generators ──────────────────────────────────────────────────────

def generate_native_filename(media_type: str, message_id: int, ext: str) -> str:
    """
    Generate filename untuk native Telegram media.

    Contoh:
    - photo_123.jpg
    - video_456.mp4
    """
    media_type = safe_filename(media_type.lower())
    ext = ext.lower().lstrip(".")
    return f"{media_type}_{message_id}.{ext}"


def generate_document_filename(filename: str) -> str:
    """
    Bersihkan filename document dari Telegram.
    """
    return safe_filename(filename)


# ─── Main Entry Point ─────────────────────────────────────────────────────────

def get_filename(message, media_type: str, msg_id: int) -> str:
    """
    Generate filename berdasarkan tipe media Telegram.

    Native-like media → auto filename (photo_123.jpg, video_456.mp4)
    Document media    → pakai nama asli dari Telegram
    Fallback          → auto filename dengan ext dari FALLBACK_EXT
    """
    # Native-like media → auto filename
    if media_type in NATIVE_FILENAME_TYPES:
        ext = FALLBACK_EXT.get(media_type, "bin")
        return generate_native_filename(
            media_type=media_type,
            message_id=msg_id,
            ext=ext,
        )

    # Document media → pakai nama asli
    if message.document:
        for attr in message.document.attributes:
            if isinstance(attr, DocumentAttributeFilename):
                return generate_document_filename(attr.file_name)

    # Fallback kalau document tidak punya filename
    ext = FALLBACK_EXT.get(media_type, "bin")
    return generate_native_filename(
        media_type=media_type,
        message_id=msg_id,
        ext=ext,
    )


# ─── Duplicate Handling ───────────────────────────────────────────────────────

def ensure_unique_filename(path: str) -> str:
    """
    Kalau file sudah ada, rename dengan suffix counter.

    file.pdf
    → file_2.pdf
    → file_3.pdf
    """
    if not os.path.exists(path):
        return path

    folder, filename = os.path.split(path)
    name, ext = os.path.splitext(filename)

    counter = 2

    while True:
        new_filename = f"{name}_{counter}{ext}"
        new_path = os.path.join(folder, new_filename)

        if not os.path.exists(new_path):
            return new_path

        counter += 1
