"""Test every API endpoint over real HTTP.

Run:  py tests/test_api.py

This script starts the server on its own port, sends it HTTP requests the
way a browser does, and checks the responses. That way the test covers not
only the Python functions but the full path from the browser to the result.
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
        print(f"  PASS  {label}" + (f" -> {extra}" if extra else ""))
    else:
        failed += 1
        print(f"  FAIL  {label}" + (f" -> {extra}" if extra else ""))


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
print(f"Test server running at {BASE}\n")

try:
    print("=" * 70)
    print("STATIC FILES")
    print("=" * 70)
    st, body = get("/")
    check("GET / returns HTML", st == 200 and b"<html" in body.lower(), f"{len(body)} bytes")
    st, _ = get("/css/style.css")
    check("GET /css/style.css", st == 200)
    st, _ = get("/missing-file.txt")
    check("missing file -> 404", st == 404)
    st, _ = get("/../run.py")
    check("path traversal rejected", st in (403, 404), f"status {st}")

    print()
    print("=" * 70)
    print("SCHEDULING API")
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
    check("returns 6 algorithms", len(d.get("results", [])) == 6)
    check("has an insight section", "insight" in d)
    r0 = d["results"][0]
    check("every result has a timeline", bool(r0["timeline"]))
    check("every result has metrics", len(r0["metrics"]) == 4)
    check("every result has a log", bool(r0["log"]))
    check(
        "total CPU used = total burst",
        all(
            sum(s["duration"] for s in r["timeline"] if s["pid"] != "IDLE") == 26
            for r in d["results"]
        ),
    )
    check(
        "formula waiting = turnaround - burst",
        all(
            m["waiting"] == m["turnaround"] - m["burst"]
            for r in d["results"]
            for m in r["metrics"]
        ),
    )

    st, d = post("/api/scheduling", {"algorithm": "fcfs", "processes": [{"burst": 5}]})
    check("single algorithm only", st == 200 and len(d["results"]) == 1)

    st, d = post("/api/scheduling", {"processes": []})
    check("empty process list -> 400", st == 400, d.get("error", "")[:48])

    st, d = post("/api/scheduling", {"algorithm": "nonexistent", "processes": [{"burst": 2}]})
    check("unknown algorithm -> 400", st == 400)

    st, d = post(
        "/api/scheduling",
        {"processes": [{"pid": "A", "burst": 2}, {"pid": "A", "burst": 3}]},
    )
    check("duplicate process name -> 400", st == 400, d.get("error", "")[:48])

    st, d = post("/api/scheduling", {"processes": [{"burst": 999}]})
    check(
        "excessive burst rejected with a clear message",
        st == 400 and "Burst time" in d.get("error", ""),
        d.get("error", ""),
    )

    print()
    print("=" * 70)
    print("IPC API")
    print("=" * 70)
    st, d = post("/api/ipc/race", {"trials": 2, "threads": 4, "increments": 500})
    check("race: status 200", st == 200)
    check("race: 2 trials returned", len(d.get("trials", [])) == 2)
    check(
        "race: version with lock is ALWAYS correct",
        all(t["safe"] == t["expected"] for t in d["trials"]),
    )
    check(
        "race: version without lock never exceeds the correct value",
        all(t["unsafe"] <= t["expected"] for t in d["trials"]),
    )

    st, d = post(
        "/api/ipc/producer-consumer",
        {"capacity": 3, "producers": 2, "consumers": 2, "items": 4},
    )
    check("prod-cons: status 200", st == 200)
    check("prod-cons: produced = 8", d.get("produced") == 8, str(d.get("produced")))
    check("prod-cons: no overflow", d.get("overflow_detected") is False)
    check(
        "prod-cons: buffer size <= capacity in ALL events",
        all(e["buffer_size"] <= 3 for e in d["events"]),
        f"peak {d.get('peak_buffer_usage')}",
    )
    check("prod-cons: counts balanced", d.get("balanced") is True)
    check("prod-cons: no hanging threads", d.get("stuck_threads") == [])

    st, d = post("/api/ipc/philosophers", {"strategy": "all", "meals": 2})
    check("philosophers: status 200", st == 200)
    check("philosophers: 3 strategies tested", len(d.get("results", [])) == 3)
    byname = {r["strategy"]: r for r in d["results"]}
    check(
        "philosophers: ordering does not deadlock",
        byname["ordering"]["deadlocked"] is False,
    )
    check("philosophers: waiter does not deadlock", byname["waiter"]["deadlocked"] is False)
    check(
        "philosophers: ordering lets everyone eat",
        byname["ordering"]["total_eaten"] == 10,
        str(byname["ordering"]["total_eaten"]),
    )
    check(
        "philosophers: naive has problems (deadlock or incomplete meals)",
        byname["naive"]["deadlocked"] or byname["naive"]["total_eaten"] < 10,
        f"deadlock={byname['naive']['deadlocked']}, eaten={byname['naive']['total_eaten']}",
    )

    st, d = post("/api/ipc/philosophers", {"strategy": "invalid"})
    check("unknown strategy -> 400", st == 400)

    print()
    print("=" * 70)
    print("DEADLOCK API")
    print("=" * 70)
    st, d = post("/api/deadlock/bankers", {})
    check("banker: status 200", st == 200)
    check("banker: standard example is SAFE", d["safety"]["safe"] is True)
    check(
        "banker: safe sequence contains all 5 processes",
        len(d["safety"]["sequence"]) == 5,
        " -> ".join(d["safety"]["sequence"]),
    )
    check("banker: Need = Max - Allocation", d["state"]["need"][0] == [7, 4, 3])
    check("banker: system total [10,5,7]", d["state"]["total"] == [10, 5, 7])

    st, d = post("/api/deadlock/bankers", {"example": "unsafe"})
    check("banker: unsafe example detected", d["safety"]["safe"] is False)

    st, d = post(
        "/api/deadlock/bankers",
        {"request": {"process": "P1", "amounts": [1, 0, 2]}},
    )
    check("banker: P1 requests [1,0,2] GRANTED", d["request"]["granted"] is True)

    st, d = post(
        "/api/deadlock/bankers",
        {"request": {"process": "P4", "amounts": [3, 3, 0]}},
    )
    check(
        "banker: P4 requests [3,3,0] denied because unsafe",
        d["request"]["granted"] is False and d["request"]["reason"] == "unsafe",
        d["request"]["reason"],
    )

    st, d = post(
        "/api/deadlock/bankers",
        {"request": {"process": "P0", "amounts": [4, 0, 0]}},
    )
    check(
        "banker: request exceeds Available -> postponed",
        d["request"]["reason"] == "must_wait",
        d["request"]["reason"],
    )

    st, d = post(
        "/api/deadlock/bankers",
        {"request": {"process": "P2", "amounts": [0, 1, 0]}},
    )
    check(
        "banker: request exceeds Need -> process error",
        d["request"]["reason"] == "exceeds_need",
        d["request"]["reason"],
    )

    st, d = post(
        "/api/deadlock/bankers",
        {"request": {"process": "Unknown", "amounts": [0, 0, 0]}},
    )
    check("banker: unknown process -> 400", st == 400)

    st, d = post("/api/deadlock/detection", {"kind": "graph", "example": "deadlock"})
    check("graph detection: deadlock found", d["detection"]["deadlock"] is True)
    check(
        "graph detection: cycle P1->P2->P3->P1",
        d["detection"]["cycles"][0] == ["P1", "P2", "P3", "P1"],
        str(d["detection"]["cycles"][0]),
    )

    st, d = post("/api/deadlock/detection", {"kind": "graph", "example": "safe"})
    check("graph detection: no cycle -> safe", d["detection"]["deadlock"] is False)

    st, d = post("/api/deadlock/detection", {"kind": "multi"})
    check("multi detection: deadlock found", d["detection"]["deadlock"] is True)
    check(
        "multi detection: all four processes stuck",
        len(d["detection"]["deadlocked_processes"]) == 4,
    )
    check("multi detection: has a recovery section", "recovery" in d)
    check("multi detection: recovery succeeded", d["recovery"]["resolved"] is True)
    check(
        "multi detection: all three recovery strategies succeed",
        all(c["resolved"] for c in d["recovery_comparison"]),
    )
    check(
        "multi detection: most_resources has the fewest victims",
        min(d["recovery_comparison"], key=lambda c: c["victim_count"])["strategy"]
        == "most_resources",
    )

    st, d = post("/api/deadlock/detection", {"kind": "ostrich"})
    check("ostrich: status 200", st == 200 and "ostrich" in d)
    check("ostrich: takes no action", d["ostrich"]["action_taken"] == "none")

    st, d = post("/api/deadlock/detection", {"kind": "invalid"})
    check("unknown kind -> 400", st == 400)

    print()
    print("=" * 70)
    print("ERROR HANDLING")
    print("=" * 70)
    st, d = post("/api/fake-endpoint", {})
    check("missing endpoint -> 404", st == 404)

    req = urllib.request.Request(
        BASE + "/api/scheduling",
        data=b"{not json",
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        urllib.request.urlopen(req, timeout=10)
        check("broken JSON -> 400", False)
    except urllib.error.HTTPError as e:
        check("broken JSON -> 400", e.code == 400)

finally:
    srv.shutdown()
    srv.server_close()

print()
print("=" * 70)
print(f"RESULT: {passed} passed, {failed} failed")
print("=" * 70)
sys.exit(1 if failed else 0)
