import argparse
from cli.cli import main as cli_main
from core.auth import login

def run_menu():
    print("Pilih mode:")
    print("1. Login")
    print("2. CLI")
    print("3. GUI")

    choice = input("Masukkan pilihan (1/2/3): ").strip()

    if choice == "1":
        login()

    elif choice == "2":
        channel = input("Masukkan channel (@username / link / ID): ").strip()

        print("\nPilih filter:")
        print("1. All")
        print("2. Photo")
        print("3. Video")
        print("4. Document")

        filter_choice = input("Masukkan pilihan (1/2/3/4): ").strip()

        filter_map = {
            "1": "all",
            "2": "photo",
            "3": "video",
            "4": "document",
        }

        filter_type = filter_map.get(filter_choice, "all")

        limit_input = input("Masukkan limit file (kosongkan untuk semua): ").strip()

        args = [channel, "--filter", filter_type]
        if limit_input.isdigit() and int(limit_input) > 0:
            args += ["--limit", limit_input]

        cli_main(args)

    elif choice == "3":
        print("GUI belum tersedia. Jalankan dengan --cli untuk mode terminal.")
        print("Pilih Mode 2 atau Jalankan Skrip di Bawah")
        print("Contoh: python main.py --cli @channelname --filter video")

    else:
        print("Pilihan tidak valid.")

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
    main()