# 🚀 Teleoder Roadmap

---

## 🥇 Phase 1 — Core Features

* [x] Limit
* [x] Stop download kapan saja
* [x] Resume otomatis (last_id)

---

## 🥈 Phase 2 — Mode Download

* [x] Semua

* [x] Sebagian (Limit)

* [ ] Rentang ID

* [ ] Rentang tanggal

* [ ] Offset + Limit

* [ ] Merge 2 channel

* [ ] Compare folder lokal

* [x] Target-based download (limit pintar, skip tidak dihitung)

---

## 🥉 Phase 3 — System Improvements

- [x] Skip file yang sudah ada
- [x] Cleanup import tidak terpakai (MessageMediaPhoto, MessageMediaDocument)
- [x] Streaming mode (scan + download langsung)
- [x] Early stop saat limit tercapai

- [x] Lanjut tanpa crash
- [x] Handle FloodWait otomatis (delay + retry)
- [x] Error handling lebih rapi (cleanup Telethon, no database lock)
  - resume hanya update saat download sukses
  - retry lebih aman
  - cleanup session lebih rapi
- [ ] Handle Ctrl+C saat active transfer (Telethon pending task)

- [ ] Skip file duplikat (MD5)
- [ ] Compare folder (anti re-download)

- [x] Advanced media filter
  - ikuti cara kirim Telegram
  - bukan hanya mime type
  - support:
    - photo
    - photo_document
    - video
    - video_note
    - video_document
    - gif
    - audio
    - voice
    - archive
    - sticker
    - document

- [x] Struktur folder:
  - per channel
  - per filter

- [ ] Penamaan file
  - native media:
    - photo_<message_id>
    - video_<message_id>
    - support grouped_id
  - document media:
    - keep original filename
    - fallback anti overwrite

- [ ] Sinkronisasi file
- [ ] Skip duplikat antar channel

---

## 🧩 Phase 4 — UX & Polish

* [x] Validasi input (limit, dll)
* [x] Output lebih clean
* [ ] Logging (opsional)

---

## 🖥️ Phase 5 — GUI

* [ ] GUI basic
* [ ] Progress bar
* [ ] Tombol stop
* [ ] Pilih mode download

---

## 🧩 Minor / Nanti (Parking Lot)

> Tidak urgent, kerjakan setelah fitur utama selesai

* [ ] Logout akun
* [ ] Optimize save resume (batch, tidak setiap pesan)
* [ ] Fix main.py --cli argument forwarding
* [ ] Prevent downloader auto-login prompt
* [ ] Add __main__ entry for cli.py
* [ ] Improve CLI UX
* [x] Rapihin output CLI
* [x] Tampilkan total asli + total setelah resume
* [x] Validasi input CLI lebih ketat
* [x] Refactor kecil (cleanup code)
* [x] Improve display limit (None → all)
* [x] Rapihin output progress

---

## 📌 Status

✔ Limit
✔ Stop
✔ Resume
✔ Streaming
✔ Target-based limit (smart)
✔ Early stop
✔ Skip existing file

➡️ NEXT:
- [ ] Penamaan file
  - native media:
    - photo_<message_id>
    - video_<message_id>
    - support grouped_id
  - document media:
    - keep original filename
    - fallback anti overwrite