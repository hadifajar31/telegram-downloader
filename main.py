import argparse
from cli.cli import main as cli_main
from core.auth import login

def run_menu():
    while True:
        print("Pilih mode:")
        print("1. Login")
        print("2. CLI")
        print("3. GUI")
        print("0. Keluar")

        choice = input("Masukkan pilihan (1/2/3/0): ").strip()

        if choice == "1":
            login()

        elif choice == "2":
            channel = input("Masukkan channel (@username / link / ID): ").strip()

            print("\nPilih filter:")
            print("1. All")

            print("2. Photo")
            print("3. Photo Document")

            print("4. Video")
            print("5. Video Note")
            print("6. Video Document")

            print("7. GIF")

            print("8. Audio")
            print("9. Voice")

            print("10. Archive")

            print("11. Sticker")

            print("12. Document")

            filter_choice = input("Masukkan pilihan: ").strip()

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

            filter_type = filter_map.get(filter_choice, "all")

            limit_input = input("Masukkan limit file (kosongkan untuk semua): ").strip()

            min_id_input = input("Masukkan min ID (Kosongkan untuk 0): ").strip()
            max_id_input = input("Masukkan max ID (Kosongkan untuk 0): ").strip()

            args = [channel, "--filter", filter_type]

            if limit_input.isdigit() and int(limit_input) > 0:
                args += ["--limit", limit_input]

            try:
                min_id_value = int(min_id_input) if min_id_input else 0
                max_id_value = int(max_id_input) if max_id_input else 0

                if min_id_value < 0 or max_id_value < 0:
                    print("[ERROR] ID tidak boleh negatif.")
                    continue

                if max_id_value and max_id_value <= min_id_value:
                    print("[ERROR] max_id harus lebih besar dari min_id.")
                    continue

                if min_id_value > 0:
                    args += ["--min-id", str(min_id_value)]

                if max_id_value > 0:
                    args += ["--max-id", str(max_id_value)]

            except ValueError:
                print("[ERROR] min_id/max_id harus berupa angka.")
                continue

            except ValueError:
                print("[ERROR] offset harus beraupa angka.")
                continue

            cli_main(args)

            print("\nKembali ke menu...\n")

        elif choice == "3":
            print("GUI belum tersedia. Jalankan dengan --cli untuk mode terminal.")
            print("Pilih Mode 2 atau Jalankan Skrip di Bawah")
            print("Contoh: python main.py --cli @channelname --filter video")

        elif choice == "0":
            print("Keluar...\n")
            break

        else:
            print("Pilihan tidak valid.\n")

        print("\n")

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

    # 🔥 kalau gak pakai flag → masuk menu
    run_menu()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nKeluar...")