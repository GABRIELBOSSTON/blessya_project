"""Five CPU scheduling algorithms.

Each function takes a list of Process objects and returns a ScheduleResult.
Besides the numbers, every algorithm also writes a `log`: a step-by-step
explanation of the scheduler's decisions. This log is what makes the
program educational rather than just showing the final result.

Topic: Process Scheduling (non-preemptive & preemptive)
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

    Processes are served strictly in order of arrival. Simple and fair in
    terms of order, but prone to the "convoy effect": one long process at
    the front makes every short process behind it wait a long time.
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

    Among the processes that have ALREADY arrived, pick the one with the
    shortest burst. Optimal for average waiting time when all jobs are ready
    at the same time; different arrival times need extra assumptions. It
    cannot be used as-is in real systems because a process's burst time is
    not known before it runs (it can only be predicted).
    Another risk: starvation of processes with long bursts.
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
    """Shortest Remaining Time First - the preemptive version of SJF.

    Simulated tick by tick (1 time unit). At every tick the scheduler checks
    again: is there a process with less remaining time than the running one?
    If so, the running process is preempted.
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
    """Round Robin - preemptive, based on a time quantum.

    Each process gets the CPU for at most `quantum` time units, then moves
    to the back of the queue. This is the algorithm interactive systems use:
    response times are even and no process waits indefinitely.

    Choosing the quantum is the core trade-off:
      - quantum too large -> behaves like FCFS again
      - quantum too small -> context switch overhead dominates
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
        """Add every process that has arrived up to time `upto` to the queue."""
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

        # Processes that arrive DURING this slice join the queue first, then
        # the process whose quantum expired goes to the back. This order
        # matters: reversing it would produce a different Gantt chart.
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
    """Priority Scheduling. A smaller priority number = more important.

    The classic problem is starvation: a low-priority process may never get
    the CPU. The usual fix is aging, which gradually raises the priority of
    processes that have waited long. Aging is NOT implemented here so the
    starvation effect can be observed and discussed.
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
    """Run one algorithm by name. Used by the web server."""
    key = name.lower()
    if key not in ALGORITHMS:
        raise ValueError(
            f"Algorithm '{name}' not recognized. Options: {', '.join(ALGORITHMS)}"
        )
    return ALGORITHMS[key](processes, **kwargs)


def compare_all(processes: list[Process], quantum: int = 2) -> list[ScheduleResult]:
    """Run every algorithm on the same data, for the comparison table."""
    return [
        fcfs(processes),
        sjf(processes),
        srtf(processes),
        round_robin(processes, quantum=quantum),
        priority(processes, preemptive=False),
        priority(processes, preemptive=True),
    ]
