"""Titik masuk utama program.

CARA PAKAI PALING MUDAH
-----------------------
    py run.py

Lalu buka http://127.0.0.1:8000 di browser.

CARA LAIN
---------
    py run.py --port 9000     jalankan di nomor port lain
    py run.py --no-browser    jangan buka browser otomatis
    py run.py demo            jalankan semua demo di terminal (tanpa web)
    py run.py test            jalankan pengujian kebenaran algoritma

Berkas ini sengaja dibuat sederhana dan banyak komentar, karena inilah
berkas pertama yang akan dibuka orang yang ingin tahu cara menjalankan
program ini.
"""

import argparse
import sys
import threading
import time
import webbrowser
from pathlib import Path

# Pastikan Python bisa menemukan folder src/ apa pun lokasi pemanggilannya.
sys.path.insert(0, str(Path(__file__).resolve().parent))


def check_python_version() -> None:
    """Program ini memakai sintaks `int | None` yang butuh Python 3.10+."""
    if sys.version_info < (3, 10):
        raise SystemExit(
            f"Program ini butuh Python 3.10 atau lebih baru.\n"
            f"Python yang terpasang: {sys.version.split()[0]}\n"
            f"Silakan perbarui Python di https://www.python.org/downloads/"
        )


def run_web(port: int, open_browser: bool) -> None:
    from src.server import serve

    if open_browser:
        # Browser dibuka dari thread terpisah dengan jeda singkat, supaya
        # server sudah siap menerima permintaan saat halaman dimuat.
        def opener() -> None:
            time.sleep(1.0)
            webbrowser.open(f"http://127.0.0.1:{port}")

        threading.Thread(target=opener, daemon=True).start()

    try:
        serve(port=port)
    except OSError as e:
        if getattr(e, "errno", None) in (48, 98, 10048):
            raise SystemExit(
                f"Port {port} sedang dipakai program lain.\n"
                f"Coba nomor port lain, contoh:  py run.py --port {port + 1}"
            ) from e
        raise


def run_demo() -> None:
    """Jalankan semua demo di terminal, berguna untuk mengambil screenshot."""
    import runpy

    modules = [
        ("PENJADWALAN PROSES", "src.scheduling.demo"),
        ("RACE CONDITION", "src.ipc.race_condition"),
        ("PRODUCER - CONSUMER", "src.ipc.producer_consumer"),
        ("DINING PHILOSOPHERS", "src.ipc.dining_philosophers"),
        ("BANKER'S ALGORITHM", "src.deadlock.bankers"),
        ("DETEKSI & RECOVERY DEADLOCK", "src.deadlock.detection"),
    ]
    for i, (title, mod) in enumerate(modules, 1):
        print()
        print("#" * 72)
        print(f"#  DEMO {i} dari {len(modules)}: {title}")
        print("#" * 72)
        try:
            runpy.run_module(mod, run_name="__main__")
        except Exception as e:  # noqa: BLE001
            print(f"  Demo '{title}' gagal dijalankan: {e}")
    print()
    print("#" * 72)
    print("#  SELURUH DEMO SELESAI")
    print("#" * 72)


def run_tests() -> int:
    """Jalankan berkas pengujian di folder tests/."""
    import subprocess

    here = Path(__file__).resolve().parent
    files = sorted((here / "tests").glob("test_*.py"))
    if not files:
        print("Tidak ada berkas pengujian di folder tests/")
        return 1

    failed = 0
    for f in files:
        print()
        print("#" * 72)
        print(f"#  MENJALANKAN {f.name}")
        print("#" * 72)
        code = subprocess.call([sys.executable, str(f)], cwd=str(here))
        if code != 0:
            failed += 1
            print(f"  -> {f.name} GAGAL")
        else:
            print(f"  -> {f.name} lulus semua")

    print()
    print("=" * 72)
    if failed:
        print(f"HASIL: {failed} dari {len(files)} berkas pengujian GAGAL")
    else:
        print(f"HASIL: seluruh {len(files)} berkas pengujian LULUS")
    print("=" * 72)
    return 1 if failed else 0


def main() -> int:
    check_python_version()

    ap = argparse.ArgumentParser(
        description="Simulator Sistem Operasi - Scheduling, IPC, dan Deadlock",
        epilog="Tanpa argumen apa pun, program menjalankan tampilan web.",
    )
    ap.add_argument(
        "mode",
        nargs="?",
        default="web",
        choices=["web", "demo", "test"],
        help="web (bawaan) | demo (terminal) | test (pengujian)",
    )
    ap.add_argument("--port", type=int, default=8000, help="nomor port untuk mode web")
    ap.add_argument(
        "--no-browser", action="store_true", help="jangan buka browser otomatis"
    )
    args = ap.parse_args()

    if args.mode == "demo":
        run_demo()
        return 0
    if args.mode == "test":
        return run_tests()

    run_web(port=args.port, open_browser=not args.no_browser)
    return 0


if __name__ == "__main__":
    sys.exit(main())
