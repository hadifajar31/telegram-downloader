"""
testing/test_hash_scanner.py
Manual test untuk hash scanner system.

Jalankan:
    python -m testing.test_hash_scanner
    atau
    python testing/test_hash_scanner.py
"""

import os
import sys
import tempfile
import shutil

# Pastikan root project ada di path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import time

from core.dedup import HashCache, HashScanner, hash_file, hash_file_safe, is_same_file
from core.dedup.models import CacheEntry, DuplicateGroup, HashEntry
from core.utils import format_size


# ─── Setup ────────────────────────────────────────────────────────────────────

def create_test_folder() -> str:
    """Buat folder temp dengan file test."""
    tmp = tempfile.mkdtemp(prefix="teleoder_test_")

    # File unik
    _write(tmp, "file_a.txt", b"isi file A, unik")
    _write(tmp, "file_b.txt", b"isi file B, unik juga")
    _write(tmp, "file_c.txt", b"isi file C")

    # Duplicate (isi sama persis)
    dup_content = b"ini konten duplikat persis sama"
    _write(tmp, "dup_1.mp4", dup_content)
    _write(tmp, "dup_2.mp4", dup_content)
    _write(tmp, "subfolder/dup_3.mp4", dup_content)

    # Duplicate lain
    dup_img = b"image bytes duplikat"
    _write(tmp, "img_1.jpg", dup_img)
    _write(tmp, "subfolder/img_2.jpg", dup_img)

    return tmp


def _write(base: str, rel_path: str, content: bytes):
    """Tulis file ke folder test."""
    full_path = os.path.join(base, rel_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "wb") as f:
        f.write(content)


# ─── Test Cases ───────────────────────────────────────────────────────────────

def test_hash_file():
    print("\n[TEST] hash_file")

    with tempfile.NamedTemporaryFile(delete=False) as f:
        f.write(b"hello world")
        tmp_path = f.name

    try:
        h = hash_file(tmp_path)
        assert isinstance(h, str), "Hash harus string"
        assert len(h) == 64, "SHA256 hex harus 64 karakter"

        # Konsistensi: hash sama untuk file sama
        h2 = hash_file(tmp_path)
        assert h == h2, "Hash harus konsisten"

        print(f"  ✔ Hash: {h[:16]}...")
        print("  ✔ Konsisten")
    finally:
        os.unlink(tmp_path)


def test_hash_file_different():
    print("\n[TEST] hash berbeda untuk file berbeda")

    with tempfile.NamedTemporaryFile(delete=False) as f:
        f.write(b"konten A")
        path_a = f.name

    with tempfile.NamedTemporaryFile(delete=False) as f:
        f.write(b"konten B")
        path_b = f.name

    try:
        ha = hash_file(path_a)
        hb = hash_file(path_b)
        assert ha != hb, "Hash berbeda untuk isi berbeda"
        print("  ✔ Hash berbeda untuk file berbeda")
    finally:
        os.unlink(path_a)
        os.unlink(path_b)


def test_hash_file_safe_missing():
    print("\n[TEST] hash_file_safe untuk file tidak ada")
    result = hash_file_safe("/path/yang/tidak/ada.mp4")
    assert result is None, "Harus return None kalau file tidak ada"
    print("  ✔ Return None untuk file missing")


def test_is_same_file():
    print("\n[TEST] is_same_file")

    content = b"konten yang sama persis"

    with tempfile.NamedTemporaryFile(delete=False) as f:
        f.write(content)
        path_a = f.name

    with tempfile.NamedTemporaryFile(delete=False) as f:
        f.write(content)
        path_b = f.name

    with tempfile.NamedTemporaryFile(delete=False) as f:
        f.write(b"konten beda")
        path_c = f.name

    try:
        assert is_same_file(path_a, path_b), "File sama harus True"
        assert not is_same_file(path_a, path_c), "File beda harus False"
        print("  ✔ is_same_file bekerja benar")
    finally:
        for p in [path_a, path_b, path_c]:
            os.unlink(p)


def test_scanner_scan():
    print("\n[TEST] HashScanner.scan")

    tmp = create_test_folder()

    try:
        scanner = HashScanner()
        scanner.scan(tmp)

        print(f"  Total file   : {scanner.total_files}")
        print(f"  Total error  : {scanner.total_errors}")
        assert scanner.total_files == 8, f"Harusnya 8 file, dapat {scanner.total_files}"
        assert scanner.total_errors == 0
        print("  ✔ Total file benar")
    finally:
        shutil.rmtree(tmp)


def test_scanner_duplicates():
    print("\n[TEST] HashScanner.get_duplicates")

    tmp = create_test_folder()

    try:
        scanner = HashScanner()
        scanner.scan(tmp)
        dupes = scanner.get_duplicates()

        print(f"  Duplicate groups: {len(dupes)}")
        for g in dupes:
            print(f"    hash={g.hash[:12]}... | {g.count} file | wasted={format_size(g.wasted_bytes)}")
            for entry in g.files:
                print(f"      - {os.path.relpath(entry.path, tmp)}")

        assert len(dupes) == 2, f"Harusnya 2 duplicate groups, dapat {len(dupes)}"
        counts = sorted([g.count for g in dupes], reverse=True)
        assert counts == [3, 2], f"Harusnya [3, 2], dapat {counts}"
        print("  ✔ Duplicate grouping benar")
    finally:
        shutil.rmtree(tmp)


def test_scanner_summary():
    print("\n[TEST] HashScanner.summary")

    tmp = create_test_folder()

    try:
        scanner = HashScanner()
        scanner.scan(tmp)
        s = scanner.summary()

        print(f"  Summary: {s}")
        assert s["total_files"] == 8
        assert s["duplicate_groups"] == 2
        assert s["duplicate_files"] == 5  # 3 + 2
        assert s["wasted_bytes"] > 0
        print("  ✔ Summary benar")
    finally:
        shutil.rmtree(tmp)


def test_scanner_progress_callback():
    print("\n[TEST] progress callback")

    tmp = create_test_folder()
    progress_log = []

    try:
        scanner = HashScanner(on_progress=lambda count, path: progress_log.append(count))
        scanner.scan(tmp)

        assert len(progress_log) == scanner.total_files
        assert progress_log[-1] == scanner.total_files
        print(f"  ✔ Callback dipanggil {len(progress_log)}x")
    finally:
        shutil.rmtree(tmp)


def test_scanner_not_a_directory():
    print("\n[TEST] scan folder tidak ada")

    scanner = HashScanner()
    try:
        scanner.scan("/path/tidak/ada")
        assert False, "Harusnya raise NotADirectoryError"
    except NotADirectoryError:
        print("  ✔ Raise NotADirectoryError dengan benar")


def test_scanner_cache_hit():
    print("\n[TEST] cache hit pada repeated scan")

    tmp = create_test_folder()

    try:
        cache = HashCache()
        scanner = HashScanner(cache=cache)

        # Scan pertama: semua miss, cache kosong
        scanner.scan(tmp)

        assert scanner.cache_hits == 0, f"Scan pertama harus 0 hits, dapat {scanner.cache_hits}"
        assert scanner.cache_misses == 8, f"Scan pertama harus 8 misses, dapat {scanner.cache_misses}"
        assert cache.size == 8, f"Cache harus isi 8 entry, dapat {cache.size}"

        print(f"  Scan 1 → hits={scanner.cache_hits}, misses={scanner.cache_misses}")

        # Scan kedua: semua hit, file tidak berubah
        scanner.scan(tmp)

        assert scanner.cache_hits == 8, f"Scan kedua harus 8 hits, dapat {scanner.cache_hits}"
        assert scanner.cache_misses == 0, f"Scan kedua harus 0 misses, dapat {scanner.cache_misses}"

        print(f"  Scan 2 → hits={scanner.cache_hits}, misses={scanner.cache_misses}")
        print("  ✔ Cache hit pada repeated scan benar")
    finally:
        shutil.rmtree(tmp)


def test_scanner_cache_invalidation():
    print("\n[TEST] cache invalidation kalau file berubah")

    tmp = create_test_folder()
    target = os.path.join(tmp, "file_a.txt")

    try:
        cache = HashCache()
        scanner = HashScanner(cache=cache)

        # Scan pertama
        scanner.scan(tmp)
        hash_before = cache.get(target)
        assert hash_before is not None

        # Ubah konten file
        # Tunggu sebentar biar mtime pasti beda
        time.sleep(0.05)
        with open(target, "wb") as f:
            f.write(b"konten baru setelah diubah")

        # Cache harus invalid sekarang
        cached = cache.get(target)
        assert cached is None, "Cache harus None setelah file diubah"

        # Scan kedua: file_a.txt harus di-hash ulang (miss)
        scanner.scan(tmp)

        # 7 file tidak berubah → hits, 1 file berubah → miss
        assert scanner.cache_hits == 7, f"Harusnya 7 hits, dapat {scanner.cache_hits}"
        assert scanner.cache_misses == 1, f"Harusnya 1 miss, dapat {scanner.cache_misses}"

        print(f"  hits={scanner.cache_hits}, misses={scanner.cache_misses}")
        print("  ✔ Cache invalidation benar")
    finally:
        shutil.rmtree(tmp)


def test_scanner_cache_duplicate_detection_intact():
    print("\n[TEST] duplicate detection tetap akurat dengan cache")

    tmp = create_test_folder()

    try:
        cache = HashCache()
        scanner = HashScanner(cache=cache)

        # Scan pertama tanpa cache
        scanner.scan(tmp)
        dupes_first = scanner.get_duplicates()

        # Scan kedua dengan cache penuh
        scanner.scan(tmp)
        dupes_second = scanner.get_duplicates()

        # Hasil harus identik
        assert len(dupes_first) == len(dupes_second), "Jumlah duplicate group harus sama"

        counts_first = sorted([g.count for g in dupes_first], reverse=True)
        counts_second = sorted([g.count for g in dupes_second], reverse=True)
        assert counts_first == counts_second, "Isi duplicate group harus sama"

        print(f"  Scan 1: {len(dupes_first)} groups")
        print(f"  Scan 2: {len(dupes_second)} groups (semua dari cache)")
        print("  ✔ Duplicate detection tetap akurat")
    finally:
        shutil.rmtree(tmp)


def test_scanner_no_cache_still_works():
    print("\n[TEST] scanner tanpa cache tetap berjalan normal")

    tmp = create_test_folder()

    try:
        # Tidak pass cache sama sekali
        scanner = HashScanner()
        scanner.scan(tmp)

        # Statistik cache harus 0 semua
        assert scanner.cache_hits == 0
        assert scanner.cache_misses == 0
        assert scanner.total_files == 8

        print(f"  total_files={scanner.total_files}, hits={scanner.cache_hits}, misses={scanner.cache_misses}")
        print("  ✔ Scanner tanpa cache tetap normal")
    finally:
        shutil.rmtree(tmp)


# ─── Runner ───────────────────────────────────────────────────────────────────

def main():
    print("=" * 50)
    print("Teleoder Hash Scanner - Manual Test")
    print("=" * 50)

    tests = [
        test_hash_file,
        test_hash_file_different,
        test_hash_file_safe_missing,
        test_is_same_file,
        test_scanner_scan,
        test_scanner_duplicates,
        test_scanner_summary,
        test_scanner_progress_callback,
        test_scanner_not_a_directory,
        test_scanner_cache_hit,
        test_scanner_cache_invalidation,
        test_scanner_cache_duplicate_detection_intact,
        test_scanner_no_cache_still_works,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"  ✘ FAILED: {e}")
            failed += 1

    print("\n" + "=" * 50)
    print(f"Hasil: {passed} passed, {failed} failed")
    print("=" * 50)


if __name__ == "__main__":
    main()
