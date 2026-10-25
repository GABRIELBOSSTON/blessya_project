"""Uji kebenaran algoritma penjadwalan.

Jalankan:  py tests/test_scheduling.py

Nilai yang diharapkan di bawah dihitung manual terlebih dahulu (lihat
docs/PERHITUNGAN-MANUAL.md). Tujuannya membuktikan program tidak hanya
"mengeluarkan angka", tapi mengeluarkan angka yang BENAR.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.scheduling import algorithms as A
from src.scheduling.models import Process

passed = 0
failed = 0


def check(label: str, got, want) -> None:
    global passed, failed
    if got == want:
        passed += 1
        print(f"  LULUS  {label}: {got}")
    else:
        failed += 1
        print(f"  GAGAL  {label}: dapat {got}, seharusnya {want}")


def gantt(result) -> str:
    return " ".join(f"{s.pid}({s.start}-{s.end})" for s in result.timeline)


print("=" * 70)
print("KASUS 1 - FCFS, convoy effect")
print("=" * 70)
# P1 burst 24 datang pertama, menahan dua proses pendek di belakangnya.
ps = [Process("P1", 0, 24), Process("P2", 0, 3), Process("P3", 0, 3)]
r = A.fcfs(ps)
print("  gantt:", gantt(r))
# P1 tunggu 0, P2 tunggu 24, P3 tunggu 27 -> (0+24+27)/3 = 17.0
check("FCFS avg waiting", r.avg_waiting, 17.0)
check("FCFS total time", r.total_time, 30)

r = A.sjf(ps)
print("  gantt:", gantt(r))
# Urutan jadi P2(3) P3(3) P1(24): tunggu 6 + 0 + 3 = 9/3 = 3.0
check("SJF avg waiting", r.avg_waiting, 3.0)
print("  -> SJF memperbaiki avg waiting 17.0 menjadi 3.0 pada data yang sama.")

print()
print("=" * 70)
print("KASUS 2 - SRTF preemption")
print("=" * 70)
ps = [Process("P1", 0, 8), Process("P2", 1, 4), Process("P3", 2, 9), Process("P4", 3, 5)]
r = A.srtf(ps)
print("  gantt:", gantt(r))
# Hasil baku (Silberschatz): P1(0-1) P2(1-5) P4(5-10) P1(10-17) P3(17-26)
check("SRTF avg waiting", r.avg_waiting, 6.5)
check("SRTF total time", r.total_time, 26)

r = A.fcfs(ps)
# FCFS urut kedatangan: P1,P2,P3,P4 -> waiting 0,7,10,18 = 35/4 = 8.75
check("FCFS avg waiting (data sama)", r.avg_waiting, 8.75)
print("  -> SRTF 6.50 lebih baik dari FCFS 8.75 pada data identik.")

print()
print("=" * 70)
print("KASUS 3 - Round Robin, pengaruh quantum")
print("=" * 70)
ps = [Process("P1", 0, 10), Process("P2", 0, 10), Process("P3", 0, 10)]
for q in (1, 2, 5, 10, 30):
    r = A.round_robin(ps, quantum=q)
    print(
        f"  quantum={q:2}  avg_waiting={r.avg_waiting:6}  "
        f"avg_response={r.avg_response:5}  context_switch={r.context_switches}"
    )
r1 = A.round_robin(ps, quantum=1)
r30 = A.round_robin(ps, quantum=30)
rf = A.fcfs(ps)
check("quantum besar -> identik FCFS", r30.avg_waiting, rf.avg_waiting)
check("quantum=1 response time terkecil", r1.avg_response, 1.0)
print("  -> Trade-off terbukti: quantum kecil = response cepat tapi switch banyak.")

print()
print("=" * 70)
print("KASUS 4 - CPU idle saat belum ada proses tiba")
print("=" * 70)
ps = [Process("P1", 5, 3)]
r = A.fcfs(ps)
print("  gantt:", gantt(r))
check("ada segmen IDLE", r.timeline[0].pid, "IDLE")
check("utilisasi CPU", r.cpu_utilization, 37.5)

print()
print("=" * 70)
print("KASUS 5 - Priority dan starvation")
print("=" * 70)
ps = [
    Process("P-penting", 0, 2, priority=1),
    Process("P-biasa", 0, 4, priority=5),
    Process("P-rendah", 0, 3, priority=9),
]
r = A.priority(ps)
print("  gantt:", gantt(r))
check("urutan pertama = prioritas tertinggi", r.timeline[0].pid, "P-penting")
check("urutan terakhir = prioritas terendah", r.timeline[-1].pid, "P-rendah")

print()
print("=" * 70)
print("KASUS 6 - Validasi masukan salah")
print("=" * 70)
try:
    Process("X", 0, 0)
    check("burst=0 ditolak", "tidak ditolak", "ValueError")
except ValueError as e:
    passed += 1
    print(f"  LULUS  burst=0 ditolak: {e}")
try:
    A.round_robin([Process("X", 0, 1)], quantum=0)
    check("quantum=0 ditolak", "tidak ditolak", "ValueError")
except ValueError as e:
    passed += 1
    print(f"  LULUS  quantum=0 ditolak: {e}")

print()
print("=" * 70)
print("KASUS 7 - Konsistensi rumus pada semua algoritma")
print("=" * 70)
ps = [Process("P1", 0, 6), Process("P2", 2, 4), Process("P3", 4, 2, 1)]
for r in A.compare_all(ps, quantum=2):
    ok = all(m.turnaround - m.burst == m.waiting for m in r.metrics)
    total = sum(m.burst for m in ps_metrics) if (ps_metrics := r.metrics) else 0
    busy = sum(s.duration for s in r.timeline if s.pid != "IDLE")
    label = f"{r.algorithm[:40]:40}"
    if ok and busy == sum(p.burst for p in ps):
        passed += 1
        print(f"  LULUS  {label} waiting=turnaround-burst, total CPU={busy}")
    else:
        failed += 1
        print(f"  GAGAL  {label} rumus/total CPU tidak konsisten (busy={busy})")

print()
print("=" * 70)
print(f"HASIL AKHIR: {passed} lulus, {failed} gagal")
print("=" * 70)
sys.exit(1 if failed else 0)
