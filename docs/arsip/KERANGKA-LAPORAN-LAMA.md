# Rangka Laporan

Tugas mensyaratkan laporan **minimal 20 halaman** berisi penjelasan materi dan
dokumentasi sistem. Berkas ini adalah rangka bab beserta saran isi, perkiraan
halaman, dan bahan mana yang diambil dari program.

Total perkiraan di bawah: **24–30 halaman** (asumsi A4, Times New Roman 12,
spasi 1.5). Ada kelebihan dari syarat minimal, jadi ada ruang untuk memotong
bagian yang Anda rasa kurang perlu.

Cara mengambil bahan:

- `py run.py demo` → keluaran teks, bisa langsung di-copy ke Word
- `py run.py` → screenshot berwarna dari browser
- `py run.py test` → screenshot bukti pengujian

---

## BAB I — PENDAHULUAN (2 halaman)

**1.1 Latar Belakang**

Mulai dari masalah nyata, bukan dari definisi. Contoh pembuka: ketika pengguna
membuka browser, pemutar musik, dan pengolah kata sekaligus, ketiganya terasa
berjalan bersamaan padahal CPU hanya mengerjakan satu hal pada satu waktu.
Bagaimana sistem operasi mengaturnya? Lalu masuk ke kesulitan mempelajari
materi ini: diagram di buku bersifat statis sehingga sulit melihat akibat dari
perubahan parameter.

**1.2 Rumusan Masalah**

Tiga pertanyaan saja, sejajar dengan tiga materi:

1. Bagaimana pilihan algoritma penjadwalan memengaruhi kinerja sistem?
2. Mengapa thread yang berbagi memori memerlukan sinkronisasi, dan apa
   akibatnya bila tidak ada?
3. Bagaimana deadlock terjadi, dan bagaimana keempat pendekatan penanganannya
   dibandingkan?

**1.3 Tujuan** — membangun simulator yang memperlihatkan ketiganya secara
terukur dan dapat diperiksa.

**1.4 Batasan Masalah** — simulator edukatif, bukan sistem operasi; tiga materi
dari dua belas yang tersedia; sumber daya dan proses disimulasikan kecuali pada
bagian thread yang memakai thread sistem operasi sungguhan.

**1.5 Manfaat**

---

## BAB II — LANDASAN TEORI (7–9 halaman)

Bab paling panjang dan paling bernilai nilai. Setiap subbab diambil dari
docstring modul yang bersangkutan, lalu dikembangkan.

**2.1 Proses dan Thread** (1.5 hal)
Definisi proses, Process Control Block, diagram lima keadaan proses (new,
ready, running, waiting, terminated). Perbedaan proses dan thread, terutama
soal **ruang memori yang dibagi bersama** — ini pondasi untuk Bab 2.3.

**2.2 Penjadwalan Proses** (2.5 hal)
Mengapa penjadwalan diperlukan. Preemptive vs non-preemptive. Kriteria
penilaian: CPU utilization, throughput, turnaround time, waiting time, response
time. Lalu satu subbagian per algoritma (FCFS, SJF, SRTF, Round Robin,
Priority) berisi cara kerja, kelebihan, kekurangan. Tutup dengan pembahasan
convoy effect dan starvation.

> Sumber: `src/scheduling/algorithms.py`, docstring tiap fungsi.

**2.3 Sinkronisasi dan IPC** (2.5 hal)
Critical section problem dan tiga syaratnya (mutual exclusion, progress,
bounded waiting). Race condition: jelaskan bahwa `counter += 1` bukan operasi
atomic melalui penguraian READ–MODIFY–WRITE. Alat sinkronisasi: mutex,
semaphore, monitor — dan **mengapa semaphore dibutuhkan padahal sudah ada
mutex** (karena perlu *menghitung*, bukan sekadar mengizinkan). Dua masalah
klasik: Producer-Consumer dan Dining Philosophers.

> Sumber: docstring `src/ipc/race_condition.py` dan `producer_consumer.py`.

**2.4 Deadlock** (2.5 hal)
Definisi. Empat syarat Coffman, masing-masing dengan contoh. Resource
Allocation Graph. Lalu empat pendekatan penanganan: prevention, avoidance
(Banker's Algorithm, termasuk definisi safe state dan safe sequence),
detection & recovery, dan ostrich. Tegaskan satu hal yang sering salah
dipahami: **unsafe state bukan berarti deadlock**.

> Sumber: docstring `src/deadlock/bankers.py` dan `detection.py`.

---

## BAB III — PERANCANGAN SISTEM (3–4 halaman)

**3.1 Arsitektur**
Tiga lapis: lapisan simulasi (Python), lapisan API (HTTP + JSON), lapisan
tampilan (browser). Buat diagram kotak sederhana yang menunjukkan alirannya:
browser → POST JSON → server → modul simulasi → JSON → browser → gambar.

**3.2 Struktur Berkas**
Copy pohon direktori dari `README.md`, lalu jelaskan pembagian tanggung
jawabnya: tiap materi satu paket terpisah agar bisa diuji sendiri-sendiri.

**3.3 Struktur Data**
`Process`, `Segment`, `Metrics`, `ScheduleResult`, `BankerState`,
`MultiInstanceState`. Tabel berisi nama field dan artinya.

**3.4 Rancangan Antarmuka**
Empat tab, screenshot tampilan awal.

**3.5 Keputusan Perancangan dan Alasannya**

Ini subbab yang membedakan laporan bagus dari laporan sekadar jadi. Bahas
pilihan dan trade-off-nya:

| Keputusan | Alasan | Konsekuensi |
|---|---|---|
| Tanpa library eksternal | Setiap langkah pemasangan bisa gagal di komputer lain | Chart digambar manual dengan CSS/SVG |
| Setiap algoritma mencatat log naratif | Membedakan alat peraga dari kalkulator | Keluaran lebih besar |
| Aging tidak diimplementasikan | Agar starvation bisa diamati | Priority Scheduling tidak lengkap, dan ini disengaja |
| Preemption dipaksa di demo race | Bug laten jadi teramati setiap kali | Perlu dijelaskan agar tidak disalahpahami |

---

## BAB IV — IMPLEMENTASI DAN PENGUJIAN (7–9 halaman)

Bab inti dokumentasi. Pola yang sama untuk setiap materi: tampilkan kode
pentingnya (potongan saja, jangan seluruh berkas), tampilkan hasilnya,
lalu analisis.

### 4.1 Penjadwalan Proses (3 hal)

Data uji yang dipakai seluruh laporan:

| Proses | Arrival | Burst | Prioritas |
|---|---|---|---|
| P1 | 0 | 8 | 3 |
| P2 | 1 | 4 | 1 |
| P3 | 2 | 9 | 4 |
| P4 | 3 | 5 | 2 |

Untuk setiap algoritma: screenshot Gantt chart + tabel metrik. Lalu tabel
perbandingan keenam algoritma sekaligus.

**Analisis yang perlu ditulis** (jangan hanya menempel tabel):

- Algoritma mana terbaik untuk avg waiting time, mana untuk avg response time,
  dan **mengapa keduanya bisa berbeda**.
- Convoy effect pada FCFS. Perkuat dengan percobaan: ubah burst P1 menjadi 30
  dan tunjukkan avg waiting melonjak.
- Tabel pengaruh time quantum pada Round Robin (dari `py run.py demo`):

  | Quantum | Avg Waiting | Avg Response | Context Switch |
  |---|---|---|---|
  | 1 | 12.5 | 0.75 | 22 |
  | 2 | 12.75 | 2.0 | 10 |
  | 3 | 13.5 | 3.0 | 6 |
  | 5 | 11.0 | 5.5 | 2 |
  | 8 | 9.75 | 8.5 | 1 |
  | 12 | 8.75 | 8.75 | 0 |

  Bahas trade-off-nya, dan tunjukkan bahwa pada quantum 12 angkanya **identik
  dengan FCFS** — bukti bahwa Round Robin dengan quantum sangat besar memang
  berubah menjadi FCFS.

### 4.2 Proses, Thread, dan IPC (3 hal)

**Race condition.** Tampilkan tabel hasil beberapa percobaan. Tekankan tiga
hal: versi tanpa lock salah, salahnya **berbeda tiap percobaan**, dan versi
dengan lock selalu tepat.

Lalu bagian yang paling berbobot: bandingkan mode "preemption dipaksa" dengan
mode "preemption alami". Pada mode alami, kode yang **sama salahnya** sering
lolos 5 dari 5 percobaan. Tulis ini sebagai temuan, karena inilah alasan race
condition berbahaya di dunia nyata.

**Producer-Consumer.** Screenshot garis waktu kejadian dengan visual buffer.
Tunjukkan bahwa isi buffer tidak pernah melebihi kapasitas dan produsen
diblokir saat penuh. Jelaskan peran `empty`, `full`, `mutex`, dan **mengapa
urutan `wait()` tidak boleh dibalik** (akan menyebabkan deadlock).

**Dining Philosophers.** Screenshot ketiga strategi, terutama gambar meja saat
deadlock. Tampilkan circular wait yang terdeteksi:

```
F1 -> F2 -> F3 -> F4 -> F5 -> F1
```

| Strategi | Deadlock | Berhasil makan |
|---|---|---|
| Naive (kiri dulu, lalu kanan) | YA | 2/15 |
| Resource Ordering | tidak | 15/15 |
| Waiter / Semaphore | tidak | 15/15 |

Jelaskan **syarat Coffman mana** yang dipatahkan masing-masing solusi:
ordering mematahkan circular wait, waiter mematahkan hold-and-wait.

### 4.3 Deadlock (3 hal)

**Banker's Algorithm.** Tabel Allocation/Max/Need/Available pada contoh baku,
lalu jalannya safety algorithm langkah demi langkah sampai menemukan safe
sequence. Sajikan keempat skenario permintaan:

| Skenario | Permintaan | Hasil | Alasan |
|---|---|---|---|
| 1 | P1 minta [1,0,2] | Dikabulkan | tetap safe |
| 2 | P4 minta [3,3,0] | **Ditolak** | sumber daya cukup, tapi jadi unsafe |
| 3 | P0 minta [4,0,0] | Ditunda | melebihi Available |
| 4 | P2 minta [0,1,0] | Ditolak | melebihi Need, kesalahan proses |

Skenario 2 yang paling penting untuk dibahas: **permintaan ditolak walaupun
sumber dayanya tersedia**. Jelaskan ini sebagai sifat konservatif avoidance.

**Deteksi.** Screenshot wait-for graph dengan siklus merah. Tegaskan bahwa
deadlock terjadi *jika dan hanya jika* graf punya siklus. Lalu kasus banyak
instance, dan jelaskan perbedaan **Request vs Need**: deteksi memeriksa apa
yang sedang terjadi, avoidance memperkirakan apa yang mungkin terjadi.

**Recovery.** Tabel perbandingan strategi pemilihan korban:

| Strategi | Jumlah korban | Korban |
|---|---|---|
| most_resources | 1 | P2 |
| fewest_resources | 2 | P0, P1 |
| first | 2 | P0, P1 |

Bahas mengapa `most_resources` biasanya paling efisien, tapi di sistem nyata
pemilihan korban juga mempertimbangkan prioritas, lama berjalan, dan keamanan
restart (proses yang sedang menulis basis data tidak boleh sembarangan
dimatikan).

**Ostrich Algorithm.** Bahas sebagai keputusan rekayasa yang sah, bukan
kemalasan. Tabel perbandingan keempat pendekatan: overhead, jaminan, dan
di mana dipakai.

### 4.4 Pengujian (1 hal)

Screenshot `py run.py test` — 79 pemeriksaan, nol kegagalan. Lalu jelaskan
**apa** yang diuji, bukan hanya bahwa pengujiannya lulus:

1. Kecocokan dengan hasil buku teks (SRTF pada data Silberschatz: avg waiting 6.5)
2. Invarian lintas algoritma (`waiting == turnaround - burst` di keenamnya)
3. Invarian keamanan (buffer tidak pernah overflow, diperiksa tiap kejadian)
4. Perilaku batas (Round Robin quantum besar = FCFS)
5. Penanganan masukan salah (burst=0, JSON rusak, path traversal)

Tulis juga keterbatasan pengujian: hasil IPC tidak deterministik, sehingga yang
bisa diuji hanyalah invarian, bukan nilai pasti.

---

## BAB V — KESIMPULAN (1–2 halaman)

**5.1 Kesimpulan** — jawab tiga rumusan masalah di Bab I secara berurutan,
dengan **angka dari hasil percobaan**, bukan pernyataan umum.

**5.2 Keterbatasan** — jujur: satu CPU saja (tidak ada multiprocessor
scheduling), I/O burst tidak dimodelkan, Banker's mensyaratkan Max diketahui di
awal, hasil thread tidak dapat diulang persis.

**5.3 Saran Pengembangan** — tambah materi memory management (fit algorithms,
page replacement), tambah aging pada Priority Scheduling, modelkan I/O burst.

---

## DAFTAR PUSTAKA

- Silberschatz, A., Galvin, P. B., Gagne, G. (2018). *Operating System
  Concepts* (10th ed.). Wiley.
- Tanenbaum, A. S., Bos, H. (2015). *Modern Operating Systems* (4th ed.).
  Pearson.
- Coffman, E. G., Elphick, M., Shoshani, A. (1971). System Deadlocks.
  *ACM Computing Surveys*, 3(2), 67–78.
- Dijkstra, E. W. (1965). *Cooperating Sequential Processes*. — asal usul
  semaphore dan Dining Philosophers.

---

## LAMPIRAN

- **Lampiran A** — kode sumber lengkap (atau tautan folder)
- **Lampiran B** — keluaran lengkap `py run.py demo`
- **Lampiran C** — keluaran lengkap `py run.py test`
- **Lampiran D** — perhitungan manual (lihat `PERHITUNGAN-MANUAL.md`)

---

## Catatan praktis

**Jangan menempel kode satu berkas penuh** ke bab isi. Ambil potongan 5–15
baris yang penting, beri penjelasan. Kode lengkap taruh di lampiran.

**Setiap gambar dan tabel harus diberi nomor dan keterangan**, lalu dirujuk di
badan tulisan ("seperti terlihat pada Gambar 4.3"). Tabel yang muncul tanpa
dirujuk akan terasa seperti tempelan.

**Bagian paling bernilai adalah analisis**, bukan jumlah screenshot. Satu tabel
yang dibahas dua paragraf lebih baik daripada lima tabel tanpa penjelasan.

**Tiga temuan yang paling kuat di projek ini** — pastikan ketiganya masuk:

1. Kode yang sama salahnya bisa lolos 5 dari 5 pengujian ketika preemption
   dibiarkan alami. Race condition bisa bersembunyi.
2. Round Robin dengan quantum sangat besar menghasilkan angka **identik**
   dengan FCFS — batas teoretisnya terbukti secara empiris.
3. Banker's Algorithm menolak permintaan **walaupun sumber dayanya tersedia**.
   Ini memperlihatkan harga dari sebuah jaminan.
