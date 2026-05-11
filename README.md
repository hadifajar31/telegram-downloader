# Teleoder

CLI tool untuk download media dari channel Telegram menggunakan Telethon.
Mendukung streaming download, smart limit, dan resume otomatis.

---

## ⚡ Highlight
* Resume otomatis per channel (last_id)
* Skip file yang sudah ada (no re-download)
* Smart limit (skip file tidak dihitung)
* Streaming download (tanpa scan list dulu)
* Handle FloodWait otomatis (delay + retry)
* Advanced media filter berdasarkan cara kirim Telegram

---

## ✨ Fitur

* CLI + menu interaktif
* Download media dari channel Telegram
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

---

## 📦 Instalasi

```bash
git clone https://github.com/hadifajar31/telegram-downloader
cd teleoder
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
python main.py --cli @channelname --filter photo --limit 5
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
* Advanced media filter:
 - all

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

---

## 📁 Output

File akan disimpan di:

```
~/Downloads/Tele
```

## 📊 Contoh Output
```
✔ Download selesai (2/2 file berhasil)
⚠ Download selesai (1/2 file ditemukan)
ℹ Selesai! 7 file diproses (3 download, 4 skip)
```

---

## 🛠️ Roadmap
* Limit download
* Resume download
* Streaming download
* FloodWait handling
* GUI (CustomTkinter)
* Multi account session

---

## 📄 License

MIT License
