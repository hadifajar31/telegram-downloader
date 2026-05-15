# Teleoder

CLI tool untuk download media dari Telegram channel, group, dan supergroup menggunakan Telethon.
Mendukung streaming download, smart limit, dan resume otomatis.

---

## ⚡ Highlight
* Resume otomatis per channel (last_id)
* Skip file yang sudah ada (no re-download)
* Smart limit (skip file tidak dihitung)
* Streaming download (tanpa scan list dulu)
* Handle FloodWait otomatis (delay + retry)
* Advanced media filter berdasarkan cara kirim Telegram
* Compare engine (anti re-download)
* Graceful Ctrl+C shutdown
* Download by ID/date range
* CLI output lebih clean + informative
* Struktur folder otomatis per channel + media type

---

## ✨ Fitur

* CLI + menu interaktif
* Download media dari channel, group, dan supergroup Telegram
* Advanced media filter:
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
* Progress download (speed + ETA)
* Resume otomatis (last_id per channel)
* Sistem login (OTP + 2FA)
* Skip file yang sudah ada
* Smart limit (skip tidak dihitung)
* Stop download kapan saja
* Streaming download
* Download by ID range (min-id / max-id)
* Download by date range (from-date / to-date)

---

## 🗂️ Struktur Project

```
core/
├── downloader.py
├── filters.py
├── naming.py
├── compare.py
├── resume.py
└── utils.py
```

---

## 📦 Instalasi

```bash
git clone https://github.com/hadifajar31/telegram-downloader
cd telegram-downloader
pip install -r requirements.txt
```

---

## ⚙️ Setup Config

Copy file config:

```bash
cp config/config.example.py config/config.py
```

Lalu isi:

```python
API_ID = ...
API_HASH = "..."
PHONE_NUMBER = "..."
```

---

## 🔐 Login

Jalankan:

```bash
python main.py
```

Lalu pilih:

1. Login

Masukkan OTP dan password (jika ada 2FA).

---

## 🚀 Cara Pakai

### Mode CLI

```bash
# Download foto, limit 5
python main.py --cli -- --channel=@channelname --filter photo --limit 5

# Download video berdasarkan ID range
python main.py --cli -- --channel=@test --filter video --min-id 100 --max-id 200

# Download berdasarkan date range
python main.py --cli -- --channel=@test --from-date 2025-01-01 --to-date 2025-01-31
```

### Mode Menu

```bash
python main.py
```

Lalu pilih:

```
1. Login
2. CLI
3. GUI (coming soon)
```

---

## 🎯 Filter yang tersedia

* all
* photo
* photo_document
* video
* video_note
* video_document
* gif
* audio
* voice
* archive
* sticker
* document

---

## 📁 Output

File akan disimpan di:

```
~/Downloads/Tele/<Channel>/<Filter>/
```

Contoh:
```
Tele/
└── CH Tes publik/
    ├── photo/
    └── photo_document/
```

## 📊 Contoh Output
```
Channel : @example
Filter  : photo
Limit   : 5
Min ID  : -
Max ID  : -
From    : -
To      : -

Memulai download...
Total   : 120 messages
Resume  : last_id 80

[1/?] image.jpg
  Progress: 100.0%  |  1.20 MB/s  |  ETA: 0s

✔ Download selesai (5/5 file berhasil)
```

---

## 🚀 Current Focus

* GUI (CustomTkinter)
* Topic system
* Dedup system (MD5/hash)
* Sync system

---

## 🧠 Planned Features

* MD5 deduplication
* Multi-source archive
* GUI

---

## 📄 License

MIT License
