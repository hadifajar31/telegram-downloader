"""
core/downloader.py
Logic utama download media dari Telegram.
"""

import os
import time
import threading
from typing import Callable, Optional

from telethon.sync import TelegramClient
from telethon import errors
from telethon.tl.types import (
    MessageMediaPhoto,
    MessageMediaDocument,
    DocumentAttributeFilename,
)

from config.config import API_ID, API_HASH, PHONE_NUMBER, SESSION_PATH, OUTPUT_DIR
from core.utils import parse_channel, safe_filename, format_size, format_eta


# ─── Tipe Filter ──────────────────────────────────────────────────────────────

VALID_FILTERS = {"all", "photo", "video", "document"}


# ─── Callbacks ────────────────────────────────────────────────────────────────

class DownloadCallbacks:
    """
    Kumpulan callback untuk melaporkan status download.

    Semua callback opsional. Kalau tidak di-set, diabaikan saja.
    """

    def __init__(
        self,
        on_progress: Optional[Callable[[float, str, str], None]] = None,
        on_file: Optional[Callable[[int, int, str], None]] = None,
        on_done: Optional[Callable[[], None]] = None,
        on_error: Optional[Callable[[str], None]] = None,
    ):
        """
        Parameters
        ----------
        on_progress(percent, speed, eta)
            percent : float  → 0.0 - 100.0
            speed   : str    → contoh "1.23 MB/s"
            eta     : str    → contoh "2m 30d"

        on_file(current, total, filename)
            current  : int   → nomor file sekarang
            total    : int   → total file
            filename : str   → nama file

        on_done()
            Dipanggil setelah semua file selesai didownload.

        on_error(message)
            message : str    → pesan error
        """
        self.on_progress = on_progress
        self.on_file = on_file
        self.on_done = on_done
        self.on_error = on_error

    def progress(self, percent: float, speed: str, eta: str):
        if self.on_progress:
            self.on_progress(percent, speed, eta)

    def file(self, current: int, total: int, filename: str):
        if self.on_file:
            self.on_file(current, total, filename)

    def done(self):
        if self.on_done:
            self.on_done()

    def error(self, message: str):
        if self.on_error:
            self.on_error(message)


# ─── Helper Internal ──────────────────────────────────────────────────────────

def _get_media_type(message) -> Optional[str]:
    """Kembalikan tipe media dari message, atau None kalau bukan media."""
    if message.photo:
        return "photo"

    if message.document:
        mime = message.document.mime_type or ""
        if mime.startswith("video/"):
            return "video"
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
    ext_map = {
        "photo": "jpg",
        "video": "mp4",
        "document": "bin",
    }
    ext = ext_map.get(media_type, "bin")
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
            channel     : str   → channel ID / username
            filter      : str   → "all" | "photo" | "video" | "document"

        callbacks : DownloadCallbacks
        """
        self.channel = parse_channel(config.get("channel", ""))
        self.filter = config.get("filter", "all")
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
        os.makedirs(OUTPUT_DIR, exist_ok=True)

        client = TelegramClient(SESSION_PATH, API_ID, API_HASH)
        try:
            client.connect()

            if not client.is_user_authorized():
                self.callbacks.error("Belum login. Jalankan 'python login.py' terlebih dahulu.")
                client.disconnect()
                return
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
        """Ambil semua pesan dan download media yang lolos filter."""
        # Resolve entity dulu, penting untuk private channel
        # Telethon butuh integer untuk numeric ID, bukan string
        channel_ref = int(self.channel) if self.channel.lstrip('-').isdigit() else self.channel
        entity = client.get_entity(channel_ref)

        # Kumpulkan dulu semua message yang akan didownload
        messages_to_download = []

        for message in client.iter_messages(entity):
            if self._stop_event.is_set():
                return

            media_type = _get_media_type(message)
            if not _passes_filter(media_type, self.filter):
                continue

            messages_to_download.append((message, media_type))

        total = len(messages_to_download)

        if total == 0:
            self.callbacks.error("Tidak ada media yang cocok dengan filter.")
            return

        for idx, (message, media_type) in enumerate(messages_to_download, start=1):
            if self._stop_event.is_set():
                break

            filename = _get_filename(message, media_type, message.id)

            output_path = os.path.join(OUTPUT_DIR, filename)

            # Skip kalau sudah ada
            if os.path.exists(output_path):
                self.callbacks.file(idx, total, f"[SKIP] {filename}")
                continue

            self.callbacks.file(idx, total, filename)

            self._download_single(client, message, output_path)

        if not self._stop_event.is_set():
            self.callbacks.done()

    def _download_single(self, client: TelegramClient, message, output_path: str):
        """Download satu file dengan progress callback."""
        start_time = time.time()
        last_bytes = 0
        last_time = start_time

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

        # Download
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
    callbacks : DownloadCallbacks
    """
    downloader = Downloader(config, callbacks)
    downloader.run()