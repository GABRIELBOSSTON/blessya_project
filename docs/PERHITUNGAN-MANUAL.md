# Perhitungan manual inti

Data: P1 datang 0 lama 5; P2 datang 1 lama 3; P3 datang 2 lama 1.
Seluruh waktu dalam satuan simulasi. Tidak ada biaya perpindahan atau I/O.

## FCFS

Gantt: P1 [0,5), P2 [5,8), P3 [8,9).

| Proses | Datang | Lama | Mulai pertama | Selesai | Turnaround | Menunggu | Respons |
|---|---:|---:|---:|---:|---:|---:|---:|
| P1 | 0 | 5 | 0 | 5 | 5 | 0 | 0 |
| P2 | 1 | 3 | 5 | 8 | 7 | 4 | 4 |
| P3 | 2 | 1 | 8 | 9 | 7 | 6 | 6 |

Turnaround = selesai − datang; menunggu = turnaround − lama;
respons = mulai pertama − datang. Rata-rata menunggu 10/3 = 3,33;
turnaround 19/3 = 6,33; respons 10/3 = 3,33. Pergantian antarproses 2.

## Round Robin quantum 2

1. t=0: P1 berjalan sampai 2, tersisa 3.
2. t=2: P2 dan P3 sudah tiba. Antrean P2, P3, P1. P3 datang tepat pada t=2,
   bersamaan dengan habisnya quantum P1. Aturan program: proses yang baru datang
   dimasukkan ke antrean lebih dahulu, baru kemudian P1 dikembalikan ke belakang.
3. P2 berjalan 2–4, tersisa 1. Antrean P3, P1, P2.
4. P3 berjalan 4–5 lalu selesai.
5. P1 berjalan 5–7, tersisa 1. Antrean P2, P1.
6. P2 berjalan 7–8 lalu selesai.
7. P1 berjalan 8–9 lalu selesai.

| Proses | Mulai pertama | Selesai | Turnaround | Menunggu | Respons |
|---|---:|---:|---:|---:|---:|
| P1 | 0 | 9 | 9 | 4 | 0 |
| P2 | 2 | 8 | 7 | 4 | 1 |
| P3 | 4 | 5 | 3 | 2 | 2 |

Menunggu rata-rata (4+4+2)/3 = 3,33. Turnaround (9+7+3)/3 = 6,33.
Respons (0+1+2)/3 = 1. Ada 5 pergantian antarproses.

## Kasus khusus

Satu proses A datang 0, lama 5, quantum 2: giliran A [0,2), A [2,4), A [4,5).
Batas giliran terlihat tetapi pergantian antarproses = 0.

P1 datang 5, lama 3: IDLE [0,5), P1 [5,8). Waktu tunggu 0,
turnaround 3, respons 0. Utilisasi model 3/8 × 100 = 37,5%.

Arrival sama: nama diurutkan sebagai teks. Dengan urutan input P2 lalu P10,
keduanya datang 0, P10 dilayani terlebih dahulu. Ini aturan tie-break yang
harus disebutkan agar contoh manual dan program menggunakan aturan sama.

## Producer–Consumer

Aturan yang harus selalu benar (invariant): 0 ≤ isi buffer ≤ kapasitas.
Urutan kerja thread tidak dijamin sama pada setiap percobaan.
Pada akhir percobaan berhasil: diproduksi = dikonsumsi dan sisa = 0.

Contoh alur yang sah untuk kapasitas 2: [] → [A] → [A,B] → [B] → [].
Tindakan berturut-turut adalah produksi A, produksi B, konsumsi A, konsumsi B.
Contoh ini ilustrasi manual; waktu dan jumlah kejadian menunggu di runtime
harus diambil dari rekaman aktual, bukan dari ilustrasi ini.

Tes `test_core.py` memeriksa contoh scheduling di atas dan merekonstruksi
antrean dari log aktual agar snapshot, urutan barang, serta jumlahnya cocok.
