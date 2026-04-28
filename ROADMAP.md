# 🚀 Teleoder Roadmap

---

## 🥇 Phase 1 — Core Features

* [x] Limit
* [x] Stop download kapan saja
* [ ] Resume otomatis (last_id)

---

## 🥈 Phase 2 — Mode Download

* [x] Semua

* [x] Sebagian (Limit)

* [ ] Rentang ID

* [ ] Rentang tanggal

* [ ] Offset + Limit

* [ ] Merge 2 channel

* [ ] Compare folder lokal

---

## 🥉 Phase 3 — System Improvements

- [x] Skip file yang sudah ada

- [ ] Handle FloodWait otomatis
- [ ] Delay otomatis
- [ ] Lanjut tanpa crash

- [ ] Skip file duplikat (MD5)
- [ ] Compare folder (anti re-download)

- [ ] Filter media: ikuti cara kirim Telegram (bukan mime type)
- [ ] Cleanup import tidak terpakai (MessageMediaPhoto, MessageMediaDocument)

- [ ] Struktur folder:
  - per channel
  - per filter (belum decided)

- [ ] Penamaan file:
  - format belum decided

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

* [ ] Stop: hindari double print "STOPPED"
* [ ] Improve display limit (None → all)
* [ ] Rapihin output progress
* [ ] Validasi input CLI lebih ketat
* [ ] Refactor kecil (cleanup code)

---

## 🧠 Catatan

* Fokus 1 fitur sampai selesai
* Jangan lompat-lompat
* Minor → masuk Parking Lot dulu
* Setelah 1 fitur selesai → boleh ambil 1–2 minor

---

## 🎯 Rule

* Feature → Stabil → Baru Optimasi
* 1 branch = 1 tujuan
* Jangan campur fitur + improvement

---

## 📌 Status

✔ Limit
✔ Stop
➡️ NEXT: Resume
