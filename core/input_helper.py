"""
core/input_helper.py
Reusable CLI input helper untuk Teleoder.
Khusus untuk interactive CLI menu, bukan utils umum.
"""

from datetime import datetime


def prompt_choice(prompt: str, choices: dict, default: str = None) -> str:
    """
    Minta input pilihan menu dari user.
    Retry otomatis kalau input tidak valid.

    Parameters
    ----------
    prompt  : str   → teks prompt
    choices : dict  → mapping key → value, contoh {"1": "all", "2": "photo"}
    default : str   → key default kalau user langsung enter (opsional)

    Returns
    -------
    str → value dari choices (bukan key-nya)
    """
    while True:
        raw = input(prompt).strip()

        if not raw and default is not None:
            return choices[default]

        if raw in choices:
            return choices[raw]

        print("[ERROR] Pilihan tidak valid.")


def prompt_int(
    prompt: str,
    allow_empty: bool = False,
    min_value: int = None,
    default: int = None,
) -> int | None:
    """
    Minta input integer dari user.
    Retry otomatis kalau input tidak valid.

    Parameters
    ----------
    prompt      : str   → teks prompt
    allow_empty : bool  → kalau True, enter kosong return None atau default
    min_value   : int   → nilai minimum yang diizinkan (opsional)
    default     : int   → nilai default kalau kosong (opsional)

    Returns
    -------
    int | None → None kalau kosong dan allow_empty=True
    """
    while True:
        raw = input(prompt).strip()

        if not raw:
            if allow_empty:
                return default
            print("[ERROR] Input tidak boleh kosong.")
            continue

        try:
            value = int(raw)
        except ValueError:
            print("[ERROR] Input harus berupa angka.")
            continue

        if min_value is not None and value < min_value:
            print(f"[ERROR] Nilai minimal adalah {min_value}.")
            continue

        return value


def prompt_date(prompt: str, allow_empty: bool = True) -> str | None:
    """
    Minta input tanggal dari user dalam format YYYY-MM-DD.
    Retry otomatis kalau format salah.

    Parameters
    ----------
    prompt      : str   → teks prompt
    allow_empty : bool  → kalau True, enter kosong return None

    Returns
    -------
    str | None → string tanggal "YYYY-MM-DD" atau None kalau kosong
    """
    while True:
        raw = input(prompt).strip()

        if not raw:
            if allow_empty:
                return None
            print("[ERROR] Tanggal tidak boleh kosong.")
            continue

        try:
            datetime.strptime(raw, "%Y-%m-%d")
            return raw
        except ValueError:
            print("[ERROR] Format tanggal harus YYYY-MM-DD.")


def prompt_channel(prompt: str) -> str:
    """
    Minta input channel dari user.
    Retry otomatis kalau kosong.

    Parameters
    ----------
    prompt : str → teks prompt

    Returns
    -------
    str → channel string yang sudah di-strip
    """
    while True:
        raw = input(prompt).strip()

        if not raw:
            print("[ERROR] Channel tidak boleh kosong.")
            continue

        return raw