"""Demo penjadwalan proses untuk terminal.

Jalankan:  py -m src.scheduling.demo

Menampilkan Gantt chart ASCII dan tabel metrik, cocok untuk di-screenshot
dan dimasukkan ke laporan.
"""

from .algorithms import compare_all
from .models import Process, ScheduleResult

# Data contoh yang dipakai di seluruh laporan agar perbandingannya adil:
# semua algoritma diuji pada himpunan proses yang SAMA.
SAMPLE = [
    Process("P1", arrival=0, burst=8, priority=3),
    Process("P2", arrival=1, burst=4, priority=1),
    Process("P3", arrival=2, burst=9, priority=4),
    Process("P4", arrival=3, burst=5, priority=2),
]

SCALE = 3  # lebar satu satuan waktu di Gantt chart ASCII


def print_input(procs: list[Process]) -> None:
    print("DATA MASUKAN")
    print("-" * 56)
    print(f"{'Proses':<8} {'Arrival':>8} {'Burst':>7} {'Prioritas':>10}")
    for p in procs:
        print(f"{p.pid:<8} {p.arrival:>8} {p.burst:>7} {p.priority:>10}")
    print(f"\nTotal burst time: {sum(p.burst for p in procs)}")


def print_gantt(res: ScheduleResult) -> None:
    """Gambar Gantt chart dengan karakter ASCII."""
    if not res.timeline:
        return

    top = "+"
    mid = "|"
    for s in res.timeline:
        w = max(len(s.pid) + 2, s.duration * SCALE)
        top += "-" * w + "+"
        mid += s.pid.center(w) + "|"

    print(top)
    print(mid)
    print(top)

    # Penanda waktu di bawah chart: batas awal/akhir setiap segmen.
    bounds = [res.timeline[0].start] + [s.end for s in res.timeline]
    print("waktu: " + " -> ".join(str(b) for b in bounds))


def print_metrics(res: ScheduleResult) -> None:
    print(
        f"{'Proses':<8} {'Arr':>5} {'Burst':>6} {'Selesai':>8} "
        f"{'Turnaround':>11} {'Waiting':>8} {'Response':>9}"
    )
    print("-" * 60)
    for m in res.metrics:
        print(
            f"{m.pid:<8} {m.arrival:>5} {m.burst:>6} {m.completion:>8} "
            f"{m.turnaround:>11} {m.waiting:>8} {m.response:>9}"
        )
    print("-" * 60)
    print(
        f"{'RATA-RATA':<8} {'':>5} {'':>6} {'':>8} "
        f"{res.avg_turnaround:>11} {res.avg_waiting:>8} {res.avg_response:>9}"
    )
    print(
        f"\nUtilisasi CPU: {res.cpu_utilization}%   "
        f"Total waktu: {res.total_time}   "
        f"Context switch: {res.context_switches}"
    )


def main() -> None:
    print("=" * 72)
    print("SIMULASI PENJADWALAN PROSES (CPU SCHEDULING)")
    print("=" * 72)
    print()
    print_input(SAMPLE)

    results = compare_all(SAMPLE, quantum=3)

    for res in results:
        print()
        print("=" * 72)
        print(res.algorithm)
        print("=" * 72)
        print("\nGantt Chart:")
        print_gantt(res)
        print()
        print_metrics(res)

        print("\nLangkah keputusan scheduler:")
        for line in res.log[:14]:
            print(f"  {line}")
        if len(res.log) > 14:
            print(f"  ... ({len(res.log) - 14} baris lagi)")

    # ---------------- Tabel perbandingan akhir ----------------
    print()
    print("=" * 72)
    print("TABEL PERBANDINGAN SELURUH ALGORITMA")
    print("=" * 72)
    print(
        f"{'Algoritma':<46} {'AvgWait':>8} {'AvgTA':>8} "
        f"{'AvgResp':>8} {'CS':>4}"
    )
    print("-" * 72)
    for r in results:
        print(
            f"{r.algorithm[:46]:<46} {r.avg_waiting:>8} {r.avg_turnaround:>8} "
            f"{r.avg_response:>8} {r.context_switches:>4}"
        )

    best_w = min(results, key=lambda r: r.avg_waiting)
    best_r = min(results, key=lambda r: r.avg_response)
    print()
    print("ANALISIS")
    print("-" * 72)
    print(
        f"Average waiting time terkecil : {best_w.algorithm} ({best_w.avg_waiting})"
    )
    print(
        f"Average response time terkecil: {best_r.algorithm} ({best_r.avg_response})"
    )
    print(
        "\nTidak ada algoritma yang terbaik di semua ukuran sekaligus.\n"
        "SJF/SRTF unggul pada waiting time, tetapi berisiko starvation dan\n"
        "butuh burst time yang sebenarnya tidak diketahui di awal.\n"
        "Round Robin memberi response time merata sehingga terasa responsif\n"
        "untuk pengguna, dengan biaya context switch yang lebih banyak.\n"
        "Pemilihan algoritma karena itu bergantung pada tujuan sistem:\n"
        "throughput (batch) atau keresponsifan (interaktif)."
    )

    # ---------------- Pengaruh quantum pada Round Robin ----------------
    from .algorithms import round_robin

    print()
    print("=" * 72)
    print("PENGARUH TIME QUANTUM PADA ROUND ROBIN")
    print("=" * 72)
    print(f"{'Quantum':>8} {'AvgWait':>9} {'AvgResp':>9} {'ContextSwitch':>15}")
    print("-" * 72)
    for q in (1, 2, 3, 5, 8, 12):
        r = round_robin(SAMPLE, quantum=q)
        print(
            f"{q:>8} {r.avg_waiting:>9} {r.avg_response:>9} "
            f"{r.context_switches:>15}"
        )
    print(
        "\nTerlihat trade-off intinya: quantum kecil membuat response time\n"
        "bagus tapi context switch melonjak; quantum besar mengurangi\n"
        "context switch tapi perilakunya mendekati FCFS."
    )


if __name__ == "__main__":
    main()
