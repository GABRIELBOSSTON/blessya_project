"""Producer-Consumer (Bounded Buffer) with semaphores.

Topic: IPC & Classical Problems

The problem: producers create items and put them into a buffer of limited
size; consumers take items out of the buffer. Three things must be
guaranteed at the same time:

  1. A producer must not put an item when the buffer is FULL.
  2. A consumer must not take an item when the buffer is EMPTY.
  3. The buffer must not be accessed by two threads at once (mutual exclusion).

The solution uses three synchronization tools with different roles:

  empty = Semaphore(N)  -> counts EMPTY slots. Producers wait() here.
  full  = Semaphore(0)  -> counts FILLED slots. Consumers wait() here.
  mutex = Lock()        -> protects operations on the buffer itself.

Why semaphores instead of just a lock? A lock can only answer "may I enter
or not", whereas here we need to COUNT (how many empty slots remain). A
semaphore is a counter that can block a thread when its value is zero.

The ORDER of wait() is CRUCIAL. If mutex is acquired BEFORE empty:
      mutex.acquire(); empty.acquire()   <-- WRONG, causes deadlock
a producer can hold the mutex and sleep waiting for an empty slot, while
the consumer that could free a slot cannot enter because the mutex is
held. Both wait for each other forever.
"""

import threading
import time
import math
from dataclasses import dataclass, field


@dataclass
class Event:
    """One event to be shown on the web timeline."""

    t: float
    actor: str
    action: str
    detail: str
    buffer_size: int
    buffer_capacity: int
    items: list[str] = field(default_factory=list)


@dataclass
class Recorder:
    """Event recorder that is safe to use from many threads at once.

    The recorder itself must be thread-safe, so it also uses a lock.
    Without the lock, the `events` list could be corrupted by a race
    condition - exactly the problem being studied here.
    """

    events: list[Event] = field(default_factory=list)
    _lock: threading.Lock = field(default_factory=threading.Lock)
    _start: float = field(default_factory=time.perf_counter)

    def log(
        self, actor: str, action: str, detail: str, size: int, capacity: int,
        items: list[str] | None = None,
    ) -> None:
        with self._lock:
            self.events.append(
                Event(
                    t=round((time.perf_counter() - self._start) * 1000, 2),
                    actor=actor,
                    action=action,
                    detail=detail,
                    buffer_size=size,
                    buffer_capacity=capacity,
                    items=list(items or []),
                )
            )

    def as_list(self) -> list[dict]:
        with self._lock:
            return [vars(e) for e in self.events]


class BoundedBuffer:
    """Bounded buffer protected by semaphores + a mutex."""

    def __init__(self, capacity: int, recorder: Recorder) -> None:
        self.capacity = capacity
        self.items: list[str] = []
        self.rec = recorder
        self.empty = threading.Semaphore(capacity)  # available empty slots
        self.full = threading.Semaphore(0)  # available filled slots
        self.mutex = threading.Lock()  # buffer guard
        self.produced = 0
        self.consumed = 0
        self.blocked_producers = 0
        self.blocked_consumers = 0
        self.cancel = threading.Event()

    def _log(self, who: str, action: str, detail: str) -> None:
        """Called while the buffer mutex is held so order and snapshot stay consistent."""
        self.rec.log(who, action, detail, len(self.items), self.capacity, self.items)

    def _acquire(self, semaphore, who: str, producer: bool) -> None:
        if self.cancel.is_set():
            raise RuntimeError("experiment cancelled")
        if semaphore.acquire(blocking=False):
            return
        with self.mutex:
            if producer:
                self.blocked_producers += 1
            else:
                self.blocked_consumers += 1
            detail = "empty slot not yet available on attempt" if producer else "item not yet available on attempt"
            self._log(who, "BLOCKED", detail)
        while not self.cancel.is_set():
            if semaphore.acquire(timeout=0.05):
                with self.mutex:
                    self._log(who, "RESUMED", "semaphore permit acquired")
                return
        raise RuntimeError("experiment cancelled")

    def put(self, item: str, who: str) -> None:
        self._acquire(self.empty, who, True)
        with self.mutex:  # ---- critical section ----
            self.items.append(item)
            self.produced += 1
            self._log(who, "PRODUCE", f"put {item}")

        self.full.release()  # notify consumers: one new item

    def get(self, who: str) -> str:
        self._acquire(self.full, who, False)
        with self.mutex:  # ---- critical section ----
            item = self.items.pop(0)
            self.consumed += 1
            self._log(who, "CONSUME", f"took {item}")

        self.empty.release()  # notify producers: one empty slot
        return item


def run_demo(
    capacity: int = 4,
    n_producers: int = 2,
    n_consumers: int = 2,
    items_each: int = 6,
    produce_delay: float = 0.004,
    consume_delay: float = 0.010,
    timeout: float = 15,
) -> dict:
    """Run the Producer-Consumer simulation with real threads.

    By default consumers are SLOWER than producers
    (consume_delay > produce_delay). As a result the buffer tends to fill up
    and "producer blocked" events can be observed. Swap the two values to
    see the opposite: consumers waiting because the buffer is empty.
    """
    for label, value, maximum in (("capacity", capacity, 10), ("producers", n_producers, 5),
                                  ("consumers", n_consumers, 5), ("items", items_each, 12)):
        if type(value) is not int or not 1 <= value <= maximum:
            raise ValueError(f"{label} must be an integer from 1 to {maximum}")
    for delay in (produce_delay, consume_delay):
        if type(delay) not in (float, int) or not math.isfinite(delay) or not 0 <= delay <= 0.1:
            raise ValueError("delay must be 0 to 0.1 seconds")
    if type(timeout) not in (float, int) or not math.isfinite(timeout) or timeout <= 0:
        raise ValueError("timeout must be positive and finite")

    rec = Recorder()
    buf = BoundedBuffer(capacity, rec)
    total_target = n_producers * items_each

    def producer(idx: int) -> None:
        name = f"Producer-{idx + 1}"
        for i in range(items_each):
            if buf.cancel.wait(produce_delay):
                return
            buf.put(f"item-{idx + 1}.{i + 1}", name)

    def consumer(idx: int) -> None:
        name = f"Consumer-{idx + 1}"
        # The total item count is split evenly so each consumer knows when to
        # stop and no thread hangs waiting for an item that never comes.
        quota = total_target // n_consumers + (1 if idx < total_target % n_consumers else 0)
        for _ in range(quota):
            if buf.cancel.wait(consume_delay):
                return
            buf.get(name)

    errors: list[str] = []
    error_lock = threading.Lock()

    def worker(fn, idx):
        try:
            fn(idx)
        except Exception as exc:
            with error_lock:
                errors.append(str(exc))
            buf.cancel.set()

    threads = [
        threading.Thread(target=worker, args=(producer, i), name=f"PC-producer-{i}")
        for i in range(n_producers)
    ] + [
        threading.Thread(target=worker, args=(consumer, i), name=f"PC-consumer-{i}")
        for i in range(n_consumers)
    ]

    deadline = time.monotonic() + timeout
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=max(0, deadline - time.monotonic()))

    if any(t.is_alive() for t in threads):
        buf.cancel.set()
        with error_lock:
            errors.append("experiment timeout reached")
    for t in threads:
        t.join(timeout=0.2)

    stuck = [t.name for t in threads if t.is_alive()]
    peak = max((e.buffer_size for e in rec.events), default=0)

    return {
        "capacity": capacity,
        "n_producers": n_producers,
        "n_consumers": n_consumers,
        "items_each": items_each,
        "produced": buf.produced,
        "consumed": buf.consumed,
        "leftover_in_buffer": len(buf.items),
        "peak_buffer_usage": peak,
        "blocked_producers": buf.blocked_producers,
        "blocked_consumers": buf.blocked_consumers,
        "overflow_detected": peak > capacity,
        "balanced": buf.produced == buf.consumed + len(buf.items),
        "stuck_threads": stuck,
        "errors": errors,
        "completed": not errors and not stuck and buf.produced == buf.consumed == total_target,
        "events": rec.as_list(),
        "conclusion": (
            f"Produced {buf.produced}, consumed {buf.consumed}, "
            f"remaining in buffer {len(buf.items)}. "
            f"Peak buffer usage {peak} of capacity {capacity} - "
            f"{'NEVER exceeded capacity' if peak <= capacity else 'EXCEEDED capacity (bug!)'}. "
            f"Producers blocked {buf.blocked_producers} time(s), "
            f"consumers blocked {buf.blocked_consumers} time(s)."
        ),
    }


if __name__ == "__main__":
    print("=" * 72)
    print("PRODUCER-CONSUMER / BOUNDED BUFFER")
    print("=" * 72)
    d = run_demo()
    print(
        f"Buffer capacity  : {d['capacity']}\n"
        f"Producers        : {d['n_producers']} ({d['items_each']} items each)\n"
        f"Consumers        : {d['n_consumers']} (deliberately slower)\n"
    )
    print(f"{'time(ms)':>10}  {'actor':<12} {'action':<10} {'buffer':<9} detail")
    print("-" * 72)
    for e in d["events"]:
        bar = "#" * e["buffer_size"] + "." * (e["buffer_capacity"] - e["buffer_size"])
        print(
            f"{e['t']:>10}  {e['actor']:<12} {e['action']:<10} "
            f"[{bar}] {e['detail']}"
        )
    print("-" * 72)
    print(d["conclusion"])
    if d["stuck_threads"]:
        print(f"WARNING: hanging threads -> {d['stuck_threads']}")
