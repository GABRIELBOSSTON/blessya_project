"""Producer-Consumer (Bounded Buffer) dengan semaphore.

Materi: IPC & Classical Problems

Masalahnya: produsen membuat barang dan menaruhnya di buffer berukuran
terbatas; konsumen mengambil barang dari buffer. Ada tiga hal yang harus
dijamin sekaligus:

  1. Produsen tidak boleh menaruh barang kalau buffer PENUH.
  2. Konsumen tidak boleh mengambil barang kalau buffer KOSONG.
  3. Buffer tidak boleh diakses dua thread sekaligus (mutual exclusion).

Solusinya memakai tiga alat sinkronisasi dengan peran berbeda:

  empty = Semaphore(N)  -> menghitung slot KOSONG. Produsen wait() di sini.
  full  = Semaphore(0)  -> menghitung slot TERISI. Konsumen wait() di sini.
  mutex = Lock()        -> melindungi operasi pada buffer itu sendiri.

Kenapa semaphore, bukan sekadar lock? Karena lock hanya bisa menjawab
"boleh masuk atau tidak", sedangkan di sini kita perlu MENGHITUNG
(berapa slot kosong tersisa). Semaphore adalah penghitung yang bisa
memblokir thread ketika nilainya nol.

URUTAN wait() SANGAT PENTING. Kalau mutex di-wait SEBELUM empty:
      mutex.acquire(); empty.acquire()   <-- SALAH, menyebabkan deadlock
produsen bisa memegang mutex lalu tertidur menunggu slot kosong,
sementara konsumen yang bisa mengosongkan slot tidak dapat masuk karena
mutex sedang dipegang. Keduanya saling menunggu selamanya.
"""

import threading
import time
import math
from dataclasses import dataclass, field


@dataclass
class Event:
    """Satu kejadian untuk ditampilkan sebagai timeline di web."""

    t: float
    actor: str
    action: str
    detail: str
    buffer_size: int
    buffer_capacity: int
    items: list[str] = field(default_factory=list)


@dataclass
class Recorder:
    """Pencatat kejadian yang aman dipakai banyak thread sekaligus.

    Pencatat ini sendiri harus thread-safe, jadi ia pun memakai lock.
    Tanpa lock, daftar `events` bisa rusak oleh race condition - masalah
    yang persis sama dengan yang sedang kita pelajari.
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
    """Buffer terbatas yang dilindungi semaphore + mutex."""

    def __init__(self, capacity: int, recorder: Recorder) -> None:
        self.capacity = capacity
        self.items: list[str] = []
        self.rec = recorder
        self.empty = threading.Semaphore(capacity)  # slot kosong tersedia
        self.full = threading.Semaphore(0)  # slot terisi tersedia
        self.mutex = threading.Lock()  # pelindung buffer
        self.produced = 0
        self.consumed = 0
        self.blocked_producers = 0
        self.blocked_consumers = 0
        self.cancel = threading.Event()

    def _log(self, who: str, action: str, detail: str) -> None:
        """Dipanggil saat mutex buffer dipegang agar urutan/snapshot konsisten."""
        self.rec.log(who, action, detail, len(self.items), self.capacity, self.items)

    def _acquire(self, semaphore, who: str, producer: bool) -> None:
        if self.cancel.is_set():
            raise RuntimeError("percobaan dibatalkan")
        if semaphore.acquire(blocking=False):
            return
        with self.mutex:
            if producer:
                self.blocked_producers += 1
            else:
                self.blocked_consumers += 1
            detail = "slot kosong belum tersedia saat dicoba" if producer else "barang belum tersedia saat dicoba"
            self._log(who, "BLOKIR", detail)
        while not self.cancel.is_set():
            if semaphore.acquire(timeout=0.05):
                with self.mutex:
                    self._log(who, "LANJUT", "izin semaphore diperoleh")
                return
        raise RuntimeError("percobaan dibatalkan")

    def put(self, item: str, who: str) -> None:
        self._acquire(self.empty, who, True)
        with self.mutex:  # ---- critical section ----
            self.items.append(item)
            self.produced += 1
            self._log(who, "PRODUKSI", f"menaruh {item}")

        self.full.release()  # beri tahu konsumen: ada 1 barang baru

    def get(self, who: str) -> str:
        self._acquire(self.full, who, False)
        with self.mutex:  # ---- critical section ----
            item = self.items.pop(0)
            self.consumed += 1
            self._log(who, "KONSUMSI", f"mengambil {item}")

        self.empty.release()  # beri tahu produsen: ada 1 slot kosong
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
    """Jalankan simulasi Producer-Consumer dengan thread sungguhan.

    Secara bawaan konsumen dibuat LEBIH LAMBAT dari produsen
    (consume_delay > produce_delay). Akibatnya buffer cenderung penuh dan
    kejadian "produsen diblokir" bisa diamati. Tukar kedua angka itu untuk
    melihat kebalikannya: konsumen yang menunggu karena buffer kosong.
    """
    for label, value, maximum in (("kapasitas", capacity, 10), ("produsen", n_producers, 5),
                                  ("konsumen", n_consumers, 5), ("barang", items_each, 12)):
        if type(value) is not int or not 1 <= value <= maximum:
            raise ValueError(f"{label} harus bilangan bulat 1 sampai {maximum}")
    for delay in (produce_delay, consume_delay):
        if type(delay) not in (float, int) or not math.isfinite(delay) or not 0 <= delay <= 0.1:
            raise ValueError("jeda harus 0 sampai 0.1 detik")
    if type(timeout) not in (float, int) or not math.isfinite(timeout) or timeout <= 0:
        raise ValueError("batas waktu harus positif dan terhingga")

    rec = Recorder()
    buf = BoundedBuffer(capacity, rec)
    total_target = n_producers * items_each

    def producer(idx: int) -> None:
        name = f"Produsen-{idx + 1}"
        for i in range(items_each):
            if buf.cancel.wait(produce_delay):
                return
            buf.put(f"item-{idx + 1}.{i + 1}", name)

    def consumer(idx: int) -> None:
        name = f"Konsumen-{idx + 1}"
        # Total barang dibagi rata agar setiap konsumen tahu kapan berhenti
        # dan tidak ada thread yang menggantung menunggu barang yang tak ada.
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
        threading.Thread(target=worker, args=(producer, i), name=f"PC-produsen-{i}")
        for i in range(n_producers)
    ] + [
        threading.Thread(target=worker, args=(consumer, i), name=f"PC-konsumen-{i}")
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
            errors.append("batas waktu percobaan tercapai")
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
            f"Diproduksi {buf.produced}, dikonsumsi {buf.consumed}, "
            f"sisa di buffer {len(buf.items)}. "
            f"Isi buffer tertinggi {peak} dari kapasitas {capacity} - "
            f"{'TIDAK PERNAH melebihi kapasitas' if peak <= capacity else 'MELEBIHI kapasitas (bug!)'}. "
            f"Produsen diblokir {buf.blocked_producers} kali, "
            f"konsumen diblokir {buf.blocked_consumers} kali."
        ),
    }


if __name__ == "__main__":
    print("=" * 72)
    print("PRODUCER-CONSUMER / BOUNDED BUFFER")
    print("=" * 72)
    d = run_demo()
    print(
        f"Kapasitas buffer : {d['capacity']}\n"
        f"Produsen         : {d['n_producers']} (masing-masing {d['items_each']} barang)\n"
        f"Konsumen         : {d['n_consumers']} (dibuat lebih lambat)\n"
    )
    print(f"{'waktu(ms)':>10}  {'pelaku':<12} {'aksi':<10} {'buffer':<9} keterangan")
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
        print(f"PERINGATAN: thread menggantung -> {d['stuck_threads']}")
