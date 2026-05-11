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
- [ ] Error handling lebih rapi (cleanup Telethon, no database lock)
  - resume hanya update saat download sukses
  - retry lebih aman
  - cleanup session lebih rapi

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

- [ ] Struktur folder:
  - per channel
  - per filter

- [ ] Penamaan file (belum decided)

- [ ] Sinkronisasi file
- [ ] Skip duplikat antar channel

---

## 🧩 Phase 4 — UX & Polish

* [ ] Validasi input (limit, dll)
* [ ] Output lebih clean
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
* [ ] Rapihin output CLI
* [ ] Tampilkan total asli + total setelah resume
* [ ] Validasi input CLI lebih ketat
* [ ] Refactor kecil (cleanup code)
* [ ] Stop: hindari double print "STOPPED"
* [ ] Improve display limit (None → all)
* [ ] Rapihin output progress

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
- [ ] Error handling lebih rapi (cleanup Telethon, no database lock)
  - resume hanya update saat download sukses
  - retry lebih aman
  - cleanup session lebih rapi