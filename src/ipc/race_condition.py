"""Demonstrating a race condition with real threads.

Topic: Process and Threads + IPC (critical section, mutual exclusion)

This is the key demo for understanding why synchronization is needed.
Several threads increment one shared variable N times each. Mathematically
the result must be n_threads * N. Without a lock, the result is smaller.

The cause: the operation `counter += 1` is NOT atomic. At machine level it
consists of three separate steps:
    1. READ   : load the counter value from memory into a register
    2. MODIFY : add 1 in the register
    3. WRITE  : store it back to memory

If thread A is interrupted right after step 1, and thread B then completes
all of 1-2-3, when A resumes it writes the old value + 1 and overwrites
B's work. One increment is lost. This is the "lost update".

IMPORTANT NOTE ON METHOD
------------------------
CPython has a Global Interpreter Lock (GIL) that makes thread switches
relatively rare. As a result, in a very tight loop the race condition
often does NOT show up even though the bug exists. That is why
`UnsafeCounter` calls `time.sleep(0)` between READ and WRITE.

`time.sleep(0)` does not actually sleep - it only forces the thread to
yield the CPU at that point. So we do NOT introduce a new bug: we only
arrange for preemption to happen at the worst possible moment, making
the existing bug observable every time.

This is exactly the most dangerous property of a race condition: it
depends on timing. Without this forcing, a WRONG program can pass tests
hundreds of times and then break on another computer or under heavy load.
The function `run_demo(force_preemption=False)` demonstrates this.
"""

import sys
import threading
import time


class UnsafeCounter:
    """Counter without protection. Deliberately unsafe."""

    def __init__(self, force_preemption: bool = True) -> None:
        self.value = 0
        self.force_preemption = force_preemption

    def increment(self) -> None:
        current = self.value  # 1. READ
        if self.force_preemption:
            # Yield the CPU right in the middle of the critical section.
            # This is where another thread slips in its increment, and its
            # work will be overwritten by the WRITE line below.
            time.sleep(0)
        current = current + 1  # 2. MODIFY
        self.value = current  # 3. WRITE


class SafeCounter:
    """The same counter, protected by a mutex (Lock).

    The lock guarantees mutual exclusion: only one thread may be inside the
    critical section at a time. Other threads that try to enter are blocked
    until the lock is released.

    Note that `time.sleep(0)` is still inside the critical section. Threads
    STILL switch in the middle of the operation, yet the result stays
    correct. This proves it is the lock that protects us, not lucky
    timing.
    """

    def __init__(self, force_preemption: bool = True) -> None:
        self.value = 0
        self.force_preemption = force_preemption
        self._lock = threading.Lock()

    def increment(self) -> None:
        with self._lock:  # ---- enter critical section ----
            current = self.value
            if self.force_preemption:
                time.sleep(0)
            current = current + 1
            self.value = current
        # ---- leave critical section, lock released automatically ----


def _hammer(counter, times: int) -> None:
    for _ in range(times):
        counter.increment()


def _run_threads(counter, n_threads: int, increments: int) -> None:
    threads = [
        threading.Thread(target=_hammer, args=(counter, increments), name=f"T{i + 1}")
        for i in range(n_threads)
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join()


def run_demo(
    n_threads: int = 4,
    increments: int = 2_000,
    force_preemption: bool = True,
) -> dict:
    """Run the unsafe and the safe version, then compare them.

    force_preemption=True  -> the bug almost always appears (for demonstration)
    force_preemption=False -> the bug often does not appear even though the code
                              is still wrong (shows the danger of
                              non-deterministic bugs)
    """
    expected = n_threads * increments
    log: list[str] = []
    original = sys.getswitchinterval()

    log.append(
        f"Running {n_threads} threads, each with {increments:,} increments "
        f"on ONE shared variable."
    )
    log.append(f"Mathematically correct value: {expected:,}")
    log.append(
        "Preemption mode: "
        + (
            "FORCED (yield in the middle of critical section)"
            if force_preemption
            else "NATURAL (dependent on GIL scheduling)"
        )
    )

    sys.setswitchinterval(1e-6)
    try:
        unsafe = UnsafeCounter(force_preemption=force_preemption)
        _run_threads(unsafe, n_threads, increments)

        safe = SafeCounter(force_preemption=force_preemption)
        _run_threads(safe, n_threads, increments)
    finally:
        sys.setswitchinterval(original)

    lost = expected - unsafe.value
    log.append("")
    log.append(f"WITHOUT LOCK : result = {unsafe.value:,}")
    if lost > 0:
        log.append(
            f"               {lost:,} increments LOST "
            f"({lost / expected * 100:.2f}% data corrupted)."
        )
        log.append(
            "               Cause: two threads read the same value, "
            "then overwrite each other's work (lost update)."
        )
    else:
        log.append(
            "               This time the result happened to be correct. The code is STILL "
            "incorrect - race condition just did not trigger."
        )

    log.append("")
    log.append(f"WITH LOCK    : result = {safe.value:,}")
    log.append(
        "               Exact, even though threads still switch in the middle of "
        "operations. The mutex forces increments to execute one by one."
    )

    return {
        "expected": expected,
        "unsafe_result": unsafe.value,
        "safe_result": safe.value,
        "lost_updates": lost,
        "corruption_percent": round(lost / expected * 100, 2) if expected else 0,
        "unsafe_correct": unsafe.value == expected,
        "safe_correct": safe.value == expected,
        "n_threads": n_threads,
        "increments": increments,
        "force_preemption": force_preemption,
        "log": log,
    }


def run_trials(
    trials: int = 5,
    n_threads: int = 4,
    increments: int = 2_000,
    force_preemption: bool = True,
) -> dict:
    """Repeat the demo several times to show its non-deterministic nature.

    The result fits a table: trial, result without lock, difference from the
    correct value, and result with lock. Note that the "without lock" column
    differs between trials, whereas the "with lock" column is always the
    same.
    """
    rows = []
    for i in range(trials):
        d = run_demo(
            n_threads=n_threads,
            increments=increments,
            force_preemption=force_preemption,
        )
        rows.append(
            {
                "trial": i + 1,
                "expected": d["expected"],
                "unsafe": d["unsafe_result"],
                "lost": d["lost_updates"],
                "percent": d["corruption_percent"],
                "safe": d["safe_result"],
            }
        )
    broken = sum(1 for r in rows if r["lost"] != 0)
    distinct = len({r["unsafe"] for r in rows})
    return {
        "trials": rows,
        "runs_corrupted": broken,
        "total_runs": trials,
        "distinct_unsafe_results": distinct,
        "conclusion": (
            f"{broken} of {trials} trials without lock produced corrupted data, "
            f"with {distinct} different final values. "
            f"Version with lock was correct in {trials} of {trials} trials."
        ),
    }


if __name__ == "__main__":
    print("=" * 72)
    print("DEMO 1 - RACE CONDITION WITH FORCED PREEMPTION")
    print("=" * 72)
    for line in run_demo(force_preemption=True)["log"]:
        print(line)

    print()
    print("=" * 72)
    print("DEMO 2 - REPEATED 5 TIMES (non-deterministic behavior)")
    print("=" * 72)
    t = run_trials(trials=5)
    print(
        f"{'Trial':>10} {'Expected':>12} {'No Lock':>12} "
        f"{'Lost':>9} {'Broken %':>9} {'With Lock':>12}"
    )
    for r in t["trials"]:
        print(
            f"{r['trial']:>10} {r['expected']:>12,} {r['unsafe']:>12,} "
            f"{r['lost']:>9,} {r['percent']:>8}% {r['safe']:>12,}"
        )
    print()
    print(t["conclusion"])

    print()
    print("=" * 72)
    print("DEMO 3 - NATURAL PREEMPTION (why this bug is dangerous)")
    print("=" * 72)
    nat = run_trials(trials=5, force_preemption=False)
    for r in nat["trials"]:
        status = "BROKEN" if r["lost"] else "passed"
        print(
            f"  trial {r['trial']}: result {r['unsafe']:,} "
            f"of {r['expected']:,} -> {status}"
        )
    print()
    print(f"  {nat['conclusion']}")
    print(
        "  The code in Demo 3 is JUST AS WRONG as in Demo 1. The only difference is\n"
        "  scheduling luck. This is why race conditions can slip through testing."
    )
