"""Dining Philosophers - bridging the IPC and Deadlock topics.

Topic: IPC & Classical Problems + Deadlock

Five philosophers sit around a round table. There is one fork between
every two philosophers, so there are 5 forks. To eat, a philosopher needs
TWO forks: the left fork and the right fork.

This problem is the standard example because it shows all four deadlock
conditions (the Coffman conditions) at once:

  1. Mutual exclusion - a fork can be held by only one philosopher.
  2. Hold and wait    - a philosopher holds the left fork while waiting for the right.
  3. No preemption    - a fork cannot be taken away; it must be released voluntarily.
  4. Circular wait    - F1 waits for F2, F2 waits for F3, ... F5 waits for F1.

This module provides three strategies to compare:

  "naive"      - everyone takes the left fork first, then the right. CAN DEADLOCK.
  "ordering"   - everyone takes the LOWER-numbered fork first. Breaks circular
                 wait, so deadlock is impossible. (Prevention)
  "waiter"     - a waiter allows only 4 philosophers to try eating at the
                 same time. Effectively breaks hold-and-wait.
                 (Avoidance / resource limiting)

Note: the "naive" strategy runs with a timeout. If time runs out while
philosophers are still waiting, that is proof a deadlock occurred.
"""

import threading
import time
from dataclasses import dataclass, field

N = 5
STRATEGIES = ("naive", "ordering", "waiter")


@dataclass
class Recorder:
    events: list[dict] = field(default_factory=list)
    _lock: threading.Lock = field(default_factory=threading.Lock)
    _start: float = field(default_factory=time.perf_counter)

    def log(self, who: str, action: str, detail: str) -> None:
        with self._lock:
            self.events.append(
                {
                    "t": round((time.perf_counter() - self._start) * 1000, 2),
                    "who": who,
                    "action": action,
                    "detail": detail,
                }
            )

    def snapshot(self) -> list[dict]:
        with self._lock:
            return list(self.events)


def run_strategy(
    strategy: str = "naive",
    meals: int = 3,
    timeout: float = 3.0,
    think: float = 0.002,
    eat: float = 0.004,
) -> dict:
    """Run one strategy and report whether a deadlock occurred."""
    if strategy not in STRATEGIES:
        raise ValueError(f"strategy must be one of {STRATEGIES}")

    rec = Recorder()
    forks = [threading.Lock() for _ in range(N)]
    # Waiter: only N-1 philosophers may "sit and try to eat" at the same time.
    # With 4 people competing for 5 forks, at least one can always get two
    # forks, so the system can never be completely stuck.
    waiter = threading.Semaphore(N - 1)

    eaten = [0] * N
    waiting_for: dict[int, int | None] = {i: None for i in range(N)}
    holding: dict[int, list[int]] = {i: [] for i in range(N)}
    state_lock = threading.Lock()
    stop = threading.Event()

    def acquire(phil: int, fork: int) -> bool:
        """Try to take one fork. Return False if time has run out."""
        with state_lock:
            waiting_for[phil] = fork
        rec.log(f"F{phil + 1}", "REQUEST", f"waiting for fork {fork + 1}")
        while not stop.is_set():
            if forks[fork].acquire(timeout=0.05):
                with state_lock:
                    waiting_for[phil] = None
                    holding[phil].append(fork)
                rec.log(f"F{phil + 1}", "TAKE", f"holding fork {fork + 1}")
                return True
        return False

    def release_all(phil: int) -> None:
        with state_lock:
            held = holding[phil][:]
            holding[phil].clear()
            waiting_for[phil] = None
        for f in held:
            forks[f].release()
        if held:
            rec.log(
                f"F{phil + 1}",
                "RELEASE",
                "releasing forks " + ", ".join(str(f + 1) for f in held),
            )

    def philosopher(phil: int) -> None:
        left, right = phil, (phil + 1) % N
        for _ in range(meals):
            if stop.is_set():
                return
            rec.log(f"F{phil + 1}", "THINK", "thinking")
            time.sleep(think)

            if strategy == "waiter":
                waiter.acquire()
                rec.log(f"F{phil + 1}", "PERMIT", "waiter granted permission to attempt eating")

            if strategy == "ordering":
                # Key idea: order requests by fork number. Because ALL
                # philosophers take the lower number first, a circular
                # wait can never form.
                first, second = min(left, right), max(left, right)
            else:
                # naive & waiter: left first, then right.
                first, second = left, right

            if not acquire(phil, first):
                return
            # This pause increases the chance that every philosopher already
            # holds the first fork before requesting the second - which is
            # the guaranteed deadlock condition for the naive strategy.
            time.sleep(0.003)
            if not acquire(phil, second):
                release_all(phil)
                return

            rec.log(f"F{phil + 1}", "EAT", "eating with 2 forks")
            time.sleep(eat)
            with state_lock:
                eaten[phil] += 1
            release_all(phil)

            if strategy == "waiter":
                waiter.release()

    threads = [
        threading.Thread(target=philosopher, args=(i,), name=f"F{i + 1}")
        for i in range(N)
    ]
    start = time.perf_counter()
    for t in threads:
        t.start()

    for t in threads:
        t.join(timeout=max(0.05, timeout - (time.perf_counter() - start)))

    alive = [t.name for t in threads if t.is_alive()]
    deadlocked = bool(alive)

    # Snapshot of the stuck state: who holds what, who waits for what.
    # The Indonesian keys (memegang/menunggu/sudah_makan) are kept for compatibility.
    with state_lock:
        snapshot = {
            f"F{i + 1}": {
                "holding": [f + 1 for f in holding[i]],
                "waiting_for": (waiting_for[i] + 1) if waiting_for[i] is not None else None,
                "meals_eaten": eaten[i],
                "memegang": [f + 1 for f in holding[i]],
                "menunggu": (waiting_for[i] + 1) if waiting_for[i] is not None else None,
                "sudah_makan": eaten[i],
            }
            for i in range(N)
        }

    cycle = _find_cycle(holding, waiting_for) if deadlocked else []

    stop.set()
    for t in threads:
        t.join(timeout=2)

    labels = {
        "naive": "Naive (left first, then right)",
        "ordering": "Resource Ordering (lower-numbered fork first)",
        "waiter": f"Waiter / Semaphore (max {N - 1} philosophers at once)",
    }

    if deadlocked:
        conclusion = (
            f"DEADLOCK OCCURRED. Stuck philosophers: {', '.join(alive)}. "
            f"Total meals eaten only {sum(eaten)} of target {N * meals}."
        )
        if cycle:
            conclusion += " Circular wait: " + " -> ".join(cycle)
    else:
        conclusion = (
            f"NO DEADLOCK. All {N} philosophers successfully ate "
            f"{meals} time(s) (total {sum(eaten)} of {N * meals})."
        )

    return {
        "strategy": strategy,
        "strategy_label": labels[strategy],
        "meals_target": meals,
        "deadlocked": deadlocked,
        "stuck_philosophers": alive,
        "meals_eaten": {f"F{i + 1}": eaten[i] for i in range(N)},
        "total_eaten": sum(eaten),
        "state_snapshot": snapshot,
        "cycle": cycle,
        "events": rec.snapshot(),
        "conclusion": conclusion,
    }


def _find_cycle(holding: dict, waiting_for: dict) -> list[str]:
    """Find the circular wait in the wait-for graph during a deadlock.

    Graph shape: philosopher A -> philosopher B if A waits for a fork that
    B currently holds. A cycle in this graph proves circular wait, the
    fourth Coffman condition.
    """
    owner = {f: p for p, fs in holding.items() for f in fs}
    edges = {}
    for phil, fork in waiting_for.items():
        if fork is not None and fork in owner and owner[fork] != phil:
            edges[phil] = owner[fork]

    for start in edges:
        path = [start]
        cur = start
        for _ in range(len(edges) + 1):
            cur = edges.get(cur)
            if cur is None:
                break
            if cur in path:
                loop = path[path.index(cur):] + [cur]
                return [f"F{p + 1}" for p in loop]
            path.append(cur)
    return []


def compare_all(meals: int = 3, timeout: float = 3.0) -> dict:
    """Run all three strategies for the comparison table."""
    results = [run_strategy(s, meals=meals, timeout=timeout) for s in STRATEGIES]
    return {
        "results": results,
        "summary": [
            {
                "strategy": r["strategy"],
                "label": r["strategy_label"],
                "deadlocked": r["deadlocked"],
                "total_eaten": r["total_eaten"],
                "target": N * meals,
            }
            for r in results
        ],
    }


if __name__ == "__main__":
    print("=" * 72)
    print("DINING PHILOSOPHERS - 5 philosophers, 5 forks")
    print("=" * 72)
    for strat in STRATEGIES:
        r = run_strategy(strat)
        print()
        print(f"STRATEGY: {r['strategy_label']}")
        print("-" * 72)
        for who, st in r["state_snapshot"].items():
            held = ", ".join(str(f) for f in st["memegang"]) or "-"
            waits = str(st["menunggu"]) if st["menunggu"] else "-"
            print(
                f"  {who}: holding {held:<10} waiting {waits:<5} "
                f"meals eaten {st['sudah_makan']}x"
            )
        print(f"  => {r['conclusion']}")

    print()
    print("=" * 72)
    print("SUMMARY")
    print("=" * 72)
    c = compare_all()
    print(f"{'Strategy':<46} {'Deadlock':<10} {'Meals eaten'}")
    print("-" * 72)
    for s in c["summary"]:
        print(
            f"{s['label']:<46} {'YES' if s['deadlocked'] else 'no':<10} "
            f"{s['total_eaten']}/{s['target']}"
        )
