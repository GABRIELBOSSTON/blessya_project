"""Deadlock Detection and Recovery.

Topic: Deadlock - Ostrich Algorithm, Detection & Recovery

Unlike avoidance (Banker's), the approach here lets deadlocks HAPPEN, then
detects and resolves them. This is more practical because it does not need
maximum demands to be declared up front.

This module contains three parts:

1. OSTRICH ALGORITHM
   Deliberately does NOTHING. The name comes from the image of an ostrich
   hiding its head in the sand. It is used in practice: UNIX and Windows
   apply it to many resource types for economic reasons. If a deadlock
   happens once a year while preventing it slows the system every day,
   restarting processes is cheaper than prevention. The choice is an
   engineering trade-off, not laziness.

2. DETECTION
   - One instance per resource -> Wait-For Graph, look for a cycle.
   - Multiple instances per resource -> an algorithm similar to the Safety
     Algorithm, but using the Request matrix (CURRENT actual requests)
     instead of Need (maximum demand). The difference matters:
     Need is "may be requested later", Request is "requested right now".

3. RECOVERY
   - Victim termination: pick a process to kill and release its resources.
   - Repeated until no deadlock remains.
"""

from dataclasses import dataclass


# ======================================================================
# 1. OSTRICH ALGORITHM
# ======================================================================


def ostrich_algorithm(deadlock_detected: bool) -> dict:
    """Deliberately ignore the problem.

    Implemented as a real function so it can be compared fairly with the
    other strategies, rather than only discussed as theory.
    """
    return {
        "strategy": "Ostrich Algorithm",
        "action_taken": "none",
        "deadlock_detected": deadlock_detected,
        "deadlock_resolved": False,
        "overhead": "zero - no checks performed",
        "explanation": (
            "The system does not check for or handle deadlocks. If one occurs, "
            "processes will hang until a user or administrator terminates "
            "them manually. Used by UNIX and Windows for many resource types "
            "because the cost of prevention is considered higher than the impact "
            "of infrequent deadlocks."
        ),
        "when_appropriate": (
            "When deadlocks are very rare AND their impact is tolerable "
            "(processes can be restarted without data corruption)."
        ),
        "when_unacceptable": (
            "Real-time systems, flight control, medical devices, financial "
            "transaction databases - where deadlocks must be handled."
        ),
    }


# ======================================================================
# 2a. DETECTION - Wait-For Graph (one instance per resource)
# ======================================================================


@dataclass
class ResourceGraph:
    """Resource Allocation Graph for single-instance resources.

    held_by   : {resource: process}  - which process holds each resource
    waiting   : {process: resource}  - which resource each process waits for
    """

    processes: list[str]
    resources: list[str]
    held_by: dict[str, str]
    waiting: dict[str, str]

    def __post_init__(self) -> None:
        for r, p in self.held_by.items():
            if r not in self.resources:
                raise ValueError(f"resource '{r}' not registered")
            if p not in self.processes:
                raise ValueError(f"process '{p}' not registered")
        for p, r in self.waiting.items():
            if p not in self.processes:
                raise ValueError(f"process '{p}' not registered")
            if r not in self.resources:
                raise ValueError(f"resource '{r}' not registered")

    def wait_for_graph(self) -> dict[str, list[str]]:
        """Convert the Resource Allocation Graph into a Wait-For Graph.

        Method: remove the resource nodes. Add an edge P1 -> P2 if P1 waits
        for a resource currently held by P2. A deadlock exists if and only
        if this graph has a cycle.
        """
        g: dict[str, list[str]] = {p: [] for p in self.processes}
        for p, r in self.waiting.items():
            owner = self.held_by.get(r)
            if owner and owner != p:
                g[p].append(owner)
        return g


def find_cycles(graph: dict[str, list[str]]) -> list[list[str]]:
    """Find every cycle in a directed graph using DFS.

    Uses three-state coloring:
      white = not visited, grey = on the current path, black = finished
    Reaching a grey node while exploring means there is a cycle.
    """
    WHITE, GREY, BLACK = 0, 1, 2
    color = {n: WHITE for n in graph}
    cycles: list[list[str]] = []
    path: list[str] = []

    def dfs(node: str) -> None:
        color[node] = GREY
        path.append(node)
        for nxt in graph.get(node, []):
            if nxt not in color:
                continue
            if color[nxt] == GREY:
                loop = path[path.index(nxt):] + [nxt]
                if loop not in cycles:
                    cycles.append(loop)
            elif color[nxt] == WHITE:
                dfs(nxt)
        path.pop()
        color[node] = BLACK

    for n in graph:
        if color[n] == WHITE:
            dfs(n)
    return cycles


def detect_single_instance(graph: ResourceGraph) -> dict:
    """Detect deadlock for single-instance resources."""
    wfg = graph.wait_for_graph()
    log: list[str] = ["Building Wait-For Graph from Resource Allocation Graph:"]

    for p, r in sorted(graph.waiting.items()):
        owner = graph.held_by.get(r)
        if owner and owner != p:
            log.append(f"  {p} waiting for {r}, held by {owner}  =>  {p} -> {owner}")
        elif owner == p:
            log.append(f"  {p} waiting for {r} which it holds itself (ignored)")
        else:
            log.append(f"  {p} waiting for {r}, but {r} is free - no edge")

    edges = [f"{a} -> {b}" for a, lst in wfg.items() for b in lst]
    log.append(f"Wait-For Graph edges: {edges if edges else 'none'}")

    cycles = find_cycles(wfg)
    log.append("")
    if cycles:
        log.append(f"DEADLOCK DETECTED - found {len(cycles)} cycle(s):")
        for c in cycles:
            log.append(f"  {' -> '.join(c)}")
        involved = sorted({p for c in cycles for p in c})
        log.append(f"Involved processes: {', '.join(involved)}")
        log.append(
            "All four Coffman conditions are met, including circular wait "
            "shown by the cycle above."
        )
    else:
        involved = []
        log.append("NO DEADLOCK - Wait-For Graph is cycle-free (acyclic).")

    return {
        "deadlock": bool(cycles),
        "cycles": cycles,
        "involved": involved,
        "wait_for_graph": wfg,
        "log": log,
    }


# ======================================================================
# 2b. DETECTION - multiple instances per resource
# ======================================================================


@dataclass
class MultiInstanceState:
    """System state for multi-instance detection.

    allocation : n x m, currently held
    request    : n x m, CURRENTLY requested (not the maximum demand)
    available  : vector of m, still free
    """

    processes: list[str]
    resources: list[str]
    allocation: list[list[int]]
    request: list[list[int]]
    available: list[int]

    def __post_init__(self) -> None:
        n, m = len(self.processes), len(self.resources)
        if len(self.allocation) != n or len(self.request) != n:
            raise ValueError("number of rows must match number of processes")
        if len(self.available) != m:
            raise ValueError("available length must match number of resources")

    def copy(self) -> "MultiInstanceState":
        return MultiInstanceState(
            processes=list(self.processes),
            resources=list(self.resources),
            allocation=[r[:] for r in self.allocation],
            request=[r[:] for r in self.request],
            available=self.available[:],
        )

    def to_dict(self) -> dict:
        return {
            "processes": self.processes,
            "resources": self.resources,
            "allocation": self.allocation,
            "request": self.request,
            "available": self.available,
        }


def detect_multi_instance(state: MultiInstanceState) -> dict:
    """Detection Algorithm for multiple instances.

    Similar to the Safety Algorithm, with TWO important differences:
      1. It uses Request (actual requests), not Need (maximum demand).
      2. A process with zero Allocation is marked finished immediately,
         because it holds nothing and therefore cannot block others.

    Processes that can never be marked finished are the ones that are
    deadlocked.
    """
    n, m = len(state.processes), len(state.resources)
    work = state.available[:]
    finish = [all(v == 0 for v in state.allocation[i]) for i in range(n)]
    order: list[str] = []
    log: list[str] = [f"Start. Work = Available = {work}"]

    for i in range(n):
        if finish[i]:
            log.append(
                f"  {state.processes[i]} holds no resources "
                f"-> immediately marked finished"
            )

    while True:
        found = None
        for i in range(n):
            if finish[i]:
                continue
            if all(state.request[i][j] <= work[j] for j in range(m)):
                found = i
                break

        if found is None:
            break

        i = found
        log.append(
            f"{state.processes[i]}: Request {state.request[i]} <= Work {work} "
            f"-> request can be satisfied"
        )
        work = [work[j] + state.allocation[i][j] for j in range(m)]
        finish[i] = True
        order.append(state.processes[i])
        log.append(
            f"  {state.processes[i]} finished, releasing {state.allocation[i]} "
            f"-> Work becomes {work}"
        )

    deadlocked = [state.processes[i] for i in range(n) if not finish[i]]
    log.append("")
    if deadlocked:
        log.append(f"DEADLOCK DETECTED. Processes in deadlock: {', '.join(deadlocked)}")
        for i in range(n):
            if not finish[i]:
                kurang = [
                    f"{state.resources[j]} (requested {state.request[i][j]}, available {work[j]})"
                    for j in range(m)
                    if state.request[i][j] > work[j]
                ]
                log.append(
                    f"  {state.processes[i]} waiting: {'; '.join(kurang)} "
                    f"while holding {state.allocation[i]}"
                )
        log.append(
            "No execution order can complete these processes."
        )
    else:
        log.append(
            f"NO DEADLOCK. All processes can finish in order: "
            f"< {' -> '.join(order)} >"
        )

    return {
        "deadlock": bool(deadlocked),
        "deadlocked_processes": deadlocked,
        "safe_order": order,
        "work_final": work,
        "log": log,
    }


# ======================================================================
# 3. RECOVERY
# ======================================================================


def recover_by_termination(
    state: MultiInstanceState, strategy: str = "most_resources"
) -> dict:
    """Recover from deadlock by terminating victim processes one at a time.

    Victim selection strategies:
      "most_resources"  - kill the process holding the most resources.
                          Restores the system fastest.
      "fewest_resources"- kill the process holding the fewest.
                          Smaller loss per victim, but more processes may
                          need to be killed.
      "first"           - kill the process with the lowest index. Simplest,
                          but arbitrary.

    Real systems also consider process priority, how long it has run, and
    whether it can be restarted safely. A process that is writing to a
    database, for example, must not be killed carelessly because it could
    leave half-written data behind.
    """
    valid = ("most_resources", "fewest_resources", "first")
    if strategy not in valid:
        raise ValueError(f"strategy must be one of {valid}")

    work_state = state.copy()
    victims: list[dict] = []
    log: list[str] = []
    rounds = 0

    while True:
        rounds += 1
        det = detect_multi_instance(work_state)
        if not det["deadlock"]:
            log.append(
                f"Round {rounds}: no more deadlock. Recovery complete."
            )
            break
        if rounds > len(state.processes) + 1:
            log.append("Stopped - too many rounds (should not happen).")
            break

        stuck = det["deadlocked_processes"]
        log.append(f"Round {rounds}: deadlock on {', '.join(stuck)}")

        idxs = [work_state.processes.index(p) for p in stuck]
        if strategy == "most_resources":
            vi = max(idxs, key=lambda i: (sum(work_state.allocation[i]), -i))
            why = "holds the most resources"
        elif strategy == "fewest_resources":
            vi = min(idxs, key=lambda i: (sum(work_state.allocation[i]), i))
            why = "holds the fewest resources"
        else:
            vi = min(idxs)
            why = "lowest process index"

        name = work_state.processes[vi]
        freed = work_state.allocation[vi][:]
        log.append(
            f"  Victim chosen: {name} ({why}, holding {freed})"
        )

        for j in range(len(work_state.resources)):
            work_state.available[j] += freed[j]
            work_state.allocation[vi][j] = 0
            work_state.request[vi][j] = 0

        log.append(f"  {name} terminated. Available becomes {work_state.available}")
        victims.append({"process": name, "released": freed, "reason": why})

    return {
        "strategy": strategy,
        "victims": [v["process"] for v in victims],
        "victim_details": victims,
        "rounds": rounds,
        "resolved": not detect_multi_instance(work_state)["deadlock"],
        "state_after": work_state.to_dict(),
        "log": log,
        "summary": (
            f"Deadlock resolved by terminating {len(victims)} process(es) "
            f"({', '.join(v['process'] for v in victims) or 'none'}) "
            f"using '{strategy}' strategy."
        )
        if victims
        else "No deadlock, no processes need to be terminated.",
    }


def compare_recovery_strategies(state: MultiInstanceState) -> list[dict]:
    """Compare the three victim selection strategies on the same state."""
    out = []
    for s in ("most_resources", "fewest_resources", "first"):
        r = recover_by_termination(state, strategy=s)
        out.append(
            {
                "strategy": s,
                "victims": r["victims"],
                "victim_count": len(r["victims"]),
                "resolved": r["resolved"],
            }
        )
    return out


# ======================================================================
# Sample data
# ======================================================================


def deadlocked_graph() -> ResourceGraph:
    """Simple cycle: P1 -> P2 -> P3 -> P1."""
    return ResourceGraph(
        processes=["P1", "P2", "P3"],
        resources=["R1", "R2", "R3"],
        held_by={"R1": "P1", "R2": "P2", "R3": "P3"},
        waiting={"P1": "R2", "P2": "R3", "P3": "R1"},
    )


def safe_graph() -> ResourceGraph:
    """Wait chain without a cycle: P1 -> P2 -> P3, P3 is not waiting."""
    return ResourceGraph(
        processes=["P1", "P2", "P3"],
        resources=["R1", "R2", "R3"],
        held_by={"R1": "P1", "R2": "P2", "R3": "P3"},
        waiting={"P1": "R2", "P2": "R3"},
    )


def deadlocked_multi() -> MultiInstanceState:
    """Deadlocked state with multiple instances.

    Available is [0,0,0] and every process requests something unavailable
    while all of them hold resources. None can make progress.
    """
    return MultiInstanceState(
        processes=["P0", "P1", "P2", "P3"],
        resources=["A", "B", "C"],
        allocation=[
            [0, 1, 0],
            [2, 0, 0],
            [3, 0, 3],
            [2, 1, 1],
        ],
        request=[
            [0, 0, 1],
            [2, 0, 2],
            [0, 0, 1],
            [1, 0, 0],
        ],
        available=[0, 0, 0],
    )


def recoverable_multi() -> MultiInstanceState:
    """A state that can finish on its own without recovery (negative example)."""
    return MultiInstanceState(
        processes=["P0", "P1", "P2"],
        resources=["A", "B"],
        allocation=[[1, 0], [0, 1], [1, 1]],
        request=[[0, 1], [1, 0], [0, 0]],
        available=[1, 1],
    )


if __name__ == "__main__":
    print("=" * 72)
    print("PART 1 - OSTRICH ALGORITHM")
    print("=" * 72)
    o = ostrich_algorithm(deadlock_detected=True)
    print(f"Action taken    : {o['action_taken']}")
    print(f"Overhead        : {o['overhead']}")
    print(f"Explanation     : {o['explanation']}")
    print(f"Appropriate when: {o['when_appropriate']}")
    print(f"Unacceptable in : {o['when_unacceptable']}")

    print()
    print("=" * 72)
    print("PART 2a - DETECTION WITH A WAIT-FOR GRAPH (single instance)")
    print("=" * 72)
    print("\nCASE A - with a cycle")
    print("-" * 72)
    for line in detect_single_instance(deadlocked_graph())["log"]:
        print(line)

    print("\nCASE B - no cycle")
    print("-" * 72)
    for line in detect_single_instance(safe_graph())["log"]:
        print(line)

    print()
    print("=" * 72)
    print("PART 2b - DETECTION WITH MULTIPLE INSTANCES")
    print("=" * 72)
    dm = deadlocked_multi()
    print(f"{'Process':<8} {'Allocation':<12} {'Request':<12}")
    for i, p in enumerate(dm.processes):
        print(f"{p:<8} {str(dm.allocation[i]):<12} {str(dm.request[i]):<12}")
    print(f"Available: {dm.available}\n")
    for line in detect_multi_instance(dm)["log"]:
        print(line)

    print("\nCOMPARISON - a state that is NOT deadlocked")
    print("-" * 72)
    for line in detect_multi_instance(recoverable_multi())["log"]:
        print(line)

    print()
    print("=" * 72)
    print("PART 3 - RECOVERY BY VICTIM TERMINATION")
    print("=" * 72)
    rec = recover_by_termination(dm, strategy="most_resources")
    for line in rec["log"]:
        print(line)
    print()
    print(rec["summary"])

    print()
    print("COMPARISON OF VICTIM SELECTION STRATEGIES")
    print("-" * 72)
    print(f"{'Strategy':<20} {'Victim count':<15} {'Victims':<25} Resolved")
    for c in compare_recovery_strategies(dm):
        print(
            f"{c['strategy']:<20} {c['victim_count']:<15} "
            f"{', '.join(c['victims']):<25} {'yes' if c['resolved'] else 'no'}"
        )
