"""Terminal demo of process scheduling.

Run:  py -m src.scheduling.demo

Prints an ASCII Gantt chart and a metrics table, suitable for screenshots
and for inclusion in a report.
"""

from .algorithms import compare_all
from .models import Process, ScheduleResult

# Sample data used throughout so comparisons are fair:
# every algorithm is tested on the SAME set of processes.
SAMPLE = [
    Process("P1", arrival=0, burst=8, priority=3),
    Process("P2", arrival=1, burst=4, priority=1),
    Process("P3", arrival=2, burst=9, priority=4),
    Process("P4", arrival=3, burst=5, priority=2),
]

SCALE = 3  # width of one time unit in the ASCII Gantt chart


def print_input(procs: list[Process]) -> None:
    print("INPUT DATA")
    print("-" * 56)
    print(f"{'Process':<8} {'Arrival':>8} {'Burst':>7} {'Priority':>10}")
    for p in procs:
        print(f"{p.pid:<8} {p.arrival:>8} {p.burst:>7} {p.priority:>10}")
    print(f"\nTotal burst time: {sum(p.burst for p in procs)}")


def print_gantt(res: ScheduleResult) -> None:
    """Draw the Gantt chart with ASCII characters."""
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

    # Time markers under the chart: start/end boundary of each segment.
    bounds = [res.timeline[0].start] + [s.end for s in res.timeline]
    print("time: " + " -> ".join(str(b) for b in bounds))


def print_metrics(res: ScheduleResult) -> None:
    print(
        f"{'Process':<8} {'Arr':>5} {'Burst':>6} {'Finish':>8} "
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
        f"{'AVERAGE':<8} {'':>5} {'':>6} {'':>8} "
        f"{res.avg_turnaround:>11} {res.avg_waiting:>8} {res.avg_response:>9}"
    )
    print(
        f"\nCPU utilization: {res.cpu_utilization}%   "
        f"Total time: {res.total_time}   "
        f"Context switch: {res.context_switches}"
    )


def main() -> None:
    print("=" * 72)
    print("PROCESS SCHEDULING SIMULATION (CPU SCHEDULING)")
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

        print("\nScheduler decision steps:")
        for line in res.log[:14]:
            print(f"  {line}")
        if len(res.log) > 14:
            print(f"  ... ({len(res.log) - 14} more lines)")

    # ---------------- Final comparison table ----------------
    print()
    print("=" * 72)
    print("COMPARISON TABLE OF ALL ALGORITHMS")
    print("=" * 72)
    print(
        f"{'Algorithm':<46} {'AvgWait':>8} {'AvgTA':>8} "
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
    print("ANALYSIS")
    print("-" * 72)
    print(
        f"Lowest average waiting time : {best_w.algorithm} ({best_w.avg_waiting})"
    )
    print(
        f"Lowest average response time: {best_r.algorithm} ({best_r.avg_response})"
    )
    print(
        "\nNo single algorithm is best on every measure at once.\n"
        "SJF/SRTF win on waiting time, but risk starvation and need\n"
        "burst times that are not actually known in advance.\n"
        "Round Robin gives even response times, so it feels responsive\n"
        "to users, at the cost of more context switches.\n"
        "The choice of algorithm therefore depends on the system goal:\n"
        "throughput (batch) or responsiveness (interactive)."
    )

    # ---------------- Effect of quantum on Round Robin ----------------
    from .algorithms import round_robin

    print()
    print("=" * 72)
    print("EFFECT OF TIME QUANTUM ON ROUND ROBIN")
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
        "\nThe core trade-off is visible: a small quantum gives good\n"
        "response time but context switches spike; a large quantum reduces\n"
        "context switches but behaves more like FCFS."
    )


if __name__ == "__main__":
    main()
