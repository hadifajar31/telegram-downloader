from telethon.sync import TelegramClient
from telethon.errors import SessionPasswordNeededError
from config.config import API_ID, API_HASH, PHONE_NUMBER, SESSION_PATH
from core.logger import log_info, log_error


def login():
    client = TelegramClient(SESSION_PATH, API_ID, API_HASH)

    client.connect()

    if client.is_user_authorized():
        print("Sudah login.")
        log_info("Login check: already authorized")
        client.disconnect()
        return

    print("Login pertama kali...")

    client.send_code_request(PHONE_NUMBER)
    code = input("Masukkan OTP: ")

    try:
        client.sign_in(PHONE_NUMBER, code)
        print("Login berhasil!")
        log_info("Login success")

    except SessionPasswordNeededError:
        password = input("Masukkan password 2FA: ")
        try:
            client.sign_in(password=password)
            print("Login berhasil!")
            log_info("Login success (2FA)")
        except Exception as e:
            print(f"Login gagal: {e}")
            log_error(f"Login failed (2FA): {e}")

    except Exception as e:
        print(f"Login gagal: {e}")
        log_error(f"Login failed: {e}")

    client.disconnect()
