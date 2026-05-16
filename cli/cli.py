"""
cli/cli.py
CLI wrapper untuk Teleoder.
"""

import argparse
import sys

from core.downloader import Downloader, DownloadCallbacks, VALID_FILTERS


# ─── Callbacks untuk CLI ──────────────────────────────────────────────────────

def _clear_progress_line(stream=sys.stdout):
    """Hapus progress line aktif di terminal."""
    print(
        "\r" + " " * 120 + "\r",
        end="",
        flush=True,
        file=stream,
    )


def _make_cli_callbacks() -> DownloadCallbacks:
    """Buat callbacks yang print output ke terminal."""

    def on_progress(percent: float, speed: str, eta: str):
        # Print di baris yang sama, timpa terus
        print(f"\r  Progress: {percent:5.1f}%  |  {speed}  |  ETA: {eta}   ", end="", flush=True)

    def on_file(current: int, total: int, filename: str):
        # Bersihkan progress line sebelum print nama file baru
        _clear_progress_line()
        print(f"[{current}/{total}] {filename}")

    def on_error(message: str):
        # Bersihkan progress line sebelum print error
        _clear_progress_line(sys.stderr)
        print(f"[ERROR] {message}", file=sys.stderr)

    def on_summary(message: str):
        # Bersihkan progress line sebelum print summary
        _clear_progress_line()
        print(message)

    return DownloadCallbacks(
        on_progress=on_progress,
        on_file=on_file,
        on_error=on_error,
        on_summary=on_summary,
    )


# ─── Argument Parser ──────────────────────────────────────────────────────────

def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="teleoder",
        description="Download media dari channel Telegram.",
    )

    parser.add_argument(
        "--channel",
        "-c",
        required=True,
        help="Channel ID, username, atau link. Contoh: @mychannel / https://t.me/mychannel",
    )

    parser.add_argument(
        "--filter",
        "-f",
        choices=sorted(VALID_FILTERS),
        default="all",
        help=(
            "Filter media: "
            "all, photo, photo_document, "
            "video, video_note, video_document, "
            "gif, audio, voice, archive, "
            "sticker, document"
        ),
    )

    parser.add_argument(
        "--limit",
        "-l",
        type=int,
        default=None,
        help="Jumlah file yang didownload. Default: semua",
    )

    parser.add_argument(
        "--min-id",
        type=int,
        default=0,
        help="Download mulai dari message ID tertentu",
    )

    parser.add_argument(
        "--max-id",
        type=int,
        default=0,
        help="Batas maksimal message ID",
    )

    parser.add_argument(
        "--from-date",
        type=str,
        default=None,
        help="Tanggal mulai download (YYYY-MM-DD)",
    )

    parser.add_argument(
        "--to-date",
        type=str,
        default=None,
        help="Tanggal akhir download (YYYY-MM-DD)",
    )

    return parser


# ─── Entry Point CLI ──────────────────────────────────────────────────────────

def main(args=None):
    """
    Entry point CLI. Bisa dipanggil langsung atau dari main.py.

    Parameters
    ----------
    args : list[str] | None
        Kalau None, ambil dari sys.argv. Berguna untuk testing.
    """
    parser = _build_parser()
    parsed = parser.parse_args(args)

    config = {
        "channel": parsed.channel,
        "filter": parsed.filter,
        "limit": parsed.limit,
        "min_id": parsed.min_id,
        "max_id": parsed.max_id,
        "from_date": parsed.from_date,
        "to_date": parsed.to_date,
    }

    callbacks = _make_cli_callbacks()

    try:
        downloader = Downloader(config, callbacks)
    except ValueError as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        return

    limit_display = (
        config["limit"]
        if config["limit"] is not None
        else "all"
    )

    print(f"Channel : {config['channel']}")
    print(f"Filter  : {config['filter']}")
    print(f"Limit   : {limit_display}")
    print(f"Min ID  : {config['min_id'] or '-'}")
    print(f"Max ID  : {config['max_id'] or '-'}")
    print(f"From    : {config['from_date'] or '-'}")
    print(f"To      : {config['to_date'] or '-'}")
    print()
    print("Memulai download...")

    thread = downloader.run_in_thread()

    try:
        while thread.is_alive():
            thread.join(0.2)

    except KeyboardInterrupt:
        _clear_progress_line()
        print("Stopping... menunggu transfer selesai.")
        downloader.stop()

        while thread.is_alive():
            thread.join(0.2)

        _clear_progress_line()
        print("STOPPED.")

if __name__ == "__main__":
    main()