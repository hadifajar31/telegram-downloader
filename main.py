import argparse

from cli.cli import main as cli_main
from core.auth import login
from core.input_helper import prompt_choice, prompt_int, prompt_date, prompt_channel


def run_menu():
    while True:
        print("Pilih mode:")
        print("1. Login")
        print("2. CLI")
        print("3. GUI")
        print("0. Keluar")

        choice = prompt_choice(
            "Masukkan pilihan (1/2/3/0): ",
            choices={"1": "login", "2": "cli", "3": "gui", "0": "exit"},
        )

        if choice == "login":
            login()

        elif choice == "cli":
            channel = prompt_channel("Masukkan channel (@username / link / ID): ")

            print("\n=== Filter ===")
            print("1. All")
            print()
            print("2. Photo")
            print("3. Photo Document")
            print()
            print("4. Video")
            print("5. Video Note")
            print("6. Video Document")
            print()
            print("7. GIF")
            print("8. Audio")
            print("9. Voice")
            print("10. Archive")
            print("11. Sticker")
            print("12. Document")

            filter_map = {
                "1": "all",

                "2": "photo",
                "3": "photo_document",

                "4": "video",
                "5": "video_note",
                "6": "video_document",

                "7": "gif",

                "8": "audio",
                "9": "voice",

                "10": "archive",

                "11": "sticker",

                "12": "document",
            }

            filter_type = prompt_choice("Masukkan pilihan: ", choices=filter_map, default="1")

            print("\n=== Range ===")
            limit = prompt_int(
                "Masukkan limit file (kosongkan untuk semua): ",
                allow_empty=True,
                min_value=1,
            )

            min_id = prompt_int(
                "Masukkan min ID (kosongkan untuk 0): ",
                allow_empty=True,
                default=0,
            )

            max_id = prompt_int(
                "Masukkan max ID (kosongkan untuk 0): ",
                allow_empty=True,
                default=0,
            )

            if max_id and max_id <= min_id:
                print("[ERROR] max_id harus lebih besar dari min_id.")
                continue

            from_date = prompt_date("Masukkan from date (kosongkan untuk skip): ")
            to_date = prompt_date("Masukkan to date (kosongkan untuk skip): ")

            args = ["--channel",channel, "--filter", filter_type]

            if limit is not None:
                args += ["--limit", str(limit)]

            if min_id:
                args += ["--min-id", str(min_id)]

            if max_id:
                args += ["--max-id", str(max_id)]

            if from_date:
                args += ["--from-date", from_date]

            if to_date:
                args += ["--to-date", to_date]

            print("\n=== Download ===")
            cli_main(args)

            print("\nKembali ke menu...")

        elif choice == "gui":
            print("GUI belum tersedia. Jalankan dengan --cli untuk mode terminal.")
            print("Pilih Mode 2 atau Jalankan Skrip di Bawah")
            print("Contoh: python main.py --cli @channelname --filter video")

        elif choice == "exit":
            print("Keluar...")
            break

        print()


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--login", action="store_true")
    parser.add_argument("--cli", action="store_true")
    parser.add_argument("--gui", action="store_true")

    args, unknown = parser.parse_known_args()

    if args.login:
        login()
        return

    if args.cli:
        cli_main(unknown)
        return

    if args.gui:
        print("GUI belum tersedia. Jalankan dengan --cli untuk mode terminal.")
        return

    # kalau gak pakai flag → masuk menu
    run_menu()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nKeluar...")