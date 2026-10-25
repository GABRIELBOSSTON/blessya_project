"""Pembuktian race condition dengan thread sungguhan.

Materi: Process and Threads + IPC (critical section, mutual exclusion)

Ini demo paling penting untuk memahami kenapa sinkronisasi dibutuhkan.
Beberapa thread menaikkan satu variabel bersama sebanyak N kali. Secara
matematika hasilnya harus n_threads * N. Tanpa lock, hasilnya lebih kecil.

Penyebabnya: operasi `counter += 1` TIDAK atomic. Di tingkat mesin ia
terdiri dari tiga langkah terpisah:
    1. READ   : baca nilai counter dari memori ke register
    2. MODIFY : tambah 1 di register
    3. WRITE  : tulis kembali ke memori

Kalau thread A disela tepat setelah langkah 1, lalu thread B menyelesaikan
seluruh 1-2-3, maka ketika A melanjutkan ia menulis nilai lama+1 dan
menimpa hasil kerja B. Satu increment hilang. Inilah "lost update".

CATATAN PENTING TENTANG METODE (jangan dihilangkan dari laporan)
---------------------------------------------------------------
Di CPython ada Global Interpreter Lock (GIL) yang membuat perpindahan
thread relatif jarang. Akibatnya, pada loop yang sangat sempit race
condition sering TIDAK muncul walau bug-nya ada. Karena itu kelas
`UnsafeCounter` memanggil `time.sleep(0)` di antara READ dan WRITE.

`time.sleep(0)` tidak menidurkan apa pun - ia hanya memaksa thread
menyerahkan CPU pada titik itu. Jadi kita TIDAK menambah bug baru:
kita hanya mengatur agar preemption terjadi tepat di saat terburuk,
sehingga bug yang memang sudah ada menjadi teramati setiap kali.

Justru inilah sifat paling berbahaya dari race condition: ia bergantung
pada waktu. Tanpa paksaan ini program yang SALAH bisa lulus pengujian
ratusan kali, lalu rusak di komputer lain atau saat beban tinggi.
Fungsi `run_demo(force_preemption=False)` menunjukkan hal itu.
"""

import sys
import threading
import time


class UnsafeCounter:
    """Counter tanpa proteksi. Sengaja dibuat rawan."""

    def __init__(self, force_preemption: bool = True) -> None:
        self.value = 0
        self.force_preemption = force_preemption

    def increment(self) -> None:
        current = self.value  # 1. READ
        if self.force_preemption:
            # Menyerahkan CPU tepat di tengah critical section.
            # Di sinilah thread lain menyelipkan increment-nya dan
            # hasil kerjanya akan tertimpa oleh baris WRITE di bawah.
            time.sleep(0)
        current = current + 1  # 2. MODIFY
        self.value = current  # 3. WRITE


class SafeCounter:
    """Counter yang sama, dilindungi mutex (Lock).

    Lock menjamin mutual exclusion: hanya satu thread boleh berada di
    critical section pada satu waktu. Thread lain yang mencoba masuk akan
    diblokir sampai lock dilepas.

    Perhatikan bahwa `time.sleep(0)` tetap ada di dalam critical section.
    Artinya thread MASIH berpindah di tengah operasi, tapi hasilnya tetap
    benar. Ini bukti bahwa yang menyelamatkan kita adalah lock-nya,
    bukan keberuntungan waktu.
    """

    def __init__(self, force_preemption: bool = True) -> None:
        self.value = 0
        self.force_preemption = force_preemption
        self._lock = threading.Lock()

    def increment(self) -> None:
        with self._lock:  # ---- masuk critical section ----
            current = self.value
            if self.force_preemption:
                time.sleep(0)
            current = current + 1
            self.value = current
        # ---- keluar critical section, lock otomatis dilepas ----


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
    """Jalankan versi tidak aman dan versi aman, lalu bandingkan.

    force_preemption=True  -> bug muncul hampir selalu (untuk demonstrasi)
    force_preemption=False -> bug sering tidak muncul walau kode tetap salah
                              (untuk menunjukkan bahaya bug non-deterministik)
    """
    expected = n_threads * increments
    log: list[str] = []
    original = sys.getswitchinterval()

    log.append(
        f"Menjalankan {n_threads} thread, masing-masing {increments:,} increment "
        f"pada SATU variabel bersama."
    )
    log.append(f"Nilai yang benar secara matematis: {expected:,}")
    log.append(
        "Mode preemption: "
        + (
            "DIPAKSA (yield di tengah critical section)"
            if force_preemption
            else "ALAMI (bergantung penjadwalan GIL)"
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
    log.append(f"TANPA LOCK  : hasil = {unsafe.value:,}")
    if lost > 0:
        log.append(
            f"              {lost:,} increment HILANG "
            f"({lost / expected * 100:.2f}% data rusak)."
        )
        log.append(
            "              Penyebab: dua thread membaca nilai yang sama, "
            "lalu saling menimpa hasil (lost update)."
        )
    else:
        log.append(
            "              Kali ini hasilnya kebetulan benar. Kodenya TETAP "
            "salah - race condition hanya belum terpicu."
        )

    log.append("")
    log.append(f"DENGAN LOCK : hasil = {safe.value:,}")
    log.append(
        "              Tepat, walaupun thread tetap berpindah di tengah "
        "operasi. Mutex memaksa increment berjalan satu per satu."
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
    """Ulangi demo beberapa kali untuk membuktikan sifat non-deterministik.

    Hasilnya cocok dijadikan tabel di laporan: kolom percobaan, hasil tanpa
    lock, selisih dari nilai benar, dan hasil dengan lock. Perhatikan bahwa
    kolom "tanpa lock" berbeda-beda tiap percobaan, sedangkan kolom "dengan
    lock" selalu sama.
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
            f"{broken} dari {trials} percobaan tanpa lock menghasilkan data rusak, "
            f"dengan {distinct} nilai akhir yang berbeda-beda. "
            f"Versi dengan lock benar di {trials} dari {trials} percobaan."
        ),
    }


if __name__ == "__main__":
    print("=" * 72)
    print("DEMO 1 - RACE CONDITION DENGAN PREEMPTION DIPAKSA")
    print("=" * 72)
    for line in run_demo(force_preemption=True)["log"]:
        print(line)

    print()
    print("=" * 72)
    print("DEMO 2 - PENGULANGAN 5 KALI (sifat non-deterministik)")
    print("=" * 72)
    t = run_trials(trials=5)
    print(
        f"{'Percobaan':>10} {'Seharusnya':>12} {'Tanpa Lock':>12} "
        f"{'Hilang':>9} {'Rusak %':>9} {'Dengan Lock':>12}"
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
    print("DEMO 3 - PREEMPTION ALAMI (kenapa bug ini berbahaya)")
    print("=" * 72)
    nat = run_trials(trials=5, force_preemption=False)
    for r in nat["trials"]:
        status = "RUSAK" if r["lost"] else "lolos"
        print(
            f"  percobaan {r['trial']}: hasil {r['unsafe']:,} "
            f"dari {r['expected']:,} -> {status}"
        )
    print()
    print(f"  {nat['conclusion']}")
    print(
        "  Kode di Demo 3 SAMA SALAHNYA dengan Demo 1. Bedanya hanya keberuntungan\n"
        "  penjadwalan. Inilah sebabnya race condition bisa lolos pengujian."
    )
