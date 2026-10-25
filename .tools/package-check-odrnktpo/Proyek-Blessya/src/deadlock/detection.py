"""Deteksi Deadlock dan Recovery.

Materi: Deadlock - Ostrich Algorithm, Detection & Recovery

Berbeda dari avoidance (Banker's), pendekatan di sini membiarkan deadlock
TERJADI, lalu mendeteksi dan memperbaikinya. Ini lebih praktis karena
tidak butuh deklarasi kebutuhan maksimal di awal.

Modul ini memuat tiga hal:

1. OSTRICH ALGORITHM
   Secara sengaja TIDAK melakukan apa pun. Namanya dari perumpamaan burung
   unta yang menyembunyikan kepala di pasir. Ini bukan lelucon: UNIX dan
   Windows benar-benar memakainya untuk banyak jenis sumber daya, dengan
   alasan ekonomi. Kalau deadlock terjadi sekali setahun sementara
   pencegahannya memperlambat sistem setiap hari, maka merestart proses
   lebih murah daripada mencegahnya. Keputusannya adalah trade-off
   rekayasa, bukan kemalasan.

2. DETECTION
   - Kasus satu instance per sumber daya -> Wait-For Graph, cari siklus.
   - Kasus banyak instance per sumber daya -> algoritma mirip Safety
     Algorithm, tapi memakai matriks Request (permintaan NYATA saat ini)
     bukan Need (kebutuhan maksimal). Perbedaan ini penting:
     Need itu "mungkin diminta nanti", Request itu "sedang diminta".

3. RECOVERY
   - Terminasi korban: pilih proses untuk dimatikan, lepas sumber dayanya.
   - Dilakukan berulang sampai tidak ada deadlock lagi.
"""

from dataclasses import dataclass


# ======================================================================
# 1. OSTRICH ALGORITHM
# ======================================================================


def ostrich_algorithm(deadlock_detected: bool) -> dict:
    """Mengabaikan masalah secara sengaja.

    Diimplementasikan sebagai fungsi nyata agar bisa dibandingkan jujur
    dengan strategi lain di laporan, bukan hanya dibahas sebagai teori.
    """
    return {
        "strategy": "Ostrich Algorithm",
        "action_taken": "tidak ada",
        "deadlock_detected": deadlock_detected,
        "deadlock_resolved": False,
        "overhead": "nol - tidak ada pemeriksaan apa pun",
        "explanation": (
            "Sistem tidak memeriksa dan tidak menangani deadlock. Jika terjadi, "
            "proses akan menggantung sampai pengguna atau administrator "
            "mematikannya secara manual. Dipakai oleh UNIX dan Windows untuk "
            "banyak jenis sumber daya karena biaya pencegahan dianggap lebih "
            "mahal daripada dampak deadlock yang jarang terjadi."
        ),
        "when_appropriate": (
            "Ketika deadlock sangat jarang DAN dampaknya bisa ditoleransi "
            "(proses bisa direstart tanpa kerusakan data)."
        ),
        "when_unacceptable": (
            "Sistem real-time, kendali penerbangan, alat medis, basis data "
            "transaksi keuangan - di sana deadlock harus ditangani."
        ),
    }


# ======================================================================
# 2a. DETECTION - Wait-For Graph (satu instance per sumber daya)
# ======================================================================


@dataclass
class ResourceGraph:
    """Resource Allocation Graph untuk sumber daya instance tunggal.

    held_by   : {sumber_daya: proses}  - sumber daya dipegang siapa
    waiting   : {proses: sumber_daya}  - proses menunggu sumber daya apa
    """

    processes: list[str]
    resources: list[str]
    held_by: dict[str, str]
    waiting: dict[str, str]

    def __post_init__(self) -> None:
        for r, p in self.held_by.items():
            if r not in self.resources:
                raise ValueError(f"sumber daya '{r}' tidak terdaftar")
            if p not in self.processes:
                raise ValueError(f"proses '{p}' tidak terdaftar")
        for p, r in self.waiting.items():
            if p not in self.processes:
                raise ValueError(f"proses '{p}' tidak terdaftar")
            if r not in self.resources:
                raise ValueError(f"sumber daya '{r}' tidak terdaftar")

    def wait_for_graph(self) -> dict[str, list[str]]:
        """Ubah Resource Allocation Graph menjadi Wait-For Graph.

        Caranya: hilangkan node sumber daya. Buat sisi P1 -> P2 jika P1
        menunggu sumber daya yang sedang dipegang P2. Deadlock terjadi
        jika dan hanya jika graf ini punya siklus.
        """
        g: dict[str, list[str]] = {p: [] for p in self.processes}
        for p, r in self.waiting.items():
            owner = self.held_by.get(r)
            if owner and owner != p:
                g[p].append(owner)
        return g


def find_cycles(graph: dict[str, list[str]]) -> list[list[str]]:
    """Cari semua siklus dalam graf berarah dengan DFS.

    Memakai pewarnaan tiga keadaan:
      putih = belum dikunjungi, abu = sedang di jalur sekarang, hitam = selesai
    Menemukan node abu-abu saat menelusuri berarti ada siklus.
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
    """Deteksi deadlock pada sumber daya instance tunggal."""
    wfg = graph.wait_for_graph()
    log: list[str] = ["Membangun Wait-For Graph dari Resource Allocation Graph:"]

    for p, r in sorted(graph.waiting.items()):
        owner = graph.held_by.get(r)
        if owner and owner != p:
            log.append(f"  {p} menunggu {r}, yang dipegang {owner}  =>  {p} -> {owner}")
        elif owner == p:
            log.append(f"  {p} menunggu {r} yang dipegangnya sendiri (diabaikan)")
        else:
            log.append(f"  {p} menunggu {r}, tapi {r} bebas - tidak ada sisi")

    edges = [f"{a} -> {b}" for a, lst in wfg.items() for b in lst]
    log.append(f"Sisi Wait-For Graph: {edges if edges else 'tidak ada'}")

    cycles = find_cycles(wfg)
    log.append("")
    if cycles:
        log.append(f"DEADLOCK TERDETEKSI - ditemukan {len(cycles)} siklus:")
        for c in cycles:
            log.append(f"  {' -> '.join(c)}")
        involved = sorted({p for c in cycles for p in c})
        log.append(f"Proses yang terlibat: {', '.join(involved)}")
        log.append(
            "Keempat syarat Coffman terpenuhi, termasuk circular wait "
            "yang ditunjukkan siklus di atas."
        )
    else:
        involved = []
        log.append("TIDAK ADA DEADLOCK - Wait-For Graph bebas siklus (asiklik).")

    return {
        "deadlock": bool(cycles),
        "cycles": cycles,
        "involved": involved,
        "wait_for_graph": wfg,
        "log": log,
    }


# ======================================================================
# 2b. DETECTION - banyak instance per sumber daya
# ======================================================================


@dataclass
class MultiInstanceState:
    """Keadaan sistem untuk deteksi dengan banyak instance.

    allocation : n x m, yang sedang dipegang
    request    : n x m, yang SEDANG diminta sekarang (bukan kebutuhan maks)
    available  : vektor m, yang masih bebas
    """

    processes: list[str]
    resources: list[str]
    allocation: list[list[int]]
    request: list[list[int]]
    available: list[int]

    def __post_init__(self) -> None:
        n, m = len(self.processes), len(self.resources)
        if len(self.allocation) != n or len(self.request) != n:
            raise ValueError("jumlah baris harus sama dengan jumlah proses")
        if len(self.available) != m:
            raise ValueError("panjang available harus sama dengan jumlah sumber daya")

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
    """Detection Algorithm untuk banyak instance.

    Mirip Safety Algorithm, dengan DUA perbedaan penting:
      1. Memakai Request (permintaan nyata), bukan Need (kebutuhan maks).
      2. Proses dengan Allocation nol langsung ditandai selesai, karena
         ia tidak memegang apa pun sehingga tidak bisa ikut memblokir.

    Proses yang pada akhirnya tidak bisa ditandai selesai adalah proses
    yang berada dalam keadaan deadlock.
    """
    n, m = len(state.processes), len(state.resources)
    work = state.available[:]
    finish = [all(v == 0 for v in state.allocation[i]) for i in range(n)]
    order: list[str] = []
    log: list[str] = [f"Mulai. Work = Available = {work}"]

    for i in range(n):
        if finish[i]:
            log.append(
                f"  {state.processes[i]} tidak memegang sumber daya apa pun "
                f"-> langsung ditandai selesai"
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
            f"-> permintaannya bisa dipenuhi"
        )
        work = [work[j] + state.allocation[i][j] for j in range(m)]
        finish[i] = True
        order.append(state.processes[i])
        log.append(
            f"  {state.processes[i]} selesai, melepas {state.allocation[i]} "
            f"-> Work menjadi {work}"
        )

    deadlocked = [state.processes[i] for i in range(n) if not finish[i]]
    log.append("")
    if deadlocked:
        log.append(f"DEADLOCK TERDETEKSI. Proses dalam deadlock: {', '.join(deadlocked)}")
        for i in range(n):
            if not finish[i]:
                kurang = [
                    f"{state.resources[j]} (minta {state.request[i][j]}, ada {work[j]})"
                    for j in range(m)
                    if state.request[i][j] > work[j]
                ]
                log.append(
                    f"  {state.processes[i]} menunggu: {'; '.join(kurang)} "
                    f"sambil memegang {state.allocation[i]}"
                )
        log.append(
            "Tidak ada urutan eksekusi yang bisa menyelesaikan proses-proses ini."
        )
    else:
        log.append(
            f"TIDAK ADA DEADLOCK. Semua proses bisa selesai dengan urutan: "
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
    """Pulihkan dari deadlock dengan mematikan proses korban satu per satu.

    Pilihan strategi pemilihan korban:
      "most_resources"  - matikan yang memegang paling banyak sumber daya.
                          Paling cepat memulihkan sistem.
      "fewest_resources"- matikan yang memegang paling sedikit.
                          Kerugian per korban kecil, tapi mungkin perlu
                          mematikan lebih banyak proses.
      "first"           - matikan yang indeksnya paling awal. Paling
                          sederhana tapi sewenang-wenang.

    Di sistem nyata pemilihan korban juga mempertimbangkan prioritas proses,
    sudah berapa lama ia berjalan, dan apakah ia bisa di-restart dengan aman.
    Proses yang sedang menulis ke basis data misalnya, tidak boleh
    sembarangan dimatikan karena bisa meninggalkan data setengah jadi.
    """
    valid = ("most_resources", "fewest_resources", "first")
    if strategy not in valid:
        raise ValueError(f"strategi harus salah satu dari {valid}")

    work_state = state.copy()
    victims: list[dict] = []
    log: list[str] = []
    rounds = 0

    while True:
        rounds += 1
        det = detect_multi_instance(work_state)
        if not det["deadlock"]:
            log.append(
                f"Putaran {rounds}: tidak ada deadlock lagi. Pemulihan selesai."
            )
            break
        if rounds > len(state.processes) + 1:
            log.append("Berhenti - terlalu banyak putaran (seharusnya tidak terjadi).")
            break

        stuck = det["deadlocked_processes"]
        log.append(f"Putaran {rounds}: deadlock pada {', '.join(stuck)}")

        idxs = [work_state.processes.index(p) for p in stuck]
        if strategy == "most_resources":
            vi = max(idxs, key=lambda i: (sum(work_state.allocation[i]), -i))
            why = "memegang sumber daya paling banyak"
        elif strategy == "fewest_resources":
            vi = min(idxs, key=lambda i: (sum(work_state.allocation[i]), i))
            why = "memegang sumber daya paling sedikit"
        else:
            vi = min(idxs)
            why = "indeks paling awal"

        name = work_state.processes[vi]
        freed = work_state.allocation[vi][:]
        log.append(
            f"  Korban dipilih: {name} ({why}, memegang {freed})"
        )

        for j in range(len(work_state.resources)):
            work_state.available[j] += freed[j]
            work_state.allocation[vi][j] = 0
            work_state.request[vi][j] = 0

        log.append(f"  {name} dimatikan. Available menjadi {work_state.available}")
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
            f"Deadlock diselesaikan dengan mematikan {len(victims)} proses "
            f"({', '.join(v['process'] for v in victims) or 'tidak ada'}) "
            f"memakai strategi '{strategy}'."
        )
        if victims
        else "Tidak ada deadlock, tidak ada proses yang perlu dimatikan.",
    }


def compare_recovery_strategies(state: MultiInstanceState) -> list[dict]:
    """Bandingkan ketiga strategi pemilihan korban pada keadaan yang sama."""
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
# Contoh data
# ======================================================================


def deadlocked_graph() -> ResourceGraph:
    """Siklus sederhana: P1 -> P2 -> P3 -> P1."""
    return ResourceGraph(
        processes=["P1", "P2", "P3"],
        resources=["R1", "R2", "R3"],
        held_by={"R1": "P1", "R2": "P2", "R3": "P3"},
        waiting={"P1": "R2", "P2": "R3", "P3": "R1"},
    )


def safe_graph() -> ResourceGraph:
    """Rantai tunggu tanpa siklus: P1 -> P2 -> P3, P3 tidak menunggu."""
    return ResourceGraph(
        processes=["P1", "P2", "P3"],
        resources=["R1", "R2", "R3"],
        held_by={"R1": "P1", "R2": "P2", "R3": "P3"},
        waiting={"P1": "R2", "P2": "R3"},
    )


def deadlocked_multi() -> MultiInstanceState:
    """Keadaan deadlock dengan banyak instance.

    Available [0,0,0] dan setiap proses meminta sesuatu yang tidak ada,
    sementara semuanya memegang sumber daya. Tidak ada yang bisa maju.
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
    """Keadaan yang bisa selesai sendiri tanpa recovery (contoh negatif)."""
    return MultiInstanceState(
        processes=["P0", "P1", "P2"],
        resources=["A", "B"],
        allocation=[[1, 0], [0, 1], [1, 1]],
        request=[[0, 1], [1, 0], [0, 0]],
        available=[1, 1],
    )


if __name__ == "__main__":
    print("=" * 72)
    print("BAGIAN 1 - OSTRICH ALGORITHM")
    print("=" * 72)
    o = ostrich_algorithm(deadlock_detected=True)
    print(f"Tindakan        : {o['action_taken']}")
    print(f"Overhead        : {o['overhead']}")
    print(f"Penjelasan      : {o['explanation']}")
    print(f"Cocok dipakai   : {o['when_appropriate']}")
    print(f"Tidak boleh di  : {o['when_unacceptable']}")

    print()
    print("=" * 72)
    print("BAGIAN 2a - DETEKSI DENGAN WAIT-FOR GRAPH (instance tunggal)")
    print("=" * 72)
    print("\nKASUS A - ada siklus")
    print("-" * 72)
    for line in detect_single_instance(deadlocked_graph())["log"]:
        print(line)

    print("\nKASUS B - tidak ada siklus")
    print("-" * 72)
    for line in detect_single_instance(safe_graph())["log"]:
        print(line)

    print()
    print("=" * 72)
    print("BAGIAN 2b - DETEKSI DENGAN BANYAK INSTANCE")
    print("=" * 72)
    dm = deadlocked_multi()
    print(f"{'Proses':<8} {'Allocation':<12} {'Request':<12}")
    for i, p in enumerate(dm.processes):
        print(f"{p:<8} {str(dm.allocation[i]):<12} {str(dm.request[i]):<12}")
    print(f"Available: {dm.available}\n")
    for line in detect_multi_instance(dm)["log"]:
        print(line)

    print("\nPEMBANDING - keadaan yang TIDAK deadlock")
    print("-" * 72)
    for line in detect_multi_instance(recoverable_multi())["log"]:
        print(line)

    print()
    print("=" * 72)
    print("BAGIAN 3 - RECOVERY DENGAN TERMINASI KORBAN")
    print("=" * 72)
    rec = recover_by_termination(dm, strategy="most_resources")
    for line in rec["log"]:
        print(line)
    print()
    print(rec["summary"])

    print()
    print("PERBANDINGAN STRATEGI PEMILIHAN KORBAN")
    print("-" * 72)
    print(f"{'Strategi':<20} {'Jumlah korban':<15} {'Korban':<25} Berhasil")
    for c in compare_recovery_strategies(dm):
        print(
            f"{c['strategy']:<20} {c['victim_count']:<15} "
            f"{', '.join(c['victims']):<25} {'ya' if c['resolved'] else 'tidak'}"
        )
