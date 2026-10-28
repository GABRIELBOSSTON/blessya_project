"""Banker's Algorithm - Deadlock Avoidance.

Topic: Deadlock - Avoidance & Prevention Algorithms

The basic idea borrows from how a bank works. A bank has a certain amount
of money. Each customer declares up front the maximum credit they may
withdraw. The bank approves a withdrawal only if, AFTER it, the bank can
still satisfy the maximum demands of all customers in some order. If that
cannot be guaranteed, the withdrawal is postponed - even though the money
is currently available.

Terms used by the algorithm:
  Allocation : resources CURRENTLY held by each process
  Max        : MAXIMUM demand of each process (declared up front)
  Need       : Max - Allocation, i.e. what may still be requested
  Available  : resources that are still free

SAFE STATE: there is an order of processes (a safe sequence) in which each
process can obtain all of its Need, finish, and then return all of its
resources for the next process to use.

A common misconception: an UNSAFE STATE IS NOT A DEADLOCK. Unsafe only
means a deadlock MAY happen if every process actually requests its maximum
demand. The Banker's Algorithm is conservative: it refuses things that
might actually still be safe, in exchange for a guarantee.

Cost of the algorithm: O(n^2 * m) for n processes and m resource types, and
it requires Max to be known in advance - something rarely possible in real
operating systems. That is why modern OSes generally do not use it.
"""

from dataclasses import dataclass


@dataclass
class BankerState:
    """System state for the Banker's Algorithm.

    processes : process names, e.g. ["P0", "P1", ...]
    resources : resource type names, e.g. ["A", "B", "C"]
    allocation: n x m matrix, resources currently held
    maximum   : n x m matrix, maximum demand
    available : vector of m, free resources
    """

    processes: list[str]
    resources: list[str]
    allocation: list[list[int]]
    maximum: list[list[int]]
    available: list[int]

    def __post_init__(self) -> None:
        n, m = len(self.processes), len(self.resources)
        if len(self.allocation) != n or len(self.maximum) != n:
            raise ValueError("number of allocation/maximum rows must match number of processes")
        if len(self.available) != m:
            raise ValueError("available length must match number of resource types")
        for i, (a, mx) in enumerate(zip(self.allocation, self.maximum)):
            if len(a) != m or len(mx) != m:
                raise ValueError(f"row {i} length does not match number of resources")
            for j in range(m):
                if a[j] < 0 or mx[j] < 0:
                    raise ValueError("values cannot be negative")
                if a[j] > mx[j]:
                    raise ValueError(
                        f"{self.processes[i]} holds {a[j]} "
                        f"{self.resources[j]} exceeding Max {mx[j]}"
                    )

    @property
    def need(self) -> list[list[int]]:
        """Need = Max - Allocation."""
        return [
            [mx - al for mx, al in zip(mrow, arow)]
            for mrow, arow in zip(self.maximum, self.allocation)
        ]

    @property
    def total_resources(self) -> list[int]:
        """Total resources in the system = held + free."""
        m = len(self.resources)
        return [
            sum(row[j] for row in self.allocation) + self.available[j] for j in range(m)
        ]

    def copy(self) -> "BankerState":
        return BankerState(
            processes=list(self.processes),
            resources=list(self.resources),
            allocation=[row[:] for row in self.allocation],
            maximum=[row[:] for row in self.maximum],
            available=self.available[:],
        )

    def to_dict(self) -> dict:
        return {
            "processes": self.processes,
            "resources": self.resources,
            "allocation": self.allocation,
            "maximum": self.maximum,
            "need": self.need,
            "available": self.available,
            "total": self.total_resources,
        }


def is_safe(state: BankerState) -> dict:
    """Safety Algorithm: find a safe sequence.

    Steps:
      1. work = available ; finish[i] = False for every i
      2. Find a process i that is not finished and Need[i] <= work
      3. If found: treat it as finished, work += Allocation[i], finish[i]=True,
         then repeat step 2
      4. If none is left: the state is SAFE if all finished, UNSAFE otherwise
    """
    n, m = len(state.processes), len(state.resources)
    need = state.need
    work = state.available[:]
    finish = [False] * n
    sequence: list[str] = []
    log: list[str] = []
    steps: list[dict] = []

    log.append(f"Start. Work = Available = {work}")

    while True:
        found = None
        for i in range(n):
            if finish[i]:
                continue
            if all(need[i][j] <= work[j] for j in range(m)):
                found = i
                break
            kurang = [
                f"{state.resources[j]}:needs {need[i][j]} > available {work[j]}"
                for j in range(m)
                if need[i][j] > work[j]
            ]
            log.append(
                f"  {state.processes[i]} skipped - Need {need[i]} "
                f"cannot be met by Work {work} ({'; '.join(kurang)})"
            )

        if found is None:
            break

        i = found
        before = work[:]
        log.append(
            f"{state.processes[i]} CAN run: Need {need[i]} <= Work {work}"
        )
        work = [work[j] + state.allocation[i][j] for j in range(m)]
        finish[i] = True
        sequence.append(state.processes[i])
        log.append(
            f"  {state.processes[i]} finished and released "
            f"Allocation {state.allocation[i]} -> Work becomes {work}"
        )
        steps.append(
            {
                "process": state.processes[i],
                "need": need[i][:],
                "work_before": before,
                "released": state.allocation[i][:],
                "work_after": work[:],
            }
        )

    safe = all(finish)
    stuck = [state.processes[i] for i in range(n) if not finish[i]]

    if safe:
        log.append("")
        log.append(f"RESULT: SAFE. Safe sequence = < {' -> '.join(sequence)} >")
        log.append(
            "Meaning there exists an execution sequence where all processes are guaranteed to finish."
        )
    else:
        log.append("")
        log.append(f"RESULT: UNSAFE. Processes that cannot be guaranteed to finish: {stuck}")
        log.append(
            "Note: unsafe is NOT deadlock. Deadlock will only occur if "
            "those processes actually claim their maximum demands."
        )

    return {
        "safe": safe,
        "sequence": sequence,
        "unfinished": stuck,
        "steps": steps,
        "log": log,
    }


def request_resources(state: BankerState, process: str, request: list[int]) -> dict:
    """Resource-Request Algorithm: may this request be granted?

    Three checks in order:
      1. Request <= Need      -> otherwise the process violates its Max declaration (ERROR)
      2. Request <= Available -> otherwise the process must wait
      3. Tentatively allocate, then run the safety check.
         If the result is safe -> grant. If unsafe -> ROLL BACK and postpone.

    Step 3 is the essence of avoidance: a request is refused even though the
    resources are available, because granting it leads to an unsafe state.
    """
    if process not in state.processes:
        raise ValueError(f"process '{process}' not found. Options: {state.processes}")
    m = len(state.resources)
    if len(request) != m:
        raise ValueError(f"request length must be {m}")
    if any(r < 0 for r in request):
        raise ValueError("request cannot be negative")

    i = state.processes.index(process)
    need = state.need
    log: list[str] = [f"{process} requests {request}"]

    # Check 1
    viol = [
        f"{state.resources[j]} (requested {request[j]}, Need only {need[i][j]})"
        for j in range(m)
        if request[j] > need[i][j]
    ]
    if viol:
        log.append(f"REJECTED - request exceeds Need: {'; '.join(viol)}")
        log.append(
            "This is a process error: it requested more than its declared Max."
        )
        return {
            "granted": False,
            "reason": "exceeds_need",
            "reason_text": "Request exceeds Need (violates declared Max).",
            "log": log,
            "state_after": state.to_dict(),
            "safety": None,
        }
    log.append(f"  Check 1 PASSED: Request {request} <= Need {need[i]}")

    # Check 2
    short = [
        f"{state.resources[j]} (requested {request[j]}, available {state.available[j]})"
        for j in range(m)
        if request[j] > state.available[j]
    ]
    if short:
        log.append(f"POSTPONED - insufficient resources: {'; '.join(short)}")
        log.append(f"{process} must wait until other processes release resources.")
        return {
            "granted": False,
            "reason": "must_wait",
            "reason_text": "Resources currently unavailable, process must wait.",
            "log": log,
            "state_after": state.to_dict(),
            "safety": None,
        }
    log.append(f"  Check 2 PASSED: Request {request} <= Available {state.available}")

    # Check 3 - tentative allocation
    trial = state.copy()
    for j in range(m):
        trial.available[j] -= request[j]
        trial.allocation[i][j] += request[j]
    log.append(
        f"  Trial allocation: Available becomes {trial.available}, "
        f"Allocation {process} becomes {trial.allocation[i]}"
    )
    log.append("  Running Safety Algorithm on trial state...")

    safety = is_safe(trial)
    log.extend("    " + line for line in safety["log"])

    if safety["safe"]:
        log.append("")
        log.append(
            f"GRANTED - state remains safe. "
            f"Safe sequence: < {' -> '.join(safety['sequence'])} >"
        )
        return {
            "granted": True,
            "reason": "safe",
            "reason_text": (
                "Request granted because system remains in a safe state."
            ),
            "log": log,
            "state_after": trial.to_dict(),
            "safety": safety,
        }

    log.append("")
    log.append("REJECTED - granting this request leads to an UNSAFE state.")
    log.append(
        "Trial allocation CANCELLED, state rolled back to original. "
        "Note: resources are available, yet rejected. This is the "
        "conservative nature of deadlock avoidance."
    )
    return {
        "granted": False,
        "reason": "unsafe",
        "reason_text": (
            "Resources available, but request rejected because it would "
            "lead system into an unsafe state."
        ),
        "log": log,
        "state_after": state.to_dict(),
        "safety": safety,
    }


def classic_example() -> BankerState:
    """Standard example from Silberschatz, Operating System Concepts.

    5 processes, 3 resource types (A=10, B=5, C=7).
    This state is SAFE with safe sequence < P1, P3, P4, P2, P0 >.
    """
    return BankerState(
        processes=["P0", "P1", "P2", "P3", "P4"],
        resources=["A", "B", "C"],
        allocation=[
            [0, 1, 0],
            [2, 0, 0],
            [3, 0, 2],
            [2, 1, 1],
            [0, 0, 2],
        ],
        maximum=[
            [7, 5, 3],
            [3, 2, 2],
            [9, 0, 2],
            [2, 2, 2],
            [4, 3, 3],
        ],
        available=[3, 3, 2],
    )


def unsafe_example() -> BankerState:
    """Example UNSAFE state: no process can have its Need satisfied."""
    return BankerState(
        processes=["P0", "P1", "P2"],
        resources=["A", "B"],
        allocation=[[1, 1], [1, 1], [1, 1]],
        maximum=[[4, 4], [4, 4], [4, 4]],
        available=[1, 1],
    )


def _table(state: BankerState) -> None:
    need = state.need
    w = max(len(p) for p in state.processes) + 2
    head = " ".join(f"{r:>2}" for r in state.resources)
    print(f"{'Process':<{w}} {'Allocation':<{len(head) + 2}} {'Max':<{len(head) + 2}} Need")
    for i, p in enumerate(state.processes):
        a = " ".join(f"{v:>2}" for v in state.allocation[i])
        mx = " ".join(f"{v:>2}" for v in state.maximum[i])
        nd = " ".join(f"{v:>2}" for v in need[i])
        print(f"{p:<{w}} {a:<{len(head) + 2}} {mx:<{len(head) + 2}} {nd}")
    print(f"\nAvailable : {state.available}  (system total: {state.total_resources})")


if __name__ == "__main__":
    print("=" * 72)
    print("BANKER'S ALGORITHM - Deadlock Avoidance")
    print("=" * 72)
    st = classic_example()
    _table(st)

    print()
    print("-" * 72)
    print("SAFETY CHECK on the initial state")
    print("-" * 72)
    r = is_safe(st)
    for line in r["log"]:
        print(line)

    print()
    print("-" * 72)
    print("SCENARIO 1 - P1 requests [1, 0, 2]  (should be GRANTED)")
    print("-" * 72)
    for line in request_resources(st, "P1", [1, 0, 2])["log"]:
        print(line)

    print()
    print("-" * 72)
    print("SCENARIO 2 - P4 requests [3, 3, 0]")
    print("Resources are SUFFICIENT (Available [3,3,2]), yet it is still DENIED")
    print("because granting it would lead the system to an unsafe state.")
    print("-" * 72)
    for line in request_resources(st, "P4", [3, 3, 0])["log"]:
        print(line)

    print()
    print("-" * 72)
    print("SCENARIO 3 - P0 requests [4, 0, 0]  (exceeds Available, POSTPONED)")
    print("-" * 72)
    for line in request_resources(st, "P0", [4, 0, 0])["log"]:
        print(line)

    print()
    print("-" * 72)
    print("SCENARIO 4 - P2 requests [0, 1, 0]  (exceeds Need, process ERROR)")
    print("P2 has Need [6,0,0]: it never declared that it needs B.")
    print("-" * 72)
    for line in request_resources(st, "P2", [0, 1, 0])["log"]:
        print(line)

    print()
    print("=" * 72)
    print("EXAMPLE OF AN UNSAFE STATE")
    print("=" * 72)
    u = unsafe_example()
    _table(u)
    print()
    for line in is_safe(u)["log"]:
        print(line)
