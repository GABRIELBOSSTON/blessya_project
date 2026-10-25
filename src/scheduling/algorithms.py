"""Lima algoritma penjadwalan CPU.

Setiap fungsi menerima daftar Process dan mengembalikan ScheduleResult.
Selain hasil angka, setiap algoritma juga menulis `log`: penjelasan
langkah-per-langkah keputusan scheduler. Log inilah yang membuat program
ini bersifat edukatif, bukan sekadar menampilkan hasil akhir.

Materi: Process Scheduling (non-preemptive & preemptive)
"""

from .models import (
    Process,
    ScheduleResult,
    Segment,
    build_metrics,
    merge_adjacent,
    validate_processes,
    count_context_switches,
)


def fcfs(processes: list[Process]) -> ScheduleResult:
    """First Come First Served - non-preemptive.

    Proses dilayani murni urut waktu kedatangan. Sederhana dan adil secara
    urutan, tapi rawan "convoy effect": satu proses panjang di depan
    membuat semua proses pendek di belakangnya menunggu lama.
    """
    validate_processes(processes)
    res = ScheduleResult(algorithm="FCFS (First Come First Served)")
    queue = sorted(processes, key=lambda p: (p.arrival, p.pid))
    clock = 0

    for p in queue:
        if clock < p.arrival:
            res.timeline.append(Segment("IDLE", clock, p.arrival))
            res.log.append(
                f"t={clock}: no process ready. CPU idle until t={p.arrival}."
            )
            clock = p.arrival
        res.log.append(
            f"t={clock}: {p.pid} runs (arrived earliest, burst={p.burst})."
        )
        res.timeline.append(Segment(p.pid, clock, clock + p.burst))
        clock += p.burst
        res.log.append(f"t={clock}: {p.pid} finished.")

    res.metrics = build_metrics(processes, res.timeline)
    res.context_switches = count_context_switches(res.timeline)
    return res


def sjf(processes: list[Process]) -> ScheduleResult:
    """Shortest Job First - non-preemptive.

    Dari semua proses yang SUDAH tiba, pilih yang burst-nya paling pendek.
    Optimal untuk average waiting time jika semua pekerjaan siap bersamaan;
    kedatangan berbeda memerlukan asumsi tambahan. Algoritma ini
    tidak bisa dipakai apa adanya di sistem nyata karena burst time proses
    tidak diketahui sebelum proses dijalankan (hanya bisa diprediksi).
    Risiko lain: starvation untuk proses yang burst-nya besar.
    """
    validate_processes(processes)
    res = ScheduleResult(algorithm="SJF (Shortest Job First)")
    all_procs = sorted(processes, key=lambda p: (p.arrival, p.pid))
    done: set[str] = set()
    clock = 0

    while len(done) < len(all_procs):
        ready = [p for p in all_procs if p.arrival <= clock and p.pid not in done]
        if not ready:
            nxt = min(p.arrival for p in all_procs if p.pid not in done)
            res.timeline.append(Segment("IDLE", clock, nxt))
            res.log.append(f"t={clock}: no process has arrived. CPU idle until t={nxt}.")
            clock = nxt
            continue

        chosen = min(ready, key=lambda p: (p.burst, p.arrival, p.pid))
        others = ", ".join(
            f"{p.pid}(burst={p.burst})" for p in ready if p.pid != chosen.pid
        )
        res.log.append(
            f"t={clock}: ready queue = [{', '.join(p.pid for p in ready)}]. "
            f"{chosen.pid} chosen because burst={chosen.burst} is shortest"
            + (f"; beats {others}." if others else ".")
        )
        res.timeline.append(Segment(chosen.pid, clock, clock + chosen.burst))
        clock += chosen.burst
        res.log.append(f"t={clock}: {chosen.pid} finished.")
        done.add(chosen.pid)

    res.metrics = build_metrics(processes, res.timeline)
    res.context_switches = count_context_switches(res.timeline)
    return res


def srtf(processes: list[Process]) -> ScheduleResult:
    """Shortest Remaining Time First - versi preemptive dari SJF.

    Disimulasikan tick-per-tick (1 satuan waktu). Pada setiap tick scheduler
    memeriksa ulang: adakah proses dengan remaining time lebih kecil dari
    yang sedang jalan? Kalau ada, proses yang berjalan di-preempt.
    """
    validate_processes(processes)
    res = ScheduleResult(algorithm="SRTF (Shortest Remaining Time First, preemptive)")
    remaining = {p.pid: p.burst for p in processes}
    by_pid = {p.pid: p for p in processes}
    raw: list[Segment] = []
    clock = 0
    running: str | None = None
    total_burst = sum(p.burst for p in processes)
    executed = 0

    while executed < total_burst:
        ready = [
            pid
            for pid, left in remaining.items()
            if left > 0 and by_pid[pid].arrival <= clock
        ]
        if not ready:
            raw.append(Segment("IDLE", clock, clock + 1))
            clock += 1
            running = None
            continue

        chosen = min(ready, key=lambda pid: (remaining[pid], by_pid[pid].arrival, pid))
        if running is not None and chosen != running and remaining.get(running, 0) > 0:
            res.context_switches += 1
            res.log.append(
                f"t={clock}: {running} PREEMPTED by {chosen} "
                f"(remaining {chosen}={remaining[chosen]} less than "
                f"remaining {running}={remaining[running]})."
            )
        elif running != chosen:
            res.log.append(
                f"t={clock}: {chosen} starts running (remaining burst={remaining[chosen]})."
            )

        running = chosen
        raw.append(Segment(chosen, clock, clock + 1))
        remaining[chosen] -= 1
        clock += 1
        executed += 1
        if remaining[chosen] == 0:
            res.log.append(f"t={clock}: {chosen} finished.")
            running = None

    res.timeline = merge_adjacent(raw)
    res.metrics = build_metrics(processes, res.timeline)
    res.context_switches = count_context_switches(res.timeline)
    return res


def round_robin(processes: list[Process], quantum: int = 2) -> ScheduleResult:
    """Round Robin - preemptive berbasis time quantum.

    Setiap proses mendapat CPU maksimal `quantum` satuan waktu, lalu
    dipindahkan ke belakang antrian. Inilah algoritma yang dipakai sistem
    interaktif: response time-nya merata, tidak ada proses yang menunggu
    tanpa batas.

    Pemilihan quantum adalah trade-off inti:
      - quantum terlalu besar -> perilakunya kembali seperti FCFS
      - quantum terlalu kecil -> overhead context switch mendominasi
    """
    validate_processes(processes)
    if type(quantum) is not int or quantum <= 0:
        raise ValueError("quantum must be a positive integer > 0")

    res = ScheduleResult(algorithm=f"Round Robin (quantum={quantum})")
    remaining = {p.pid: p.burst for p in processes}
    arrivals = sorted(processes, key=lambda p: (p.arrival, p.pid))
    queue: list[str] = []
    raw: list[Segment] = []
    clock = 0
    idx = 0

    def admit(upto: int) -> None:
        """Masukkan semua proses yang tiba sampai waktu `upto` ke antrian."""
        nonlocal idx
        while idx < len(arrivals) and arrivals[idx].arrival <= upto:
            queue.append(arrivals[idx].pid)
            idx += 1

    admit(clock)
    while queue or idx < len(arrivals):
        if not queue:
            nxt = arrivals[idx].arrival
            raw.append(Segment("IDLE", clock, nxt))
            res.log.append(f"t={clock}: queue empty. CPU idle until t={nxt}.")
            clock = nxt
            admit(clock)
            continue

        pid = queue.pop(0)
        slice_len = min(quantum, remaining[pid])
        res.log.append(
            f"t={clock}: {pid} gets CPU for {slice_len} "
            f"(remaining burst={remaining[pid]}, quantum={quantum})."
        )
        raw.append(Segment(pid, clock, clock + slice_len))
        clock += slice_len
        remaining[pid] -= slice_len

        # Proses yang tiba SELAMA slice ini masuk antrian lebih dulu, baru
        # proses yang habis quantum-nya dimasukkan ke belakang. Urutan ini
        # penting: kalau dibalik, hasil Gantt chart akan berbeda.
        admit(clock)
        if remaining[pid] > 0:
            queue.append(pid)
            res.context_switches += 1
            res.log.append(
                f"t={clock}: quantum for {pid} expired, remaining {remaining[pid]}. "
                f"Moved to back of queue -> [{', '.join(queue)}]."
            )
        else:
            res.log.append(f"t={clock}: {pid} finished.")

    res.timeline = raw
    res.metrics = build_metrics(processes, res.timeline)
    res.context_switches = count_context_switches(res.timeline)
    return res


def priority(processes: list[Process], preemptive: bool = False) -> ScheduleResult:
    """Priority Scheduling. Angka prioritas lebih kecil = lebih penting.

    Masalah klasiknya adalah starvation: proses prioritas rendah bisa tidak
    pernah dapat CPU. Solusi umumnya aging, yaitu prioritas proses yang lama
    menunggu dinaikkan perlahan. Aging TIDAK diimplementasikan di sini agar
    efek starvation-nya bisa diamati dan dibahas di laporan.
    """
    validate_processes(processes)
    label = "Priority (preemptive)" if preemptive else "Priority (non-preemptive)"
    res = ScheduleResult(algorithm=label)
    remaining = {p.pid: p.burst for p in processes}
    by_pid = {p.pid: p for p in processes}
    raw: list[Segment] = []
    clock = 0
    running: str | None = None
    left = sum(p.burst for p in processes)

    while left > 0:
        ready = [
            pid for pid, r in remaining.items() if r > 0 and by_pid[pid].arrival <= clock
        ]
        if not ready:
            raw.append(Segment("IDLE", clock, clock + 1))
            clock += 1
            continue

        chosen = min(
            ready, key=lambda pid: (by_pid[pid].priority, by_pid[pid].arrival, pid)
        )
        if preemptive:
            if (
                running is not None
                and running != chosen
                and remaining.get(running, 0) > 0
            ):
                res.context_switches += 1
                res.log.append(
                    f"t={clock}: {running} preempted by {chosen} "
                    f"(priority {by_pid[chosen].priority} more important than "
                    f"{by_pid[running].priority})."
                )
            running = chosen
            raw.append(Segment(chosen, clock, clock + 1))
            remaining[chosen] -= 1
            clock += 1
            left -= 1
            if remaining[chosen] == 0:
                res.log.append(f"t={clock}: {chosen} finished.")
                running = None
        else:
            res.log.append(
                f"t={clock}: {chosen} runs to completion "
                f"(priority={by_pid[chosen].priority}, burst={remaining[chosen]})."
            )
            dur = remaining[chosen]
            raw.append(Segment(chosen, clock, clock + dur))
            clock += dur
            left -= dur
            remaining[chosen] = 0
            res.context_switches += 1
            res.log.append(f"t={clock}: {chosen} finished.")

    res.timeline = merge_adjacent(raw)
    res.metrics = build_metrics(processes, res.timeline)
    if not preemptive:
        res.context_switches = max(0, res.context_switches - 1)
    res.context_switches = count_context_switches(res.timeline)
    return res


ALGORITHMS = {
    "fcfs": fcfs,
    "sjf": sjf,
    "srtf": srtf,
    "rr": round_robin,
    "priority": priority,
}


def run(name: str, processes: list[Process], **kwargs) -> ScheduleResult:
    """Jalankan satu algoritma berdasarkan namanya. Dipakai oleh server web."""
    key = name.lower()
    if key not in ALGORITHMS:
        raise ValueError(
            f"Algorithm '{name}' not recognized. Options: {', '.join(ALGORITHMS)}"
        )
    return ALGORITHMS[key](processes, **kwargs)


def compare_all(processes: list[Process], quantum: int = 2) -> list[ScheduleResult]:
    """Jalankan semua algoritma pada data yang sama, untuk tabel perbandingan."""
    return [
        fcfs(processes),
        sjf(processes),
        srtf(processes),
        round_robin(processes, quantum=quantum),
        priority(processes, preemptive=False),
        priority(processes, preemptive=True),
    ]
