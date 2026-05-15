"""
core/filters.py
Media filter logic untuk Telegram downloader.

Tanggung jawab:
- Definisi filter yang valid
- Deteksi tipe media dari message Telegram
- Archive detection
- Filter matching
"""

import os
from typing import Optional

from telethon.tl.types import (
    DocumentAttributeAnimated,
    DocumentAttributeAudio,
    DocumentAttributeFilename,
    DocumentAttributeSticker,
    DocumentAttributeVideo,
)


# ─── Konstanta ────────────────────────────────────────────────────────────────

VALID_FILTERS = {
    "all",
    "photo",
    "photo_document",
    "video",
    "video_note",
    "video_document",
    "gif",
    "audio",
    "voice",
    "archive",
    "sticker",
    "document",
}

# Ekstensi archive yang dikenali
ARCHIVE_EXTENSIONS = {".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz"}
ARCHIVE_MIME_TYPES = {
    "application/x-rar-compressed",
    "application/x-7z-compressed",
    "application/x-bzip2",
    "application/x-tar",
    "application/x-rar",
    "application/gzip",
    "application/zip",
}


# ─── Archive Detection ────────────────────────────────────────────────────────

def is_archive(filename: str, mime: str) -> bool:
    """Cek apakah file termasuk archive berdasarkan ekstensi atau mime type."""
    ext = os.path.splitext(filename)[1].lower()
    return ext in ARCHIVE_EXTENSIONS or mime in ARCHIVE_MIME_TYPES


# ─── Media Type Detection ─────────────────────────────────────────────────────

def get_media_type(message) -> Optional[str]:
    """
    Kembalikan tipe media dari message, atau None kalau bukan media.

    Urutan prioritas detection:
    1. photo
    2. video_note
    3. gif
    4. video
    5. audio
    6. voice
    7. sticker
    8. photo_document
    9. video_document
    10. archive
    11. document
    """
    # 1. Photo (dikirim sebagai foto biasa)
    if message.photo and not message.document:
        return "photo"

    if message.document:
        attrs = message.document.attributes
        mime = message.document.mime_type or ""

        attr_types = {type(a) for a in attrs}

        # 2. Round video (video_note)
        for attr in attrs:
            if isinstance(attr, DocumentAttributeVideo) and attr.round_message:
                return "video_note"

        # 3. GIF (animated document)
        if DocumentAttributeAnimated in attr_types:
            return "gif"

        # 4. Video biasa Telegram
        if (
            DocumentAttributeVideo in attr_types
            and DocumentAttributeFilename in attr_types
        ):
            return "video"

        # 5-6. Audio / Voice
        for attr in attrs:
            if isinstance(attr, DocumentAttributeAudio):
                return "voice" if attr.voice else "audio"

        # 7. Sticker
        if DocumentAttributeSticker in attr_types:
            return "sticker"

        # 8. Photo as document
        if mime.startswith("image/"):
            return "photo_document"

        # 9. Video as document/file
        if mime.startswith("video/"):
            return "video_document"

        # Ambil filename untuk cek archive
        filename = ""
        for attr in attrs:
            if isinstance(attr, DocumentAttributeFilename):
                filename = attr.file_name
                break

        # 10. Archive
        if is_archive(filename, mime):
            return "archive"

        # 11. Fallback document
        return "document"

    return None


# ─── Filter Matching ──────────────────────────────────────────────────────────

def passes_filter(media_type: Optional[str], filter_type: str) -> bool:
    """Cek apakah media lolos filter."""
    if media_type is None:
        return False
    if filter_type == "all":
        return True
    return media_type == filter_type
