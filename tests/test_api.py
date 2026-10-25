"""Uji seluruh endpoint API lewat HTTP sungguhan.

Jalankan:  py tests/test_api.py

Skrip ini menyalakan server di port tersendiri, menembaknya dengan
permintaan HTTP seperti yang dilakukan browser, lalu memeriksa balasannya.
Dengan begitu yang diuji bukan hanya fungsi Python-nya, tapi juga jalur
lengkap dari browser sampai hasil.
"""

import json
import sys
import threading
import time
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.server import Handler

PORT = 0
BASE = f"http://127.0.0.1:{PORT}"

passed = 0
failed = 0


def check(label: str, cond: bool, extra: str = "") -> None:
    global passed, failed
    if cond:
        passed += 1
        print(f"  LULUS  {label}" + (f" -> {extra}" if extra else ""))
    else:
        failed += 1
        print(f"  GAGAL  {label}" + (f" -> {extra}" if extra else ""))


def post(path: str, payload: dict) -> tuple[int, dict]:
    req = urllib.request.Request(
        BASE + path,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())


def get(path: str) -> tuple[int, bytes]:
    try:
        with urllib.request.urlopen(BASE + path, timeout=15) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()


# ---------------------------------------------------------------- start
srv = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
BASE = f"http://127.0.0.1:{srv.server_port}"
threading.Thread(target=srv.serve_forever, daemon=True).start()
time.sleep(0.6)
print(f"Server uji berjalan di {BASE}\n")

try:
    print("=" * 70)
    print("BERKAS STATIS")
    print("=" * 70)
    st, body = get("/")
    check("GET / mengembalikan HTML", st == 200 and b"<html" in body.lower(), f"{len(body)} byte")
    st, _ = get("/css/style.css")
    check("GET /css/style.css", st == 200)
    st, _ = get("/berkas-tidak-ada.txt")
    check("berkas tidak ada -> 404", st == 404)
    st, _ = get("/../run.py")
    check("path traversal ditolak", st in (403, 404), f"status {st}")

    print()
    print("=" * 70)
    print("API PENJADWALAN")
    print("=" * 70)
    st, d = post(
        "/api/scheduling",
        {
            "algorithm": "all",
            "quantum": 3,
            "processes": [
                {"pid": "P1", "arrival": 0, "burst": 8, "priority": 3},
                {"pid": "P2", "arrival": 1, "burst": 4, "priority": 1},
                {"pid": "P3", "arrival": 2, "burst": 9, "priority": 4},
                {"pid": "P4", "arrival": 3, "burst": 5, "priority": 2},
            ],
        },
    )
    check("status 200", st == 200)
    check("mengembalikan 6 algoritma", len(d.get("results", [])) == 6)
    check("ada bagian insight", "insight" in d)
    r0 = d["results"][0]
    check("setiap hasil punya timeline", bool(r0["timeline"]))
    check("setiap hasil punya metrics", len(r0["metrics"]) == 4)
    check("setiap hasil punya log", bool(r0["log"]))
    check(
        "total CPU terpakai = total burst",
        all(
            sum(s["duration"] for s in r["timeline"] if s["pid"] != "IDLE") == 26
            for r in d["results"]
        ),
    )
    check(
        "rumus waiting = turnaround - burst",
        all(
            m["waiting"] == m["turnaround"] - m["burst"]
            for r in d["results"]
            for m in r["metrics"]
        ),
    )

    st, d = post("/api/scheduling", {"algorithm": "fcfs", "processes": [{"burst": 5}]})
    check("satu algoritma saja", st == 200 and len(d["results"]) == 1)

    st, d = post("/api/scheduling", {"processes": []})
    check("daftar proses kosong -> 400", st == 400, d.get("error", "")[:48])

    st, d = post("/api/scheduling", {"algorithm": "tidakada", "processes": [{"burst": 2}]})
    check("algoritma tak dikenal -> 400", st == 400)

    st, d = post(
        "/api/scheduling",
        {"processes": [{"pid": "A", "burst": 2}, {"pid": "A", "burst": 3}]},
    )
    check("nama proses ganda -> 400", st == 400, d.get("error", "")[:48])

    st, d = post("/api/scheduling", {"processes": [{"burst": 999}]})
    check(
        "burst berlebihan ditolak dengan pesan jelas",
        st == 400 and "Burst time" in d.get("error", ""),
        d.get("error", ""),
    )

    print()
    print("=" * 70)
    print("API IPC")
    print("=" * 70)
    st, d = post("/api/ipc/race", {"trials": 2, "threads": 4, "increments": 500})
    check("race: status 200", st == 200)
    check("race: ada 2 percobaan", len(d.get("trials", [])) == 2)
    check(
        "race: versi dengan lock SELALU benar",
        all(t["safe"] == t["expected"] for t in d["trials"]),
    )
    check(
        "race: versi tanpa lock tidak pernah melebihi nilai benar",
        all(t["unsafe"] <= t["expected"] for t in d["trials"]),
    )

    st, d = post(
        "/api/ipc/producer-consumer",
        {"capacity": 3, "producers": 2, "consumers": 2, "items": 4},
    )
    check("prod-cons: status 200", st == 200)
    check("prod-cons: produksi = 8", d.get("produced") == 8, str(d.get("produced")))
    check("prod-cons: tidak ada overflow", d.get("overflow_detected") is False)
    check(
        "prod-cons: isi buffer <= kapasitas di SEMUA kejadian",
        all(e["buffer_size"] <= 3 for e in d["events"]),
        f"tertinggi {d.get('peak_buffer_usage')}",
    )
    check("prod-cons: jumlah seimbang", d.get("balanced") is True)
    check("prod-cons: tidak ada thread menggantung", d.get("stuck_threads") == [])

    st, d = post("/api/ipc/philosophers", {"strategy": "all", "meals": 2})
    check("filsuf: status 200", st == 200)
    check("filsuf: 3 strategi diuji", len(d.get("results", [])) == 3)
    byname = {r["strategy"]: r for r in d["results"]}
    check(
        "filsuf: ordering tidak deadlock",
        byname["ordering"]["deadlocked"] is False,
    )
    check("filsuf: waiter tidak deadlock", byname["waiter"]["deadlocked"] is False)
    check(
        "filsuf: ordering semua kebagian makan",
        byname["ordering"]["total_eaten"] == 10,
        str(byname["ordering"]["total_eaten"]),
    )
    check(
        "filsuf: naive bermasalah (deadlock atau makan tak lengkap)",
        byname["naive"]["deadlocked"] or byname["naive"]["total_eaten"] < 10,
        f"deadlock={byname['naive']['deadlocked']}, makan={byname['naive']['total_eaten']}",
    )

    st, d = post("/api/ipc/philosophers", {"strategy": "ngawur"})
    check("strategi tak dikenal -> 400", st == 400)

    print()
    print("=" * 70)
    print("API DEADLOCK")
    print("=" * 70)
    st, d = post("/api/deadlock/bankers", {})
    check("banker: status 200", st == 200)
    check("banker: contoh baku SAFE", d["safety"]["safe"] is True)
    check(
        "banker: safe sequence memuat semua 5 proses",
        len(d["safety"]["sequence"]) == 5,
        " -> ".join(d["safety"]["sequence"]),
    )
    check("banker: Need = Max - Allocation", d["state"]["need"][0] == [7, 4, 3])
    check("banker: total sistem [10,5,7]", d["state"]["total"] == [10, 5, 7])

    st, d = post("/api/deadlock/bankers", {"example": "unsafe"})
    check("banker: contoh unsafe terdeteksi", d["safety"]["safe"] is False)

    st, d = post(
        "/api/deadlock/bankers",
        {"request": {"process": "P1", "amounts": [1, 0, 2]}},
    )
    check("banker: P1 minta [1,0,2] DIKABULKAN", d["request"]["granted"] is True)

    st, d = post(
        "/api/deadlock/bankers",
        {"request": {"process": "P4", "amounts": [3, 3, 0]}},
    )
    check(
        "banker: P4 minta [3,3,0] ditolak karena unsafe",
        d["request"]["granted"] is False and d["request"]["reason"] == "unsafe",
        d["request"]["reason"],
    )

    st, d = post(
        "/api/deadlock/bankers",
        {"request": {"process": "P0", "amounts": [4, 0, 0]}},
    )
    check(
        "banker: permintaan melebihi Available -> ditunda",
        d["request"]["reason"] == "must_wait",
        d["request"]["reason"],
    )

    st, d = post(
        "/api/deadlock/bankers",
        {"request": {"process": "P2", "amounts": [0, 1, 0]}},
    )
    check(
        "banker: permintaan melebihi Need -> error proses",
        d["request"]["reason"] == "exceeds_need",
        d["request"]["reason"],
    )

    st, d = post(
        "/api/deadlock/bankers",
        {"request": {"process": "TidakAda", "amounts": [0, 0, 0]}},
    )
    check("banker: proses tak dikenal -> 400", st == 400)

    st, d = post("/api/deadlock/detection", {"kind": "graph", "example": "deadlock"})
    check("deteksi graf: deadlock ditemukan", d["detection"]["deadlock"] is True)
    check(
        "deteksi graf: siklus P1->P2->P3->P1",
        d["detection"]["cycles"][0] == ["P1", "P2", "P3", "P1"],
        str(d["detection"]["cycles"][0]),
    )

    st, d = post("/api/deadlock/detection", {"kind": "graph", "example": "safe"})
    check("deteksi graf: tanpa siklus -> aman", d["detection"]["deadlock"] is False)

    st, d = post("/api/deadlock/detection", {"kind": "multi"})
    check("deteksi multi: deadlock ditemukan", d["detection"]["deadlock"] is True)
    check(
        "deteksi multi: keempat proses macet",
        len(d["detection"]["deadlocked_processes"]) == 4,
    )
    check("deteksi multi: ada bagian recovery", "recovery" in d)
    check("deteksi multi: recovery berhasil", d["recovery"]["resolved"] is True)
    check(
        "deteksi multi: ketiga strategi recovery berhasil",
        all(c["resolved"] for c in d["recovery_comparison"]),
    )
    check(
        "deteksi multi: most_resources korban paling sedikit",
        min(d["recovery_comparison"], key=lambda c: c["victim_count"])["strategy"]
        == "most_resources",
    )

    st, d = post("/api/deadlock/detection", {"kind": "ostrich"})
    check("ostrich: status 200", st == 200 and "ostrich" in d)
    check("ostrich: tidak melakukan tindakan", d["ostrich"]["action_taken"] == "none")

    st, d = post("/api/deadlock/detection", {"kind": "ngawur"})
    check("kind tak dikenal -> 400", st == 400)

    print()
    print("=" * 70)
    print("PENANGANAN KESALAHAN")
    print("=" * 70)
    st, d = post("/api/endpoint-palsu", {})
    check("endpoint tak ada -> 404", st == 404)

    req = urllib.request.Request(
        BASE + "/api/scheduling",
        data=b"{bukan json",
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        urllib.request.urlopen(req, timeout=10)
        check("JSON rusak -> 400", False)
    except urllib.error.HTTPError as e:
        check("JSON rusak -> 400", e.code == 400)

finally:
    srv.shutdown()
    srv.server_close()

print()
print("=" * 70)
print(f"HASIL AKHIR: {passed} lulus, {failed} gagal")
print("=" * 70)
sys.exit(1 if failed else 0)
