# Teleoder

CLI tool untuk download media dari channel Telegram menggunakan Telethon.

---

## ✨ Fitur

* Download media dari channel Telegram
* Filter media (photo, video, document)
* Progress download (speed + ETA)
* Skip file yang sudah ada (no re-download)
* CLI + menu interaktif
* Sistem login (OTP + 2FA)

---

## 📦 Instalasi

```bash
git clone https://github.com/USERNAME/teleoder.git
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

```bash
python main.py --login
```

Masukkan OTP dan password (jika ada 2FA).

---

## 🚀 Cara Pakai

### Mode CLI

```bash
python main.py --cli @channelname --filter photo
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

* `all` (default)
* `photo`
* `video`
* `document`

---

## 📁 Output

File akan disimpan di:

```
~/Downloads/Tele
```

---

## ⚠️ Catatan

* Jangan upload `config.py` (berisi data pribadi)
* Jangan upload folder `session/`
* Gunakan `config.example.py` sebagai template

---

## 🛠️ Roadmap

* [ ] Limit download (`--limit`)
* [ ] Resume download
* [ ] GUI (CustomTkinter)
* [ ] Multi account session

---

## 📄 License

MIT License
