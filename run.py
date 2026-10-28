"""Main entry point of the program.

QUICKEST WAY TO RUN
-------------------
    py run.py

Then open http://127.0.0.1:8000 in a browser.

OTHER OPTIONS
-------------
    py run.py --port 9000     run on a different port
    py run.py --no-browser    do not open the browser automatically
    py run.py demo            run every demo in the terminal (no web UI)
    py run.py test            run the algorithm correctness tests

This file is intentionally simple and well commented, because it is the
first file people open when they want to know how to run the program.
"""

import argparse
import sys
import threading
import time
import webbrowser
from pathlib import Path

# Make sure Python can find the src/ folder regardless of where it is launched from.
sys.path.insert(0, str(Path(__file__).resolve().parent))


def check_python_version() -> None:
    """This program uses `int | None` syntax, which requires Python 3.10+."""
    if sys.version_info < (3, 10):
        raise SystemExit(
            f"This program requires Python 3.10 or newer.\n"
            f"Installed Python: {sys.version.split()[0]}\n"
            f"Please update Python at https://www.python.org/downloads/"
        )


def run_web(port: int, open_browser: bool) -> None:
    from src.server import serve

    if open_browser:
        # Open the browser from a separate thread after a short delay, so the
        # server is ready to accept requests when the page loads.
        def opener() -> None:
            time.sleep(1.0)
            webbrowser.open(f"http://127.0.0.1:{port}")

        threading.Thread(target=opener, daemon=True).start()

    try:
        serve(port=port)
    except OSError as e:
        if getattr(e, "errno", None) in (48, 98, 10048):
            raise SystemExit(
                f"Port {port} is already in use by another program.\n"
                f"Try a different port, for example:  py run.py --port {port + 1}"
            ) from e
        raise


def run_demo() -> None:
    """Run every demo in the terminal; useful for taking screenshots."""
    import runpy

    modules = [
        ("PROCESS SCHEDULING", "src.scheduling.demo"),
        ("RACE CONDITION", "src.ipc.race_condition"),
        ("PRODUCER - CONSUMER", "src.ipc.producer_consumer"),
        ("DINING PHILOSOPHERS", "src.ipc.dining_philosophers"),
        ("BANKER'S ALGORITHM", "src.deadlock.bankers"),
        ("DEADLOCK DETECTION & RECOVERY", "src.deadlock.detection"),
    ]
    for i, (title, mod) in enumerate(modules, 1):
        print()
        print("#" * 72)
        print(f"#  DEMO {i} of {len(modules)}: {title}")
        print("#" * 72)
        try:
            runpy.run_module(mod, run_name="__main__")
        except Exception as e:  # noqa: BLE001
            print(f"  Demo '{title}' failed to run: {e}")
    print()
    print("#" * 72)
    print("#  ALL DEMOS FINISHED")
    print("#" * 72)


def run_tests() -> int:
    """Run the test files in the tests/ folder."""
    import subprocess

    here = Path(__file__).resolve().parent
    files = sorted((here / "tests").glob("test_*.py"))
    if not files:
        print("No test files found in the tests/ folder")
        return 1

    failed = 0
    for f in files:
        print()
        print("#" * 72)
        print(f"#  RUNNING {f.name}")
        print("#" * 72)
        code = subprocess.call([sys.executable, str(f)], cwd=str(here))
        if code != 0:
            failed += 1
            print(f"  -> {f.name} FAILED")
        else:
            print(f"  -> {f.name} all passed")

    print()
    print("=" * 72)
    if failed:
        print(f"RESULT: {failed} of {len(files)} test files FAILED")
    else:
        print(f"RESULT: all {len(files)} test files PASSED")
    print("=" * 72)
    return 1 if failed else 0


def main() -> int:
    check_python_version()

    ap = argparse.ArgumentParser(
        description="Operating System Simulator - Scheduling, IPC, and Deadlock",
        epilog="Without any argument, the program starts the web interface.",
    )
    ap.add_argument(
        "mode",
        nargs="?",
        default="web",
        choices=["web", "demo", "test"],
        help="web (default) | demo (terminal) | test (run tests)",
    )
    ap.add_argument("--port", type=int, default=8000, help="port number for web mode")
    ap.add_argument(
        "--no-browser", action="store_true", help="do not open the browser automatically"
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
