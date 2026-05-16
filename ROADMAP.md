# 🚀 Teleoder Roadmap

---

## 🥇 Phase 1 — Core Features

* [x] Limit
* [x] Stop download kapan saja
* [x] Resume otomatis (last_id)

---

## 🥈 Phase 2 — Mode 

### Mode Download

* [x] Semua

* [x] Sebagian (Limit)

* [x] Rentang ID

* [x] Rentang tanggal

* [x] Offset + Limit

* [ ] Merge 2 channel

### Mode Dedup 

* [ ] Off

* [ ] Fast Skip

* [ ] Smart Skip

* [ ] Content  Dedup

### Topic System

* [ ] Topic detection

* [ ] Topic mode

* [ ] Auto topic split

* [ ] Folder per topic

### Compare & Sync

* [x] Compare folder lokal

* [ ] Sinkronisasi file

* [ ] Multi-source compare

* [ ] Skip duplikat antar channel

### Dedup Engine

* [x] Hash scanner

* [x] Hash cache/database

* [ ] Global media index

---

## 🥉 Phase 3 — System Improvements

* [x] Target-based download (limit pintar, skip tidak dihitung)

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
- [x] Handle Ctrl+C saat active transfer (Telethon pending task)

- [x] Compare folder (anti re-download)
  - channel-scoped compare index
  - skip existing native media

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

- [x] Penamaan file
  - native media:
    - <type>_<message_id>
  - document media:
    - keep original filename
  - duplicate document:
    - auto rename (_2)

- [x] Album/grouped_id handling
  - grouped media detection
  - optional album folder structure

- [x] Resume manager modularization
  - extract resume state management
  - batching save terpisah dari downloader

---

## 🧩 Phase 4 — UX & Polish

* [x] Validasi input (limit, dll)
* [x] Output lebih clean
- [x] Input helper system
  - [x] validasi angka
  - [x] validasi pilihan menu
  - [x] validasi channel
  - [x] reusable prompt helper
* [x] Cleanup terminal progress line after stop/download finish
* [x] Better progress output for very fast downloads
* [x] Logging
---

## 🖥️ Phase 5 — GUI

* [ ] GUI basic
* [ ] Progress bar
* [ ] Tombol stop
* [ ] Pilih mode download
* [ ] Filter selector
* [ ] Dedup selector
* [ ] Topic selector
* [ ] Log panel
* [ ] Download history

---

## 🧩 Minor / Nanti (Parking Lot)

> Tidak urgent, kerjakan setelah fitur utama selesai

* [ ] Logout akun
* [ ] Colored console logging
* [ ] Verbose / quiet logging mode
* [ ] GUI log panel integration
* [ ] Structured JSON logging
* [ ] Improve download summary statistics
  - separate downloaded / skipped / failed count
  - avoid counting failed download as skipped
* [x] Fix main.py --cli argument forwarding
* [x] Prevent downloader auto-login prompt
* [x] Add __main__ entry for cli.py
* [x] Improve CLI UX
* [x] Only create album folder for grouped media with >1 item
* [x] Optimize save resume (batch, tidak setiap pesan)
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
✔ Graceful Ctrl+C shutdown
✔ Resume batch save

➡️ NEXT:
* [ ] Global media index