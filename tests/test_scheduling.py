"""Correctness tests for the scheduling algorithms.

Run:  py tests/test_scheduling.py

The expected values below were first calculated by hand. The goal is to
prove that the program does not just "output numbers", but outputs the
CORRECT numbers.
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
        print(f"  PASS  {label}: {got}")
    else:
        failed += 1
        print(f"  FAIL  {label}: got {got}, expected {want}")


def gantt(result) -> str:
    return " ".join(f"{s.pid}({s.start}-{s.end})" for s in result.timeline)


print("=" * 70)
print("CASE 1 - FCFS, convoy effect")
print("=" * 70)
# P1 with burst 24 arrives first and holds back two short processes behind it.
ps = [Process("P1", 0, 24), Process("P2", 0, 3), Process("P3", 0, 3)]
r = A.fcfs(ps)
print("  gantt:", gantt(r))
# P1 waits 0, P2 waits 24, P3 waits 27 -> (0+24+27)/3 = 17.0
check("FCFS avg waiting", r.avg_waiting, 17.0)
check("FCFS total time", r.total_time, 30)

r = A.sjf(ps)
print("  gantt:", gantt(r))
# Order becomes P2(3) P3(3) P1(24): waits 6 + 0 + 3 = 9/3 = 3.0
check("SJF avg waiting", r.avg_waiting, 3.0)
print("  -> SJF improves avg waiting from 17.0 to 3.0 on the same data.")

print()
print("=" * 70)
print("CASE 2 - SRTF preemption")
print("=" * 70)
ps = [Process("P1", 0, 8), Process("P2", 1, 4), Process("P3", 2, 9), Process("P4", 3, 5)]
r = A.srtf(ps)
print("  gantt:", gantt(r))
# Standard result (Silberschatz): P1(0-1) P2(1-5) P4(5-10) P1(10-17) P3(17-26)
check("SRTF avg waiting", r.avg_waiting, 6.5)
check("SRTF total time", r.total_time, 26)

r = A.fcfs(ps)
# FCFS in arrival order: P1,P2,P3,P4 -> waiting 0,7,10,18 = 35/4 = 8.75
check("FCFS avg waiting (same data)", r.avg_waiting, 8.75)
print("  -> SRTF 6.50 is better than FCFS 8.75 on identical data.")

print()
print("=" * 70)
print("CASE 3 - Round Robin, effect of quantum")
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
check("large quantum -> identical to FCFS", r30.avg_waiting, rf.avg_waiting)
check("quantum=1 gives the lowest response time", r1.avg_response, 1.0)
print("  -> Trade-off confirmed: small quantum = fast response but many switches.")

print()
print("=" * 70)
print("CASE 4 - CPU idle before any process arrives")
print("=" * 70)
ps = [Process("P1", 5, 3)]
r = A.fcfs(ps)
print("  gantt:", gantt(r))
check("has an IDLE segment", r.timeline[0].pid, "IDLE")
check("CPU utilization", r.cpu_utilization, 37.5)

print()
print("=" * 70)
print("CASE 5 - Priority and starvation")
print("=" * 70)
ps = [
    Process("P-high", 0, 2, priority=1),
    Process("P-normal", 0, 4, priority=5),
    Process("P-low", 0, 3, priority=9),
]
r = A.priority(ps)
print("  gantt:", gantt(r))
check("first in order = highest priority", r.timeline[0].pid, "P-high")
check("last in order = lowest priority", r.timeline[-1].pid, "P-low")

print()
print("=" * 70)
print("CASE 6 - Invalid input validation")
print("=" * 70)
try:
    Process("X", 0, 0)
    check("burst=0 rejected", "not rejected", "ValueError")
except ValueError as e:
    passed += 1
    print(f"  PASS  burst=0 rejected: {e}")
try:
    A.round_robin([Process("X", 0, 1)], quantum=0)
    check("quantum=0 rejected", "not rejected", "ValueError")
except ValueError as e:
    passed += 1
    print(f"  PASS  quantum=0 rejected: {e}")

print()
print("=" * 70)
print("CASE 7 - Formula consistency across all algorithms")
print("=" * 70)
ps = [Process("P1", 0, 6), Process("P2", 2, 4), Process("P3", 4, 2, 1)]
for r in A.compare_all(ps, quantum=2):
    ok = all(m.turnaround - m.burst == m.waiting for m in r.metrics)
    total = sum(m.burst for m in ps_metrics) if (ps_metrics := r.metrics) else 0
    busy = sum(s.duration for s in r.timeline if s.pid != "IDLE")
    label = f"{r.algorithm[:40]:40}"
    if ok and busy == sum(p.burst for p in ps):
        passed += 1
        print(f"  PASS  {label} waiting=turnaround-burst, total CPU={busy}")
    else:
        failed += 1
        print(f"  FAIL  {label} formula/total CPU inconsistent (busy={busy})")

print()
print("=" * 70)
print(f"RESULT: {passed} passed, {failed} failed")
print("=" * 70)
sys.exit(1 if failed else 0)
