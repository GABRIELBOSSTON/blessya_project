"""Banker's Algorithm - Deadlock Avoidance.

Materi: Deadlock - Avoidance & Prevention Algorithms

Ide dasarnya meminjam cara kerja bank. Bank punya sejumlah uang. Setiap
nasabah mengumumkan di awal berapa maksimal kredit yang mungkin ia tarik.
Bank hanya menyetujui penarikan jika SETELAH penarikan itu bank masih
mampu memenuhi permintaan maksimal semua nasabah dalam suatu urutan
tertentu. Kalau tidak bisa dijamin, penarikan ditunda - walaupun uangnya
sebenarnya sedang ada.

Istilah dalam algoritma:
  Allocation : sumber daya yang SEDANG dipegang tiap proses
  Max        : kebutuhan MAKSIMAL tiap proses (dideklarasikan di awal)
  Need       : Max - Allocation, yaitu sisa yang mungkin masih diminta
  Available  : sumber daya yang masih bebas

SAFE STATE: ada urutan proses (safe sequence) di mana setiap proses bisa
mendapatkan seluruh Need-nya, selesai, lalu mengembalikan semua sumber
dayanya untuk dipakai proses berikutnya.

Yang sering salah dipahami: UNSAFE STATE BUKAN BERARTI DEADLOCK. Unsafe
hanya berarti deadlock MUNGKIN terjadi kalau semua proses benar-benar
menarik kebutuhan maksimalnya. Banker's Algorithm bersifat konservatif:
ia menolak hal-hal yang sebetulnya mungkin masih aman, demi jaminan.

Biaya algoritma ini: O(n^2 * m) untuk n proses dan m jenis sumber daya,
dan ia mensyaratkan Max diketahui di awal - sesuatu yang jarang terpenuhi
di sistem operasi nyata. Itu sebabnya OS modern umumnya tidak memakainya.
"""

from dataclasses import dataclass


@dataclass
class BankerState:
    """Keadaan sistem untuk Banker's Algorithm.

    processes : nama proses, contoh ["P0", "P1", ...]
    resources : nama jenis sumber daya, contoh ["A", "B", "C"]
    allocation: matriks n x m, sumber daya yang dipegang sekarang
    maximum   : matriks n x m, kebutuhan maksimal
    available : vektor m, sumber daya yang bebas
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
        """Total sumber daya di sistem = yang dipegang + yang bebas."""
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
    """Safety Algorithm: cari safe sequence.

    Langkah:
      1. work = available ; finish[i] = False untuk semua i
      2. Cari proses i yang belum finish dan Need[i] <= work
      3. Kalau ada: anggap ia selesai, work += Allocation[i], finish[i]=True,
         lalu ulangi langkah 2
      4. Kalau tidak ada lagi: state SAFE jika semua finish, UNSAFE jika tidak
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
    """Resource-Request Algorithm: boleh tidak permintaan ini dikabulkan?

    Tiga pemeriksaan berurutan:
      1. Request <= Need    -> kalau tidak, proses melanggar deklarasi Max (ERROR)
      2. Request <= Available -> kalau tidak, proses harus menunggu
      3. Coba alokasikan sementara, lalu jalankan safety check.
         Kalau hasilnya safe -> kabulkan. Kalau unsafe -> BATALKAN dan tunda.

    Langkah 3 inilah inti avoidance: permintaan ditolak walaupun sumber
    dayanya tersedia, karena mengabulkannya membawa sistem ke unsafe state.
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

    # Pemeriksaan 1
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

    # Pemeriksaan 2
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

    # Pemeriksaan 3 - alokasi percobaan
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
    """Contoh baku dari Silberschatz, Operating System Concepts.

    5 proses, 3 jenis sumber daya (A=10, B=5, C=7).
    Keadaan ini SAFE dengan safe sequence < P1, P3, P4, P2, P0 >.
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
    """Contoh keadaan UNSAFE: tidak ada proses yang Need-nya bisa dipenuhi."""
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
    print(f"{'Proses':<{w}} {'Allocation':<{len(head) + 2}} {'Max':<{len(head) + 2}} Need")
    for i, p in enumerate(state.processes):
        a = " ".join(f"{v:>2}" for v in state.allocation[i])
        mx = " ".join(f"{v:>2}" for v in state.maximum[i])
        nd = " ".join(f"{v:>2}" for v in need[i])
        print(f"{p:<{w}} {a:<{len(head) + 2}} {mx:<{len(head) + 2}} {nd}")
    print(f"\nAvailable : {state.available}  (total sistem: {state.total_resources})")


if __name__ == "__main__":
    print("=" * 72)
    print("BANKER'S ALGORITHM - Deadlock Avoidance")
    print("=" * 72)
    st = classic_example()
    _table(st)

    print()
    print("-" * 72)
    print("SAFETY CHECK pada keadaan awal")
    print("-" * 72)
    r = is_safe(st)
    for line in r["log"]:
        print(line)

    print()
    print("-" * 72)
    print("SKENARIO 1 - P1 meminta [1, 0, 2]  (seharusnya DIKABULKAN)")
    print("-" * 72)
    for line in request_resources(st, "P1", [1, 0, 2])["log"]:
        print(line)

    print()
    print("-" * 72)
    print("SKENARIO 2 - P4 meminta [3, 3, 0]")
    print("Sumber daya CUKUP (Available [3,3,2]), tetapi tetap DITOLAK")
    print("karena mengabulkannya membawa sistem ke unsafe state.")
    print("-" * 72)
    for line in request_resources(st, "P4", [3, 3, 0])["log"]:
        print(line)

    print()
    print("-" * 72)
    print("SKENARIO 3 - P0 meminta [4, 0, 0]  (melebihi Available, DITUNDA)")
    print("-" * 72)
    for line in request_resources(st, "P0", [4, 0, 0])["log"]:
        print(line)

    print()
    print("-" * 72)
    print("SKENARIO 4 - P2 meminta [0, 1, 0]  (melebihi Need, ERROR proses)")
    print("P2 punya Need [6,0,0]: ia tidak pernah mendeklarasikan butuh B.")
    print("-" * 72)
    for line in request_resources(st, "P2", [0, 1, 0])["log"]:
        print(line)

    print()
    print("=" * 72)
    print("CONTOH KEADAAN UNSAFE")
    print("=" * 72)
    u = unsafe_example()
    _table(u)
    print()
    for line in is_safe(u)["log"]:
        print(line)
