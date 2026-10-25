# Perhitungan Manual

Berkas ini menghitung ulang hasil program **dengan tangan**, agar bisa
dibuktikan bahwa angka yang dikeluarkan program memang benar dan bukan
kebetulan.

Rumus yang dipakai di seluruh dokumen:

```
Turnaround Time = Completion Time - Arrival Time
Waiting Time    = Turnaround Time - Burst Time
Response Time   = waktu pertama kali dapat CPU - Arrival Time
```

---

## 1. Data Uji Utama

| Proses | Arrival | Burst | Prioritas |
|---|---|---|---|
| P1 | 0 | 8 | 3 |
| P2 | 1 | 4 | 1 |
| P3 | 2 | 9 | 4 |
| P4 | 3 | 5 | 2 |

Total burst = 8 + 4 + 9 + 5 = **26**. Karena P1 tiba di t=0, CPU tidak pernah
idle, sehingga total waktu seluruh algoritma juga **26** dan utilisasi CPU
**100%**.

---

## 2. FCFS

Urutan = urut kedatangan: P1, P2, P3, P4.

```
P1: 0 -> 8        P2: 8 -> 12       P3: 12 -> 21      P4: 21 -> 26
```

| Proses | Completion | Turnaround | Waiting | Response |
|---|---|---|---|---|
| P1 | 8 | 8 − 0 = 8 | 8 − 8 = **0** | 0 |
| P2 | 12 | 12 − 1 = 11 | 11 − 4 = **7** | 7 |
| P3 | 21 | 21 − 2 = 19 | 19 − 9 = **10** | 10 |
| P4 | 26 | 26 − 3 = 23 | 23 − 5 = **18** | 18 |

```
Avg waiting    = (0 + 7 + 10 + 18) / 4 = 35 / 4 = 8.75
Avg turnaround = (8 + 11 + 19 + 23) / 4 = 61 / 4 = 15.25
```

Keluaran program: `AvgWait=8.75  ATT=15.25` — **cocok**.

---

## 3. SRTF (preemptive)

Ini perhitungan paling rumit, dan sekaligus kasus yang dipakai sebagai
pembanding dengan buku teks.

Jalannya keputusan, diperiksa pada setiap satuan waktu:

| t | Proses siap (sisa burst) | Dipilih | Alasan |
|---|---|---|---|
| 0 | P1(8) | P1 | satu-satunya yang sudah tiba |
| 1 | P1(7), P2(4) | **P2** | 4 < 7 → P1 di-preempt |
| 2 | P1(7), P2(3), P3(9) | P2 | 3 paling kecil |
| 3 | P1(7), P2(2), P3(9), P4(5) | P2 | 2 paling kecil |
| 4 | P1(7), P2(1), P3(9), P4(5) | P2 | 1 paling kecil |
| 5 | P1(7), P3(9), P4(5) | **P4** | P2 selesai; 5 paling kecil |
| 6–9 | P4 berlanjut | P4 | tetap paling kecil |
| 10 | P1(7), P3(9) | **P1** | P4 selesai; 7 < 9 |
| 11–16 | P1 berlanjut | P1 | |
| 17 | P3(9) | **P3** | P1 selesai, sisa P3 saja |

Gantt chart hasilnya:

```
P1(0-1)  P2(1-5)  P4(5-10)  P1(10-17)  P3(17-26)
```

| Proses | Completion | Turnaround | Waiting | Response |
|---|---|---|---|---|
| P1 | 17 | 17 − 0 = 17 | 17 − 8 = **9** | 0 − 0 = 0 |
| P2 | 5 | 5 − 1 = 4 | 4 − 4 = **0** | 1 − 1 = 0 |
| P3 | 26 | 26 − 2 = 24 | 24 − 9 = **15** | 17 − 2 = 15 |
| P4 | 10 | 10 − 3 = 7 | 7 − 5 = **2** | 5 − 3 = 2 |

```
Avg waiting = (9 + 0 + 15 + 2) / 4 = 26 / 4 = 6.5
```

Keluaran program: `AvgWait=6.5`, total waktu 26 — **cocok**, dan cocok pula
dengan hasil baku di Silberschatz, *Operating System Concepts*.

**Perbandingan:** SRTF 6.5 vs FCFS 8.75 pada data yang sama persis. Perbaikan
sebesar 2.25 satuan waktu, atau sekitar **26%**, murni berasal dari pergantian
algoritma.

---

## 4. Convoy Effect pada FCFS

Data uji berbeda, untuk menunjukkan kasus terburuk FCFS:

| Proses | Arrival | Burst |
|---|---|---|
| P1 | 0 | 24 |
| P2 | 0 | 3 |
| P3 | 0 | 3 |

**FCFS** — urut kedatangan P1, P2, P3:

```
P1: 0 -> 24      P2: 24 -> 27      P3: 27 -> 30

Waiting: P1=0, P2=24, P3=27
Avg waiting = (0 + 24 + 27) / 3 = 51 / 3 = 17.0
```

**SJF** — urut burst terpendek P2, P3, P1:

```
P2: 0 -> 3       P3: 3 -> 6        P1: 6 -> 30

Waiting: P2=0, P3=3, P1=6
Avg waiting = (0 + 3 + 6) / 3 = 9 / 3 = 3.0
```

Keluaran program: FCFS 17.0, SJF 3.0 — **cocok**.

Avg waiting turun dari 17.0 ke 3.0, membaik **hampir enam kali**, hanya dengan
mengubah urutan. Inilah *convoy effect*: satu proses panjang di depan menahan
dua proses pendek di belakangnya, seperti satu truk lambat menahan antrean di
jalan satu jalur.

---

## 5. Round Robin dan Pengaruh Quantum

Data uji: tiga proses identik, semuanya tiba di t=0 dengan burst 10.

**Quantum = 10** (sama dengan burst, jadi tidak pernah ada preemption):

```
P1: 0 -> 10      P2: 10 -> 20      P3: 20 -> 30

Waiting: P1=0, P2=10, P3=20  ->  avg = 30/3 = 10.0
Response: 0, 10, 20          ->  avg = 10.0
Context switch: 0
```

Hasilnya **identik dengan FCFS**, karena quantum yang lebih besar atau sama
dengan burst terpanjang membuat Round Robin berubah menjadi FCFS. Program
menguji invarian ini di `tests/test_scheduling.py` dengan membandingkan
`round_robin(quantum=30)` terhadap `fcfs()` secara langsung.

**Quantum = 1** (preemption semaksimal mungkin):

Urutan jatah: P1,P2,P3,P1,P2,P3,... sampai ketiganya habis.
Setiap proses pertama kali dapat CPU pada t = 0, 1, 2.

```
Response: 0, 1, 2  ->  avg = 3/3 = 1.0
```

Response time turun dari 10.0 menjadi 1.0, tetapi context switch melonjak
menjadi 27.

**Tabel lengkap dari program** (`py run.py demo`, memakai data uji utama):

| Quantum | Avg Waiting | Avg Response | Context Switch |
|---|---|---|---|
| 1 | 12.5 | 0.75 | 22 |
| 2 | 12.75 | 2.0 | 10 |
| 3 | 13.5 | 3.0 | 6 |
| 5 | 11.0 | 5.5 | 2 |
| 8 | 9.75 | 8.5 | 1 |
| 12 | 8.75 | 8.75 | 0 |

Perhatikan baris terakhir: pada quantum 12, avg waiting **8.75** — angka yang
sama persis dengan FCFS di Bagian 2. Batas teoretis terbukti secara empiris.

---

## 6. Banker's Algorithm

Contoh baku Silberschatz. Sumber daya: A=10, B=5, C=7.

| Proses | Allocation | Max | Need = Max − Alloc |
|---|---|---|---|
| P0 | 0 1 0 | 7 5 3 | 7 4 3 |
| P1 | 2 0 0 | 3 2 2 | 1 2 2 |
| P2 | 3 0 2 | 9 0 2 | 6 0 0 |
| P3 | 2 1 1 | 2 2 2 | 0 1 1 |
| P4 | 0 0 2 | 4 3 3 | 4 3 1 |

**Pemeriksaan total sumber daya:**

```
Terpakai A = 0+2+3+2+0 = 7,  Available A = 3  ->  total 10  OK
Terpakai B = 1+0+0+1+0 = 2,  Available B = 3  ->  total  5  OK
Terpakai C = 0+0+2+1+2 = 5,  Available C = 2  ->  total  7  OK
```

**Safety Algorithm**, Work dimulai dari Available = [3,3,2]:

| Langkah | Work | Proses diperiksa | Need | Bisa? | Work sesudahnya |
|---|---|---|---|---|---|
| 1 | [3,3,2] | P0 | [7,4,3] | tidak (7>3) | — |
| 2 | [3,3,2] | P1 | [1,2,2] | **ya** | [3,3,2]+[2,0,0] = [5,3,2] |
| 3 | [5,3,2] | P0 | [7,4,3] | tidak (7>5) | — |
| 4 | [5,3,2] | P2 | [6,0,0] | tidak (6>5) | — |
| 5 | [5,3,2] | P3 | [0,1,1] | **ya** | [5,3,2]+[2,1,1] = [7,4,3] |
| 6 | [7,4,3] | P0 | [7,4,3] | **ya** (pas) | [7,4,3]+[0,1,0] = [7,5,3] |
| 7 | [7,5,3] | P2 | [6,0,0] | **ya** | [7,5,3]+[3,0,2] = [10,5,5] |
| 8 | [10,5,5] | P4 | [4,3,1] | **ya** | [10,5,5]+[0,0,2] = [10,5,7] |

Semua proses selesai → **SAFE**.

Safe sequence: `< P1 → P3 → P0 → P2 → P4 >`

Work akhir [10,5,7] sama dengan total sumber daya sistem — semuanya kembali.

> **Catatan penting:** buku teks sering menyebut safe sequence
> `< P1, P3, P4, P2, P0 >`. Keduanya **sama-sama benar**. Sebuah keadaan bisa
> punya lebih dari satu safe sequence; program ini memeriksa proses secara
> berurutan dari indeks terkecil dan mengambil yang pertama cocok, sehingga
> menemukan urutan yang berbeda. Yang penting dan yang diuji adalah
> kesimpulannya: **safe atau unsafe**.

### Skenario P4 meminta [3,3,0]

**Cek 1** — Request ≤ Need? [3,3,0] ≤ [4,3,1] → **lulus**.

**Cek 2** — Request ≤ Available? [3,3,0] ≤ [3,3,2] → **lulus**, sumber daya cukup.

**Cek 3** — alokasi percobaan:

```
Available  = [3,3,2] − [3,3,0] = [0,0,2]
Alloc P4   = [0,0,2] + [3,3,0] = [3,3,2]
Need P4    = [4,3,3] − [3,3,2] = [1,0,1]
```

Safety check dengan Work = [0,0,2]:

| Proses | Need | Work [0,0,2] | Bisa? |
|---|---|---|---|
| P0 | [7,4,3] | A: 7>0 | tidak |
| P1 | [1,2,2] | A: 1>0 | tidak |
| P2 | [6,0,0] | A: 6>0 | tidak |
| P3 | [0,1,1] | B: 1>0 | tidak |
| P4 | [1,0,1] | A: 1>0 | tidak |

Tidak ada proses yang bisa jalan → **UNSAFE** → permintaan **DITOLAK**, alokasi
percobaan dibatalkan.

**Inilah inti deadlock avoidance:** sumber dayanya **tersedia** (Cek 2 lulus),
tetapi permintaan tetap ditolak karena sesudahnya sistem tidak bisa lagi
menjamin semua proses selesai. Avoidance mengorbankan sebagian pemanfaatan
sumber daya untuk mendapat jaminan.

---

## 7. Deteksi Deadlock

### 7.1 Instance tunggal — Wait-For Graph

Keadaan:

| Sumber daya | Dipegang | | Proses | Menunggu |
|---|---|---|---|---|
| R1 | P1 | | P1 | R2 |
| R2 | P2 | | P2 | R3 |
| R3 | P3 | | P3 | R1 |

Ubah menjadi Wait-For Graph dengan menghilangkan node sumber daya:

```
P1 menunggu R2, R2 dipegang P2   ->  P1 -> P2
P2 menunggu R3, R3 dipegang P3   ->  P2 -> P3
P3 menunggu R1, R1 dipegang P1   ->  P3 -> P1
```

Telusuri dari P1: P1 → P2 → P3 → **P1**. Kembali ke titik awal, berarti ada
siklus → **DEADLOCK**.

Bandingkan dengan keadaan aman: hapus baris "P3 menunggu R1". Maka graf menjadi
P1 → P2 → P3, berhenti di P3 yang tidak menunggu apa pun. Tidak ada siklus →
tidak ada deadlock. P3 akan selesai, melepas R3, lalu P2 bisa jalan,
dan seterusnya.

Teorema yang mendasarinya: untuk sumber daya instance tunggal, deadlock terjadi
**jika dan hanya jika** wait-for graph memuat siklus.

### 7.2 Banyak instance

| Proses | Allocation | Request |
|---|---|---|
| P0 | 0 1 0 | 0 0 1 |
| P1 | 2 0 0 | 2 0 2 |
| P2 | 3 0 3 | 0 0 1 |
| P3 | 2 1 1 | 1 0 0 |

Available = [0,0,0].

Work mulai dari [0,0,0]. Tidak ada proses dengan Allocation nol, jadi tidak ada
yang bisa langsung ditandai selesai.

| Proses | Request | Work [0,0,0] | Bisa? |
|---|---|---|---|
| P0 | [0,0,1] | C: 1>0 | tidak |
| P1 | [2,0,2] | A: 2>0 | tidak |
| P2 | [0,0,1] | C: 1>0 | tidak |
| P3 | [1,0,0] | A: 1>0 | tidak |

Tidak ada yang bisa maju → **keempat proses dalam deadlock**.

> **Perbedaan penting dari Banker's:** di sini yang dipakai adalah **Request**
> (yang sedang diminta sekarang), bukan **Need** (kebutuhan maksimal).
> Deteksi memeriksa apa yang *sedang* terjadi; avoidance memperkirakan apa yang
> *mungkin* terjadi.

### 7.3 Recovery

Strategi `most_resources` — matikan yang memegang paling banyak:

```
Total yang dipegang:  P0=1, P1=2, P2=6, P3=4   ->  korban = P2
```

Setelah P2 dimatikan, sumber dayanya dilepas:

```
Available = [0,0,0] + [3,0,3] = [3,0,3]
```

Periksa ulang dengan Work = [3,0,3]:

| Proses | Request | Bisa? | Work sesudahnya |
|---|---|---|---|
| P0 | [0,0,1] | **ya** | [3,0,3]+[0,1,0] = [3,1,3] |
| P1 | [2,0,2] | **ya** | [3,1,3]+[2,0,0] = [5,1,3] |
| P3 | [1,0,0] | **ya** | [5,1,3]+[2,1,1] = [7,2,4] |

Semua selesai → deadlock teratasi dengan **satu** korban.

Bandingkan dengan `fewest_resources`, yang mematikan P0 lebih dulu (hanya
memegang 1), lalu masih perlu mematikan P1 — jadi **dua** korban. Program
mengonfirmasi perbandingan ini:

| Strategi | Jumlah korban | Korban |
|---|---|---|
| most_resources | 1 | P2 |
| fewest_resources | 2 | P0, P1 |
| first | 2 | P0, P1 |

---

## 8. Ringkasan Verifikasi

| Yang dihitung | Manual | Program | Status |
|---|---|---|---|
| FCFS avg waiting (data utama) | 8.75 | 8.75 | cocok |
| FCFS avg turnaround | 15.25 | 15.25 | cocok |
| SRTF avg waiting | 6.5 | 6.5 | cocok |
| SRTF total waktu | 26 | 26 | cocok |
| FCFS convoy avg waiting | 17.0 | 17.0 | cocok |
| SJF convoy avg waiting | 3.0 | 3.0 | cocok |
| RR quantum besar = FCFS | 8.75 | 8.75 | cocok |
| Banker's contoh baku | SAFE | SAFE | cocok |
| Banker's total sistem | [10,5,7] | [10,5,7] | cocok |
| P4 minta [3,3,0] | ditolak, unsafe | ditolak, unsafe | cocok |
| Wait-for graph siklus | P1→P2→P3→P1 | P1→P2→P3→P1 | cocok |
| Deteksi multi-instance | 4 proses macet | 4 proses macet | cocok |
| Recovery most_resources | 1 korban (P2) | 1 korban (P2) | cocok |

Seluruh perhitungan manual cocok dengan keluaran program. Pemeriksaan ini
juga dikodekan sebagai pengujian otomatis di `tests/`, sehingga akan
memberi peringatan bila ada perubahan kode yang merusaknya.
