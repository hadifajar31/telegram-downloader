"""
cli/cli.py
CLI wrapper untuk Teleoder.
"""

import argparse
import sys
import time

from core.downloader import run_downloader, DownloadCallbacks, VALID_FILTERS


# ─── Callbacks untuk CLI ──────────────────────────────────────────────────────

def _make_cli_callbacks() -> DownloadCallbacks:
    """Buat callbacks yang print output ke terminal."""

    def on_progress(percent: float, speed: str, eta: str):
        # Print di baris yang sama, timpa terus
        print(f"\r  Progress: {percent:5.1f}%  |  {speed}  |  ETA: {eta}   ", end="", flush=True)

    def on_file(current: int, total: int, filename: str):
        # Newline dulu biar tidak menimpa progress bar sebelumnya
        print()
        print(f"[{current}/{total}] {filename}")

    def on_error(message: str):
        print(file=sys.stderr)
        print(f"[ERROR] {message}", file=sys.stderr)

    def on_summary(message: str):
        print()
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
        "channel",
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
    }

    limit_display = config["limit"] if config["limit"] is not None else "all"

    print(f"Channel : {config['channel']}")
    print(f"Filter  : {config['filter']}")
    print(f"Limit   : {limit_display}")
    print("Memulai download...\n")

    callbacks = _make_cli_callbacks()

    try:
        run_downloader(config, callbacks)
    except ValueError as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        return
    except KeyboardInterrupt:
        print("\n\nSTOPPED oleh user.")
        time.sleep(0.5)
        return