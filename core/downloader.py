"""
core/downloader.py
Logic utama download media dari Telegram.
"""

import os
import json
import time
import threading
from typing import Callable, Optional, Union

from telethon.sync import TelegramClient
from telethon import errors
from telethon.tl.types import (
    DocumentAttributeAnimated,
    DocumentAttributeAudio,
    DocumentAttributeFilename,
    DocumentAttributeSticker,
    DocumentAttributeVideo,
)

from config.config import API_ID, API_HASH, PHONE_NUMBER, SESSION_PATH, OUTPUT_DIR
from core.utils import parse_channel, safe_filename, format_size, format_eta


# ─── Tipe Filter ──────────────────────────────────────────────────────────────

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


# ─── Resume ───────────────────────────────────────────────────────────────────

RESUME_PATH = "data/resume.json"


def load_resume() -> dict:
    if not os.path.exists(RESUME_PATH):
        return {}
    try:
        with open(RESUME_PATH, "r") as f:
            return json.load(f)
    except Exception:
        return {}


def save_resume(data: dict):
    os.makedirs("data", exist_ok=True)
    with open(RESUME_PATH, "w") as f:
        json.dump(data, f, indent=2)


# ─── Callbacks ────────────────────────────────────────────────────────────────

class DownloadCallbacks:
    """
    Kumpulan callback untuk melaporkan status download.

    Semua callback opsional. Kalau tidak di-set, diabaikan saja.
    """

    def __init__(
        self,
        on_progress: Optional[Callable[[float, str, str], None]] = None,
        on_file: Optional[Callable[[int, Union[int, str], str], None]] = None,
        on_done: Optional[Callable[[], None]] = None,
        on_error: Optional[Callable[[str], None]] = None,
    ):
        """
        Parameters
        ----------
        on_progress(percent, speed, eta)
            percent : float       → 0.0 - 100.0
            speed   : str         → contoh "1.23 MB/s"
            eta     : str         → contoh "2m 30s"

        on_file(current, total, filename)
            current  : int        → nomor file sekarang
            total    : int | str  → total file, atau "?" kalau tidak diketahui
            filename : str        → nama file

        on_done()
            Dipanggil setelah semua file selesai didownload.

        on_error(message)
            message : str         → pesan error
        """
        self.on_progress = on_progress
        self.on_file = on_file
        self.on_done = on_done
        self.on_error = on_error

    def progress(self, percent: float, speed: str, eta: str):
        if self.on_progress:
            self.on_progress(percent, speed, eta)

    def file(self, current: int, total: Union[int, str], filename: str):
        if self.on_file:
            self.on_file(current, total, filename)

    def done(self):
        if self.on_done:
            self.on_done()

    def error(self, message: str):
        if self.on_error:
            self.on_error(message)


# ─── Helper Internal ──────────────────────────────────────────────────────────

def _is_archive(filename: str, mime: str) -> bool:
    """Cek apakah file termasuk archive berdasarkan ekstensi atau mime type."""
    ext = os.path.splitext(filename)[1].lower()
    return ext in ARCHIVE_EXTENSIONS or mime in ARCHIVE_MIME_TYPES


def _get_media_type(message) -> Optional[str]:
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

        # Kumpulkan atribut yang ada
        attr_types = {type(a) for a in attrs}

        # Cek round video (video_note)
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

        # 8. Photo as document (gambar dikirim sebagai file)
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
        if _is_archive(filename, mime):
            return "archive"

        # 11. Fallback document
        return "document"

    return None


def _get_filename(message, media_type: str, msg_id: int) -> str:
    """Buat filename yang aman dari message."""
    # Coba ambil nama asli dari atribut dokumen
    if message.document:
        for attr in message.document.attributes:
            if isinstance(attr, DocumentAttributeFilename):
                return safe_filename(attr.file_name)

    # Fallback: buat nama dari ID dan tipe
    ext = FALLBACK_EXT.get(media_type, "bin")
    return f"media_{msg_id}.{ext}"


def _passes_filter(media_type: Optional[str], filter_type: str) -> bool:
    """Cek apakah media lolos filter."""
    if media_type is None:
        return False
    if filter_type == "all":
        return True
    return media_type == filter_type


# ─── Core Downloader ──────────────────────────────────────────────────────────

class Downloader:
    """
    Downloader utama. Jalankan via run() atau run_in_thread().
    """

    def __init__(self, config: dict, callbacks: DownloadCallbacks):
        """
        Parameters
        ----------
        config : dict
            channel : str   → channel ID / username
            filter  : str   → salah satu dari VALID_FILTERS
            limit   : int   → jumlah file, None = semua

        callbacks : DownloadCallbacks
        """
        self.channel = parse_channel(config.get("channel", ""))
        self.filter = config.get("filter", "all")
        self.limit = config.get("limit", None)
        self.callbacks = callbacks
        self._stop_event = threading.Event()

        if self.filter not in VALID_FILTERS:
            raise ValueError(f"Filter tidak valid: '{self.filter}'. Pilih dari: {VALID_FILTERS}")

        if not self.channel:
            raise ValueError("Channel tidak boleh kosong.")

    def stop(self):
        """Minta downloader berhenti setelah file saat ini selesai."""
        self._stop_event.set()

    def run(self):
        """Jalankan proses download secara synchronous."""
        self._stop_event.clear()
        os.makedirs(OUTPUT_DIR, exist_ok=True)

        try:
            with TelegramClient(SESSION_PATH, API_ID, API_HASH) as client:
                client.start(phone=PHONE_NUMBER)
                self._download_all(client)

        except errors.FloodWaitError as e:
            self.callbacks.error(f"Flood wait: harus tunggu {e.seconds} detik.")
        except errors.ChannelPrivateError:
            self.callbacks.error("Channel private atau tidak ditemukan.")
        except errors.UsernameNotOccupiedError:
            self.callbacks.error(f"Username '{self.channel}' tidak ditemukan.")
        except ConnectionError as e:
            self.callbacks.error(f"Koneksi gagal: {e}")
        except Exception as e:
            self.callbacks.error(f"Error tidak terduga: {e}")

    def run_in_thread(self) -> threading.Thread:
        """Jalankan download di background thread. Kembalikan thread-nya."""
        t = threading.Thread(target=self.run, daemon=True)
        t.start()
        return t

    def _download_all(self, client: TelegramClient):
        """Stream pesan dan download langsung per file."""
        # Resolve entity, penting untuk private channel
        channel_ref = int(self.channel) if self.channel.lstrip('-').isdigit() else self.channel
        entity = client.get_entity(channel_ref)

        # Resume
        resume_data = load_resume()
        channel_key = str(self.channel)
        last_id = resume_data.get(channel_key, 0)

        if last_id > 0:
            print(f"Melanjutkan dari last_id: {last_id}")

        # Total untuk callback: pakai limit kalau ada, "?" kalau tidak
        total: Union[int, str] = "?"

        downloaded_count = 0  # untuk logic limit
        display_count = 0     # untuk UI (nomor file)

        for message in client.iter_messages(entity, min_id=last_id, reverse=True):
            if self._stop_event.is_set():
                return

            media_type = _get_media_type(message)
            if not _passes_filter(media_type, self.filter):
                continue

            filename = _get_filename(message, media_type, message.id)
            output_path = os.path.join(OUTPUT_DIR, filename)

            # Naik sekali di awal loop
            display_count += 1

            # Skip file yang sudah ada
            if os.path.exists(output_path):
                self.callbacks.file(display_count, total, f"(SKIP) {filename}")
                self.callbacks.progress(100.0, "SKIP", "-")
                resume_data[channel_key] = message.id
                save_resume(resume_data)
                continue

            # Download
            self.callbacks.file(display_count, total, filename)

            download_success = False

            while True:
                try:
                    self._download_single(client, message, output_path)
                    downloaded_count += 1
                    download_success = True
                    break
                except errors.FloodWaitError as e:
                    wait_time = e.seconds
                    self.callbacks.error(f"[RETRY] FloodWait {wait_time}s")
                    time.sleep(wait_time)
                except Exception as e:
                    self.callbacks.error(f"Gagal download {filename}: {e}")
                    break

            if download_success:
                resume_data[channel_key] = message.id
                save_resume(resume_data)

            # Early stop kalau limit tercapai
            if self.limit is not None and downloaded_count >= self.limit:
                break

        if not self._stop_event.is_set():
            if self.limit is not None:
                if downloaded_count >= self.limit:
                    print("\n\n" + f"✔ Download selesai ({downloaded_count}/{self.limit} file berhasil)")
                else:
                    print("\n\n" + f"⚠ Download selesai ({downloaded_count}/{self.limit} file ditemukan)")
            else:
                skip_count = display_count - downloaded_count
                print("\n\n" + f"ℹ Selesai! {display_count} file diproses ({downloaded_count} download, {skip_count} skip)")

    def _download_single(self, client: TelegramClient, message, output_path: str):
        """Download satu file dengan progress callback."""
        last_bytes = 0
        last_time = time.time()

        def progress_callback(received: int, total: int):
            nonlocal last_bytes, last_time

            now = time.time()
            elapsed = now - last_time

            # Update speed tiap 0.5 detik
            if elapsed >= 0.5:
                delta_bytes = received - last_bytes
                speed_bps = delta_bytes / elapsed if elapsed > 0 else 0
                speed_str = f"{format_size(int(speed_bps))}/s"

                remaining_bytes = total - received
                eta_seconds = remaining_bytes / speed_bps if speed_bps > 0 else 0
                eta_str = format_eta(eta_seconds)

                last_bytes = received
                last_time = now
            else:
                speed_str = "..."
                eta_str = "..."

            percent = (received / total * 100) if total > 0 else 0
            self.callbacks.progress(percent, speed_str, eta_str)

        client.download_media(
            message,
            file=output_path,
            progress_callback=progress_callback,
        )


# ─── Entry Point ──────────────────────────────────────────────────────────────

def run_downloader(config: dict, callbacks: DownloadCallbacks):
    """
    Shortcut untuk buat Downloader dan langsung jalankan.

    Parameters
    ----------
    config : dict
        channel : str
        filter  : str
        limit   : int | None
    callbacks : DownloadCallbacks
    """
    downloader = Downloader(config, callbacks)
    downloader.run()