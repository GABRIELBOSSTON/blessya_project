# Simulator Sistem Operasi

Alat peraga interaktif untuk tiga materi mata kuliah Sistem Operasi:
**Process Scheduling**, **Process/Threads & IPC**, dan **Deadlock**.

Logika simulasi ditulis dengan Python, visualisasi dengan HTML/CSS/JavaScript.
**Tanpa dependency eksternal** — hanya pustaka standar Python.

> Kalau Anda bukan programmer, baca [`OWNER.md`](OWNER.md) saja. Berkas itu
> menjelaskan semuanya tanpa menyentuh kode.

---

## Menjalankan

```bash
cd D:\blessya
py run.py
```

Browser terbuka otomatis di <http://127.0.0.1:8000>.

| Perintah | Keterangan |
|---|---|
| `py run.py` | Mode web (bawaan) |
| `py run.py demo` | Jalankan semua demo di terminal |
| `py run.py test` | Jalankan 79 pemeriksaan kebenaran |
| `py run.py --port 9000` | Ganti nomor port |
| `py run.py --no-browser` | Tanpa membuka browser |

Kebutuhan: **Python 3.10+** (memakai sintaks `X | None`). Diuji pada Python 3.13.1.

---

## Struktur

```
src/
├── server.py                    HTTP server + 6 endpoint JSON
├── scheduling/
│   ├── models.py                Process, Segment, Metrics, ScheduleResult
│   ├── algorithms.py            FCFS, SJF, SRTF, Round Robin, Priority
│   └── demo.py                  keluaran terminal + Gantt chart ASCII
├── ipc/
│   ├── race_condition.py        pembuktian lost update dengan thread nyata
│   ├── producer_consumer.py     bounded buffer: 2 semaphore + 1 mutex
│   └── dining_philosophers.py   3 strategi, deteksi circular wait
└── deadlock/
    ├── bankers.py               safety algorithm + resource-request algorithm
    └── detection.py             wait-for graph, multi-instance, recovery, ostrich

web/
├── index.html                   4 tab
├── css/style.css
└── js/{util,scheduling,ipc,deadlock,app}.js

tests/
├── test_scheduling.py           20 pemeriksaan, dicocokkan dengan buku teks
└── test_api.py                  59 pemeriksaan lewat HTTP sungguhan
```

---

## Materi yang diimplementasikan

### 1. Process Scheduling

Enam algoritma pada data masukan yang sama, sehingga perbandingannya adil:

| Algoritma | Preemptive | Catatan |
|---|---|---|
| FCFS | tidak | memperlihatkan convoy effect |
| SJF | tidak | optimal untuk avg waiting time |
| SRTF | ya | SJF versi preemptive, simulasi tick-per-tick |
| Round Robin | ya | quantum dapat diatur 1–20 |
| Priority | tidak | tanpa aging, agar starvation teramati |
| Priority | ya | |

Keluaran: Gantt chart, per-proses (completion, turnaround, waiting, response),
rata-rata, utilisasi CPU, jumlah context switch, dan **log keputusan scheduler
langkah demi langkah**.

### 2. Process, Threads & IPC

Semuanya memakai `threading` — thread sistem operasi sungguhan, bukan simulasi.

- **Race condition** — `UnsafeCounter` vs `SafeCounter`. Yield dipaksa di antara
  READ dan WRITE agar bug laten jadi deterministik; mode "alami" disediakan
  untuk menunjukkan bahwa kode yang sama salahnya bisa lolos pengujian.
- **Producer-Consumer** — `Semaphore(empty)`, `Semaphore(full)`, `Lock(mutex)`.
  Setiap kejadian dicatat dengan timestamp dan isi buffer.
- **Dining Philosophers** — strategi `naive` (deadlock), `ordering` (resource
  ordering memutus circular wait), `waiter` (semaphore membatasi N-1 filsuf).
  Circular wait dicari dengan penelusuran wait-for graph.

### 3. Deadlock

- **Banker's Algorithm** — safety algorithm + resource-request algorithm dengan
  ketiga jalur keputusan: `safe` (dikabulkan), `must_wait` (ditunda),
  `unsafe` (ditolak walau sumber daya tersedia), `exceeds_need` (error proses).
- **Detection** — wait-for graph + pencarian siklus DFS tiga-warna untuk
  instance tunggal; algoritma berbasis matriks `Request` untuk banyak instance.
- **Recovery** — terminasi korban berulang dengan tiga strategi pemilihan
  (`most_resources`, `fewest_resources`, `first`), beserta perbandingannya.
- **Ostrich Algorithm** — diimplementasikan sebagai fungsi nyata agar bisa
  dibandingkan setara, bukan hanya dibahas sebagai teori.

---

## API

Semua endpoint menerima `POST` dengan body JSON dan mengembalikan JSON.
Kesalahan masukan dibalas `400` dengan pesan yang bisa dibaca pengguna.

| Endpoint | Parameter utama |
|---|---|
| `POST /api/scheduling` | `algorithm`, `processes[]`, `quantum`, `preemptive` |
| `POST /api/ipc/race` | `threads`, `increments`, `trials`, `force_preemption` |
| `POST /api/ipc/producer-consumer` | `capacity`, `producers`, `consumers`, `items` |
| `POST /api/ipc/philosophers` | `strategy` (`naive`/`ordering`/`waiter`/`all`), `meals` |
| `POST /api/deadlock/bankers` | `example`, `allocation`/`maximum`/`available`, `request` |
| `POST /api/deadlock/detection` | `kind` (`graph`/`multi`/`ostrich`), `example`, `strategy` |

Contoh:

```bash
curl -X POST http://127.0.0.1:8000/api/scheduling \
  -H "Content-Type: application/json" \
  -d '{"algorithm":"all","quantum":3,"processes":[{"pid":"P1","arrival":0,"burst":8}]}'
```

Semua masukan dibatasi di `src/server.py` (`LIMITS`) agar permintaan dari
browser tidak membuat server kewalahan. Nilai di luar batas **dipotong**, bukan
ditolak, kecuali untuk kesalahan yang memang perlu diberitahukan (nama proses
ganda, daftar kosong, algoritma tak dikenal).

---

## Pengujian

```bash
py run.py test
```

79 pemeriksaan, nol kegagalan. Yang dijamin:

- **Kecocokan dengan buku teks.** SRTF pada data Silberschatz menghasilkan
  Gantt `P1(0-1) P2(1-5) P4(5-10) P1(10-17) P3(17-26)` dan avg waiting 6.5.
  Banker's pada contoh baku menghasilkan safe state.
- **Invarian lintas algoritma.** `waiting == turnaround - burst` di keenam
  algoritma; total CPU terpakai selalu sama dengan total burst.
- **Invarian keamanan.** Isi buffer tidak pernah melebihi kapasitas, diperiksa
  pada **setiap** kejadian, bukan hanya di akhir. `SafeCounter` selalu tepat.
- **Perilaku batas.** Round Robin dengan quantum sangat besar menghasilkan
  angka identik dengan FCFS; quantum=1 memberi response time minimum.
- **Penanganan kesalahan.** JSON rusak, endpoint tak ada, path traversal
  (`/../run.py` → 403), burst=0, quantum=0, proses tak dikenal.

Perbedaan penting: hasil **scheduling dan deadlock deterministik**, sedangkan
hasil **IPC berubah antar-eksekusi** karena memakai thread nyata. Pengujian IPC
karena itu memeriksa *invarian* (dengan lock selalu benar, buffer tidak pernah
overflow), bukan nilai pasti.

---

## Keputusan desain

**Tanpa dependency eksternal.** Tidak ada `pip install`, tidak ada
`requirements.txt`. Setiap langkah pemasangan adalah satu langkah yang bisa
gagal di komputer lain; projek ini harus bisa dijalankan dengan satu perintah.
Konsekuensinya: Gantt chart digambar dengan flexbox CSS, bukan Chart.js, dan
graf digambar dengan SVG yang disusun manual, bukan D3.

**Log naratif, bukan hanya hasil akhir.** Setiap algoritma mengembalikan
`log[]` berisi alasan setiap keputusan (`"t=5: P2 DI-PREEMPT oleh P4 (sisa P4=2
< sisa P2=4)"`). Ini yang membedakan alat peraga dari kalkulator.

**Aging sengaja tidak diimplementasikan** di Priority Scheduling, agar
starvation bisa diamati dan dibahas.

**Preemption dipaksa di demo race condition**, dengan mode alami sebagai
pembanding. Dokumentasinya ada di docstring `src/ipc/race_condition.py`.
Tanpa paksaan, CPython jarang berpindah thread pada loop sempit sehingga bug
tidak teramati — dan fakta itu sendiri adalah temuan yang layak dilaporkan.

**Server hanya mendengarkan di 127.0.0.1**, tidak dapat diakses dari jaringan.

---

## Dokumentasi

| Berkas | Untuk siapa |
|---|---|
| [`OWNER.md`](OWNER.md) | Pembaca non-teknis. Lengkap, termasuk pemecahan masalah. |
| `README.md` | Pembaca teknis. Berkas ini. |
| [`docs/LAPORAN.md`](docs/LAPORAN.md) | Rangka bab laporan 20+ halaman |
| [`docs/PERHITUNGAN-MANUAL.md`](docs/PERHITUNGAN-MANUAL.md) | Verifikasi perhitungan dengan tangan |
| Docstring di tiap modul | Dasar teori materi yang bersangkutan |

---

## Rujukan

- Silberschatz, Galvin, Gagne. *Operating System Concepts*, 10th ed.
  Bab 5 (CPU Scheduling), 6–7 (Synchronization), 8 (Deadlocks).
- Tanenbaum, Bos. *Modern Operating Systems*, 4th ed.
  Bab 2 (Processes and Threads), 6 (Deadlocks).
- Coffman, Elphick, Shoshani (1971). *System Deadlocks*. — empat syarat deadlock.
