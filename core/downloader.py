"""
core/downloader.py
Logic utama download media dari Telegram.
"""

import os
import asyncio
import time
import threading
from typing import Callable, Optional, Union
from datetime import datetime

from telethon.sync import TelegramClient
from telethon import errors

from config.config import API_ID, API_HASH, PHONE_NUMBER, SESSION_PATH, OUTPUT_DIR
from core.compare import CompareIndex
from core.resume import ResumeManager
from core.filters import (
    VALID_FILTERS,
    get_media_type,
    passes_filter,
)
from core.naming import (
    NATIVE_FILENAME_TYPES,
    get_filename,
    ensure_unique_filename,
)
from core.utils import (
    parse_channel,
    format_size,
    format_eta,
    build_output_path,
    get_channel_folder_name,
)


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
        on_error: Optional[Callable[[str], None]] = None,
        on_summary: Optional[Callable[[str], None]] = None,
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

        on_error(message)
            message : str         → pesan error

        on_summary(message)
            message : str         → pesan ringkasan
        """
        self.on_progress = on_progress
        self.on_file = on_file
        self.on_error = on_error
        self.on_summary = on_summary

    def progress(self, percent: float, speed: str, eta: str):
        if self.on_progress:
            self.on_progress(percent, speed, eta)

    def file(self, current: int, total: Union[int, str], filename: str):
        if self.on_file:
            self.on_file(current, total, filename)

    def error(self, message: str):
        if self.on_error:
            self.on_error(message)

    def summary(self, message: str):
        if self.on_summary:
            self.on_summary(message)


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
        raw_channel = str(config.get("channel", "")).strip()

        self.channel = parse_channel(raw_channel)
        self.filter = config.get("filter", "all")
        self.limit = config.get("limit", None)
        self.min_id = config.get("min_id", 0)
        self.max_id = config.get("max_id", 0)
        self.from_date = config.get("from_date")
        self.to_date = config.get("to_date")
        self.callbacks = callbacks
        self._stop_event = threading.Event()

        if self.filter not in VALID_FILTERS:
            raise ValueError(f"Filter tidak valid: '{self.filter}'. Pilih dari: {VALID_FILTERS}")

        if not raw_channel:
            raise ValueError("Channel tidak boleh kosong.")

        if self.limit is not None and self.limit <= 0:
            raise ValueError("Limit harus lebih dari 0 atau None untuk semua.")

        if self.min_id < 0:
            raise ValueError("min_id tidak boleh negatif.")

        if self.max_id < 0:
            raise ValueError("max_id tidak boleh negatif.")

        if self.max_id and self.max_id <= self.min_id:
            raise ValueError("max_id harus lebih besar dari min_id.")

        try:
            if self.from_date:
                self.from_date = datetime.strptime(self.from_date, "%Y-%m-%d")

            if self.to_date:
                self.to_date = datetime.strptime(self.to_date, "%Y-%m-%d")

        except ValueError:
            raise ValueError("Format tanggal harus YYYY-MM-DD.")

        if self.from_date and self.to_date and self.to_date < self.from_date:
            raise ValueError("to_date harus lebih besar dari from_date.")

    def stop(self):
        """Minta downloader berhenti setelah file saat ini selesai."""
        self._stop_event.set()

    def run(self):
        """Jalankan proses download secara synchronous."""
        # Fix: pastikan event loop baru di thread non-main
        # Tanpa ini, Telethon bisa raise "no current event loop" di background thread
        asyncio.set_event_loop(asyncio.new_event_loop())

        self._stop_event.clear()
        os.makedirs(OUTPUT_DIR, exist_ok=True)

        client = None

        try:
            client = TelegramClient(SESSION_PATH, API_ID, API_HASH)
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

        finally:
            if client:
                try:
                    client.disconnect()
                except Exception as e:
                    self.callbacks.error(f"Error saat disconnect: {e}")

    def run_in_thread(self) -> threading.Thread:
        """Jalankan download di background thread. Kembalikan thread-nya."""
        t = threading.Thread(target=self.run, daemon=True)
        t.start()
        return t

    def _download_all(self, client: TelegramClient):
        """Stream pesan dan download langsung per file."""
        channel_ref = int(self.channel) if self.channel.lstrip('-').isdigit() else self.channel
        entity = client.get_entity(channel_ref)
        channel_folder = get_channel_folder_name(entity)

        channel_base = os.path.join(OUTPUT_DIR, channel_folder)
        compare_index = CompareIndex(channel_base)
        compare_index.build()

        total_messages = client.get_messages(entity, limit=1).total
        print(f"Total   : {total_messages} messages")

        is_explicit_range = (
            self.min_id > 0
            or self.max_id > 0
            or self.from_date
            or self.to_date
        )

        resume = ResumeManager(str(self.channel))

        if not is_explicit_range and resume.last_id > 0:
            print(f"Resume  : last_id {resume.last_id}")

        total: Union[int, str] = "?"

        downloaded_count = 0
        display_count = 0

        effective_min_id = self.min_id if is_explicit_range else max(resume.last_id, self.min_id)

        # Pre-scan: hitung jumlah media valid per grouped_id
        # Biar album folder hanya dibuat kalau isinya >1 file
        grouped_counts: dict[int, int] = {}
        for msg in client.iter_messages(
            entity,
            min_id=effective_min_id,
            max_id=self.max_id if self.max_id > 0 else None,
            reverse=True
        ):
            if msg.grouped_id is None:
                continue

            msg_date = msg.date.replace(tzinfo=None)
            if self.from_date and msg_date < self.from_date:
                continue
            if self.to_date and msg_date > self.to_date:
                continue

            mt = get_media_type(msg)
            if not passes_filter(mt, self.filter):
                continue

            grouped_counts[msg.grouped_id] = grouped_counts.get(msg.grouped_id, 0) + 1

        for message in client.iter_messages(
            entity,
            min_id=effective_min_id,
            max_id=self.max_id if self.max_id > 0 else None,
            reverse=True
        ):
            if self._stop_event.is_set():
                if not is_explicit_range:
                    resume.flush()
                return

            message_date = message.date.replace(tzinfo=None)

            if self.from_date and message_date < self.from_date:
                continue

            if self.to_date and message_date > self.to_date:
                continue

            media_type = get_media_type(message)

            if not passes_filter(media_type, self.filter):
                continue

            filename = get_filename(message, media_type, message.id)
            output_path = build_output_path(
                OUTPUT_DIR,
                channel_folder,
                media_type, filename,
                grouped_id=message.grouped_id,
                grouped_count=grouped_counts.get(message.grouped_id, 0) if message.grouped_id else 0,
            )

            display_count += 1

            # Native-like media → skip kalau sudah ada
            if media_type in NATIVE_FILENAME_TYPES:
                if compare_index.exists(output_path):
                    self.callbacks.file(display_count, total, f"(SKIP) {filename}")
                    self.callbacks.progress(100.0, "SKIP", "-")

                    if not is_explicit_range:
                        resume.update(message.id)

                    continue

            # Document-like media → rename kalau sudah ada
            else:
                output_path = ensure_unique_filename(output_path)
                filename = os.path.basename(output_path)

            self.callbacks.file(display_count, total, filename)

            download_success = False

            while True:
                try:
                    self._download_single(client, message, output_path)
                    downloaded_count += 1
                    download_success = True
                    compare_index.add(output_path)
                    break
                except errors.FloodWaitError as e:
                    wait_time = e.seconds
                    self.callbacks.error(f"[RETRY] FloodWait {wait_time}s")
                    time.sleep(wait_time)
                except Exception as e:
                    self.callbacks.error(f"Gagal download {filename}: {e}")
                    break

            if download_success and not is_explicit_range:
                resume.update(message.id)

            if self.limit is not None and downloaded_count >= self.limit:
                break

        if not self._stop_event.is_set():
            if not is_explicit_range:
                resume.flush()

            if self.limit is not None:
                if downloaded_count >= self.limit:
                    self.callbacks.summary(
                        f"✔ Download selesai ({downloaded_count}/{self.limit} file berhasil)"
                    )
                else:
                    self.callbacks.summary(
                        f"⚠ Download selesai ({downloaded_count}/{self.limit} file ditemukan)"
                    )
            else:
                skip_count = display_count - downloaded_count
                self.callbacks.summary(
                    f"ℹ Selesai! {display_count} file diproses "
                    f"({downloaded_count} download, {skip_count} skip)"
                )

    def _download_single(self, client: TelegramClient, message, output_path: str):
        """Download satu file dengan progress callback."""
        last_bytes = 0
        last_time = time.time()
        start_time = last_time

        # Cache last valid stats — biar tidak tampil "..." terus
        last_speed_str = "..."
        last_eta_str = "..."

        def progress_callback(received: int, total: int):
            nonlocal last_bytes, last_time, last_speed_str, last_eta_str

            if self._stop_event.is_set():
                return

            now = time.time()
            elapsed = now - last_time
            percent = (received / total * 100) if total > 0 else 0

            # Force final update saat download selesai
            if received == total:
                total_elapsed = now - start_time
                if total_elapsed > 0:
                    last_speed_str = f"{format_size(int(total / total_elapsed))}/s"
                last_eta_str = "0s"
                self.callbacks.progress(100.0, last_speed_str, last_eta_str)
                return

            if elapsed >= 0.5:
                delta_bytes = received - last_bytes
                speed_bps = delta_bytes / elapsed if elapsed > 0 else 0
                last_speed_str = f"{format_size(int(speed_bps))}/s"

                remaining_bytes = total - received
                eta_seconds = remaining_bytes / speed_bps if speed_bps > 0 else 0
                last_eta_str = format_eta(eta_seconds)

                last_bytes = received
                last_time = now

            # Pakai cache kalau belum waktunya update
            self.callbacks.progress(percent, last_speed_str, last_eta_str)

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