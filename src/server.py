"""Server web untuk tampilan simulator.

Dibangun hanya dengan modul bawaan Python (http.server + json). Tidak ada
library tambahan, jadi tidak perlu `pip install` apa pun. Keputusan ini
diambil supaya program bisa dijalankan di komputer mana pun yang sudah
ada Python-nya, cukup dengan satu perintah.

Server ini melakukan dua hal:
  1. Menyajikan berkas statis dari folder web/ (HTML, CSS, JavaScript)
  2. Menyediakan API JSON di /api/* yang memanggil modul simulasi

Catatan keamanan: server ini sengaja hanya mendengarkan di 127.0.0.1
(localhost), jadi tidak bisa diakses dari komputer lain di jaringan.
Untuk tugas kuliah ini memang tidak perlu diakses dari luar.
"""

import json
import mimetypes
import re
import traceback
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from .deadlock import bankers, detection
from .ipc import dining_philosophers, producer_consumer, race_condition
from .scheduling import algorithms as sched
from .scheduling.models import Process

ROOT = Path(__file__).resolve().parents[1]
WEB_DIR = ROOT / "web"

# Windows tidak selalu mengenal tipe font web; daftarkan agar font lokal terlayani benar.
mimetypes.add_type("font/woff2", ".woff2")

# Batas atas untuk mencegah permintaan dari web membuat server kewalahan.
LIMITS = {
    "max_processes": 12,
    "max_burst": 50,
    "max_arrival": 100,
    "max_quantum": 20,
    "max_threads": 16,
    "max_increments": 50_000,
    "max_buffer": 10,
    "max_items": 12,
    "max_meals": 6,
}


def _clamp(value: int, low: int, high: int) -> int:
    return max(low, min(high, value))


def _integer(value, label: str, low: int, high: int) -> int:
    """Terima integer JSON/string integer; jangan mengubah masukan diam-diam."""
    if isinstance(value, str) and re.fullmatch(r"-?\d+", value.strip()):
        value = int(value)
    if type(value) is not int or not low <= value <= high:
        raise ValueError(f"{label} must be an integer from {low} to {high}")
    return value


# ======================================================================
# Handler untuk setiap endpoint API
# ======================================================================


def api_scheduling(payload: dict) -> dict:
    """POST /api/scheduling - jalankan satu atau semua algoritma."""
    raw = payload.get("processes")
    if not isinstance(raw, list) or not raw:
        raise ValueError("process list must not be empty")
    if len(raw) > LIMITS["max_processes"]:
        raise ValueError(f"maximum {LIMITS['max_processes']} processes")

    procs: list[Process] = []
    seen: set[str] = set()
    for i, p in enumerate(raw):
        if not isinstance(p, dict):
            raise ValueError("each process must be a data object")
        pid = p.get("pid", f"P{i + 1}")
        if not isinstance(pid, str) or not pid.strip() or len(pid.strip()) > 12:
            raise ValueError("process name must be 1 to 12 characters")
        pid = pid.strip()
        if pid in seen:
            raise ValueError(f"process name '{pid}' is used twice")
        seen.add(pid)
        procs.append(
            Process(
                pid=pid,
                arrival=_integer(p.get("arrival", 0), f"Arrival time {pid}", 0, LIMITS["max_arrival"]),
                burst=_integer(p.get("burst", 1), f"Burst time {pid}", 1, LIMITS["max_burst"]),
                priority=_integer(p.get("priority", 0), f"Priority {pid}", 0, 99),
            )
        )

    quantum = _integer(payload.get("quantum", 2), "Quantum", 1, LIMITS["max_quantum"])
    algo = str(payload.get("algorithm", "all")).lower()

    if algo == "all":
        results = sched.compare_all(procs, quantum=quantum)
        best_wait = min(results, key=lambda r: r.avg_waiting)
        best_resp = min(results, key=lambda r: r.avg_response)
        return {
            "mode": "compare",
            "quantum": quantum,
            "input": [vars(p) for p in procs],
            "results": [r.to_dict() for r in results],
            "insight": {
                "best_avg_waiting": best_wait.algorithm,
                "best_avg_waiting_value": best_wait.avg_waiting,
                "best_avg_response": best_resp.algorithm,
                "best_avg_response_value": best_resp.avg_response,
            },
        }

    kwargs = {}
    if algo == "rr":
        kwargs["quantum"] = quantum
    if algo == "priority":
        kwargs["preemptive"] = bool(payload.get("preemptive", False))
    result = sched.run(algo, procs, **kwargs)
    return {
        "mode": "single",
        "quantum": quantum,
        "input": [vars(p) for p in procs],
        "results": [result.to_dict()],
    }


def api_race(payload: dict) -> dict:
    """POST /api/ipc/race - demo race condition."""
    return race_condition.run_trials(
        trials=_clamp(int(payload.get("trials", 5)), 1, 10),
        n_threads=_clamp(int(payload.get("threads", 4)), 2, LIMITS["max_threads"]),
        increments=_clamp(
            int(payload.get("increments", 2000)), 100, LIMITS["max_increments"]
        ),
        force_preemption=bool(payload.get("force_preemption", True)),
    )


def api_producer_consumer(payload: dict) -> dict:
    """POST /api/ipc/producer-consumer - simulasi bounded buffer."""
    return producer_consumer.run_demo(
        capacity=_integer(payload.get("capacity", 5), "Capacity", 1, LIMITS["max_buffer"]),
        n_producers=_integer(payload.get("producers", 1), "Number of producers", 1, 5),
        n_consumers=_integer(payload.get("consumers", 1), "Number of consumers", 1, 5),
        items_each=_integer(payload.get("items", 8), "Number of items", 1, LIMITS["max_items"]),
        produce_delay=_integer(payload.get("produce_ms", 10), "Producer delay", 0, 100) / 1000,
        consume_delay=_integer(payload.get("consume_ms", 80), "Consumer delay", 0, 100) / 1000,
    )


def api_philosophers(payload: dict) -> dict:
    """POST /api/ipc/philosophers - Dining Philosophers."""
    strategy = str(payload.get("strategy", "naive")).lower()
    meals = _clamp(int(payload.get("meals", 3)), 1, LIMITS["max_meals"])
    if strategy == "all":
        return dining_philosophers.compare_all(meals=meals, timeout=3.0)
    return dining_philosophers.run_strategy(strategy, meals=meals, timeout=3.0)


def api_bankers(payload: dict) -> dict:
    """POST /api/deadlock/bankers - safety check dan resource request."""
    if payload.get("example") == "unsafe":
        state = bankers.unsafe_example()
    elif payload.get("allocation"):
        state = bankers.BankerState(
            processes=[str(p)[:8] for p in payload["processes"]],
            resources=[str(r)[:4] for r in payload["resources"]],
            allocation=[[int(v) for v in row] for row in payload["allocation"]],
            maximum=[[int(v) for v in row] for row in payload["maximum"]],
            available=[int(v) for v in payload["available"]],
        )
    else:
        state = bankers.classic_example()

    out = {"state": state.to_dict(), "safety": bankers.is_safe(state)}

    req = payload.get("request")
    if req:
        out["request"] = bankers.request_resources(
            state, str(req.get("process")), [int(v) for v in req.get("amounts", [])]
        )
    return out


def api_detection(payload: dict) -> dict:
    """POST /api/deadlock/detection - deteksi dan recovery."""
    kind = str(payload.get("kind", "graph")).lower()

    if kind == "graph":
        if payload.get("held_by"):
            g = detection.ResourceGraph(
                processes=[str(p)[:8] for p in payload["processes"]],
                resources=[str(r)[:8] for r in payload["resources"]],
                held_by={str(k): str(v) for k, v in payload["held_by"].items()},
                waiting={str(k): str(v) for k, v in payload["waiting"].items()},
            )
        elif payload.get("example") == "safe":
            g = detection.safe_graph()
        else:
            g = detection.deadlocked_graph()
        return {
            "kind": "graph",
            "graph": {
                "processes": g.processes,
                "resources": g.resources,
                "held_by": g.held_by,
                "waiting": g.waiting,
            },
            "detection": detection.detect_single_instance(g),
        }

    if kind == "multi":
        if payload.get("allocation"):
            st = detection.MultiInstanceState(
                processes=[str(p)[:8] for p in payload["processes"]],
                resources=[str(r)[:4] for r in payload["resources"]],
                allocation=[[int(v) for v in row] for row in payload["allocation"]],
                request=[[int(v) for v in row] for row in payload["request"]],
                available=[int(v) for v in payload["available"]],
            )
        elif payload.get("example") == "safe":
            st = detection.recoverable_multi()
        else:
            st = detection.deadlocked_multi()
        det = detection.detect_multi_instance(st)
        out = {"kind": "multi", "state": st.to_dict(), "detection": det}
        if det["deadlock"]:
            out["recovery"] = detection.recover_by_termination(
                st, strategy=str(payload.get("strategy", "most_resources"))
            )
            out["recovery_comparison"] = detection.compare_recovery_strategies(st)
        return out

    if kind == "ostrich":
        return {
            "kind": "ostrich",
            "ostrich": detection.ostrich_algorithm(
                bool(payload.get("deadlock_detected", True))
            ),
        }

    raise ValueError("kind must be 'graph', 'multi', or 'ostrich'")


ROUTES = {
    "/api/scheduling": api_scheduling,
    "/api/ipc/race": api_race,
    "/api/ipc/producer-consumer": api_producer_consumer,
    "/api/ipc/philosophers": api_philosophers,
    "/api/deadlock/bankers": api_bankers,
    "/api/deadlock/detection": api_detection,
}


# ======================================================================
# HTTP handler
# ======================================================================


class Handler(BaseHTTPRequestHandler):
    server_version = "SimulatorOS/1.0"

    def log_message(self, fmt: str, *args) -> None:
        # Hanya catat yang penting, supaya jendela terminal tidak penuh
        # oleh baris permintaan berkas statis.
        msg = fmt % args
        if "/api/" in msg or " 4" in msg or " 5" in msg:
            print(f"  [server] {msg}")

    # ---------- utilitas balasan ----------

    def _send_json(self, obj: dict, status: int = 200) -> None:
        body = json.dumps(obj, ensure_ascii=False, default=str).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _send_error_json(self, status: int, message: str, detail: str = "") -> None:
        self._send_json({"error": message, "detail": detail}, status=status)

    # ---------- GET: berkas statis ----------

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path

        if path.startswith("/api/"):
            # Beberapa endpoint boleh dipanggil lewat GET agar mudah diuji
            # langsung dari address bar browser.
            fn = ROUTES.get(path)
            if not fn:
                self._send_error_json(404, f"Endpoint {path} not found")
                return
            params = {k: v[0] for k, v in parse_qs(parsed.query).items()}
            self._handle_api(fn, params, path)
            return

        if path == "/":
            path = "/index.html"

        # Cegah path traversal (misal /../../rahasia.txt).
        safe = re.sub(r"[^A-Za-z0-9._/\-]", "", path).lstrip("/")
        target = (WEB_DIR / safe).resolve()
        if not target.is_relative_to(WEB_DIR.resolve()):
            self._send_error_json(403, "Access denied")
            return
        if not target.is_file():
            self._send_error_json(404, f"File {safe} not found")
            return

        ctype, _ = mimetypes.guess_type(str(target))
        data = target.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", ctype or "application/octet-stream")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    # ---------- POST: API ----------

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        fn = ROUTES.get(path)
        if not fn:
            self._send_error_json(404, f"Endpoint {path} not found")
            return

        try:
            length = int(self.headers.get("Content-Length") or 0)
            if length < 0:
                raise ValueError
        except ValueError:
            self._send_error_json(400, "Invalid content length")
            return
        if length > 200_000:
            self._send_error_json(413, "Request payload too large")
            return
        raw = self.rfile.read(length) if length else b"{}"
        try:
            payload = json.loads(raw or b"{}")
        except RecursionError:
            self._send_error_json(400, "JSON data too deeply nested")
            return
        except (ValueError, UnicodeDecodeError) as e:
            self._send_error_json(400, "Invalid JSON data", str(e))
            return
        if not isinstance(payload, dict):
            self._send_error_json(400, "Data must be a JSON object")
            return

        self._handle_api(fn, payload, path)

    def _handle_api(self, fn, payload: dict, path: str) -> None:
        """Jalankan handler API dan ubah error menjadi balasan JSON yang rapi."""
        try:
            self._send_json(fn(payload))
        except (ValueError, KeyError, TypeError) as e:
            # Kesalahan masukan dari pengguna - bukan kerusakan program.
            self._send_error_json(400, f"Invalid input: {e}")
        except Exception as e:  # noqa: BLE001
            # Kerusakan tak terduga: catat ke terminal agar bisa diperbaiki,
            # tapi jangan bocorkan seluruh traceback ke browser.
            print(f"  [server] ERROR di {path}: {e}")
            traceback.print_exc()
            self._send_error_json(500, "An error occurred on the server", str(e))


def serve(host: str = "127.0.0.1", port: int = 8000) -> None:
    """Jalankan server sampai dihentikan dengan Ctrl+C."""
    if not WEB_DIR.is_dir():
        raise SystemExit(f"Folder web/ tidak ditemukan di {WEB_DIR}")

    httpd = ThreadingHTTPServer((host, port), Handler)
    url = f"http://{host}:{port}"
    print()
    print("=" * 64)
    print("  SIMULATOR SISTEM OPERASI")
    print("=" * 64)
    print(f"  Server berjalan di : {url}")
    print("  Buka alamat di atas dengan browser (Chrome/Edge/Firefox).")
    print("  Tekan Ctrl+C di jendela ini untuk menghentikan server.")
    print("=" * 64)
    print()
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n  Server dihentikan. Sampai jumpa.")
    finally:
        httpd.server_close()
