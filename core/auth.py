from telethon.sync import TelegramClient
from telethon.errors import SessionPasswordNeededError
from config.config import API_ID, API_HASH, PHONE_NUMBER, SESSION_PATH

def login():
    client = TelegramClient(SESSION_PATH, API_ID, API_HASH)

    client.connect()

    if client.is_user_authorized():
        print("Sudah login.")
        client.disconnect()
        return

    print("Login pertama kali...")

    client.send_code_request(PHONE_NUMBER)
    code = input("Masukkan OTP: ")

    try:
        client.sign_in(PHONE_NUMBER, code)
    except SessionPasswordNeededError:
        password = input("Masukkan password 2FA: ")
        client.sign_in(password=password)

    print("Login berhasil!")

    client.disconnect()