"""
core/utils.py
Helper functions untuk Teleoder.
"""

import os
import re


# ─── Channel Parsing ──────────────────────────────────────────────────────────

def parse_channel(channel_input: str) -> str:
    """
    Terima input channel dalam berbagai format, kembalikan identifier bersih.

    Format yang didukung:
    - https://t.me/channelname
    - t.me/channelname
    - https://t.me/c/1234567890        → -1001234567890
    - https://t.me/c/1234567890/42     → -1001234567890  (nomor pesan diabaikan)
    - @channelname
    - channelname
    - -100xxxxxxxxxx (numeric ID)
    """
    channel_input = channel_input.strip()

    # Numeric ID (positif atau negatif)
    if re.match(r'^-?\d+$', channel_input):
        return channel_input

    # URL t.me/c/... → private channel numeric ID
    match = re.match(r'^(?:https?://)?t\.me/c/(\d+)', channel_input)
    if match:
        return f"-100{match.group(1)}"

    # URL t.me/username
    match = re.match(r'^(?:https?://)?t\.me/([a-zA-Z0-9_]+)', channel_input)
    if match:
        return match.group(1)

    # @username
    if channel_input.startswith('@'):
        return channel_input[1:]

    # Bare username
    return channel_input


# ─── Filename ─────────────────────────────────────────────────────────────────

def safe_filename(filename: str, max_length: int = 200) -> str:
    """
    Bersihkan filename dari karakter yang tidak aman untuk filesystem.
    """
    if not filename:
        return "unnamed_file"

    # Hapus karakter ilegal
    filename = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '_', filename)

    # Trim spasi dan titik di awal/akhir
    filename = filename.strip('. ')

    # Pastikan tidak kosong setelah cleaning
    if not filename:
        return "unnamed_file"

    # Potong kalau terlalu panjang, jaga ekstensi
    if len(filename) > max_length:
        name, ext = os.path.splitext(filename)
        ext = ext[:10]  # ekstensi max 10 char
        name = name[: max_length - len(ext)]
        filename = name + ext

    return filename


# ─── Formatting ───────────────────────────────────────────────────────────────

def format_size(size_bytes: int) -> str:
    """
    Konversi bytes ke string yang mudah dibaca.
    Contoh: 1048576 → "1.00 MB"
    """
    if size_bytes < 0:
        return "0 B"

    units = ["B", "KB", "MB", "GB", "TB"]
    size = float(size_bytes)
    unit_index = 0

    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1

    if unit_index == 0:
        return f"{int(size)} B"

    return f"{size:.2f} {units[unit_index]}"


def format_eta(seconds: float) -> str:
    """
    Konversi detik ke string ETA yang mudah dibaca.
    Contoh: 3661 → "1j 1m 1s"
    """
    if seconds < 0 or seconds != seconds:  # negatif atau NaN
        return "--:--"

    seconds = int(seconds)

    if seconds < 60:
        return f"{seconds}s"

    minutes, secs = divmod(seconds, 60)

    if minutes < 60:
        return f"{minutes}m {secs}s"

    hours, mins = divmod(minutes, 60)

    if hours < 24:
        return f"{hours}j {mins}m"

    days, hrs = divmod(hours, 24)
    return f"{days}d {hrs}j"

# ─── Filesystem  ──────────────────────────────────────────────────────────────

def ensure_folder(path: str):
    """Pastikan folder ada."""
    os.makedirs(path, exist_ok=True)

# ─── Path Builder ─────────────────────────────────────────────────────────────

def get_channel_folder_name(entity) -> str:
    """
    Ambil nama folder channel yang aman untuk filesystem.

    Prioritas:
    1. title
    2. username
    3. ID
    """
    if getattr(entity, "title", None):
        return safe_filename(entity.title)

    if getattr(entity, "username", None):
        return safe_filename(entity.username)

    return str(entity.id)


def build_output_path(
    base_dir: str,
    channel_name: str,
    media_type: str,
    filename: str,
    grouped_id: int | None = None,
) -> str:
    """
    Build path output:
    - normal:
      base/channel/media_type/filename

    - grouped media:
      base/channel/media_type/album_<grouped_id>/filename
    """
    channel_folder = safe_filename(channel_name)
    media_folder = safe_filename(media_type.lower())

    path_parts = [
        base_dir,
        channel_folder,
        media_folder,
    ]

    # Album/grouped media
    if grouped_id is not None:
        path_parts.append(f"album_{grouped_id}")

    folder_path = os.path.join(*path_parts)

    ensure_folder(folder_path)

    return os.path.join(folder_path, filename)

# ─── Filename Builder ─────────────────────────────────────────────────────────

def generate_native_filename(
    media_type: str,
    message_id: int,
    ext: str,
) -> str:
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


def ensure_unique_filename(path: str) -> str:
    """
    Kalau file sudah ada:
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