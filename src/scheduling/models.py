"""Core data structures for the process scheduling (CPU Scheduling) simulation.

Topic: Process Scheduling (Tanenbaum, Modern Operating Systems, Section 2.4)
"""

from dataclasses import dataclass, field


@dataclass
class Process:
    """A single process to be scheduled on the CPU.

    pid      : process name/identifier, e.g. "P1"
    arrival  : time the process arrives in the ready queue
    burst    : CPU time the process needs
    priority : priority number; the SMALLER it is, the more important
    """

    pid: str
    arrival: int
    burst: int
    priority: int = 0

    def __post_init__(self) -> None:
        if not isinstance(self.pid, str) or not self.pid.strip() or self.pid != self.pid.strip():
            raise ValueError("process name must be text without leading or trailing spaces")
        if self.pid.upper() == "IDLE":
            raise ValueError("the name IDLE is reserved for CPU idle time; use another name")
        for label, value in (("arrival", self.arrival), ("burst", self.burst), ("priority", self.priority)):
            if type(value) is not int:
                raise ValueError(f"{self.pid}: {label} must be an integer")
        if self.burst <= 0:
            raise ValueError(f"{self.pid}: burst time must be > 0, not {self.burst}")
        if self.arrival < 0:
            raise ValueError(f"{self.pid}: arrival time cannot be negative")


@dataclass
class Segment:
    """One time slice in the Gantt chart: process `pid` uses the CPU from start..end."""

    pid: str
    start: int
    end: int

    @property
    def duration(self) -> int:
        return self.end - self.start


@dataclass
class Metrics:
    """Measurements for one process after it has been scheduled.

    completion - time the process fully finishes
    turnaround - completion - arrival  (total time the process "lives" in the system)
    waiting    - turnaround - burst    (time spent waiting, not working)
    response   - time the process first gets the CPU, minus arrival
    """

    pid: str
    arrival: int
    burst: int
    completion: int
    turnaround: int
    waiting: int
    response: int


@dataclass
class ScheduleResult:
    """Complete output of a scheduling algorithm."""

    algorithm: str
    timeline: list[Segment] = field(default_factory=list)
    metrics: list[Metrics] = field(default_factory=list)
    log: list[str] = field(default_factory=list)
    context_switches: int = 0

    @property
    def avg_waiting(self) -> float:
        return _mean(m.waiting for m in self.metrics)

    @property
    def avg_turnaround(self) -> float:
        return _mean(m.turnaround for m in self.metrics)

    @property
    def avg_response(self) -> float:
        return _mean(m.response for m in self.metrics)

    @property
    def total_time(self) -> int:
        return max((s.end for s in self.timeline), default=0)

    @property
    def cpu_utilization(self) -> float:
        """Percentage of time the CPU is actually busy (not idle)."""
        if self.total_time == 0:
            return 0.0
        busy = sum(s.duration for s in self.timeline if s.pid != "IDLE")
        return round(busy / self.total_time * 100, 2)

    def to_dict(self) -> dict:
        """JSON shape sent to the web interface."""
        return {
            "algorithm": self.algorithm,
            "timeline": [
                {"pid": s.pid, "start": s.start, "end": s.end, "duration": s.duration}
                for s in self.timeline
            ],
            "metrics": [vars(m) for m in self.metrics],
            "log": self.log,
            "summary": {
                "avg_waiting": self.avg_waiting,
                "avg_turnaround": self.avg_turnaround,
                "avg_response": self.avg_response,
                "total_time": self.total_time,
                "cpu_utilization": self.cpu_utilization,
                "context_switches": self.context_switches,
            },
        }


def _mean(values) -> float:
    vals = list(values)
    if not vals:
        return 0.0
    return round(sum(vals) / len(vals), 2)


def build_metrics(
    processes: list[Process],
    timeline: list[Segment],
) -> list[Metrics]:
    """Compute completion/turnaround/waiting/response from a finished Gantt chart.

    Shared by every algorithm so the formulas stay consistent and are computed once.
    """
    first_seen: dict[str, int] = {}
    last_seen: dict[str, int] = {}

    for seg in timeline:
        if seg.pid == "IDLE":
            continue
        first_seen.setdefault(seg.pid, seg.start)
        last_seen[seg.pid] = seg.end

    out: list[Metrics] = []
    for p in sorted(processes, key=lambda x: x.pid):
        completion = last_seen.get(p.pid, p.arrival)
        turnaround = completion - p.arrival
        out.append(
            Metrics(
                pid=p.pid,
                arrival=p.arrival,
                burst=p.burst,
                completion=completion,
                turnaround=turnaround,
                waiting=turnaround - p.burst,
                response=first_seen.get(p.pid, p.arrival) - p.arrival,
            )
        )
    return out


def merge_adjacent(timeline: list[Segment]) -> list[Segment]:
    """Merge adjacent segments that belong to the same process.

    Preemptive algorithms produce many 1-unit segments (from the
    tick-by-tick simulation). This tidies them up so the Gantt chart is
    not filled with many identical small boxes.
    """
    if not timeline:
        return []
    merged = [Segment(timeline[0].pid, timeline[0].start, timeline[0].end)]
    for seg in timeline[1:]:
        if seg.pid == merged[-1].pid and seg.start == merged[-1].end:
            merged[-1].end = seg.end
        else:
            merged.append(Segment(seg.pid, seg.start, seg.end))
    return merged


def validate_processes(processes: list[Process]) -> None:
    """Prevent duplicate identifiers from corrupting the remaining/metrics dictionaries."""
    if len({p.pid for p in processes}) != len(processes):
        raise ValueError("each process name must be unique")


def count_context_switches(timeline: list[Segment]) -> int:
    """Direct switches between different processes; idle and the first dispatch are not counted."""
    return sum(a.pid != b.pid and a.pid != "IDLE" and b.pid != "IDLE"
               for a, b in zip(timeline, timeline[1:]))
