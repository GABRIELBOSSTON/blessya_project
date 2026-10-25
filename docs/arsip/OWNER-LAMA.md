# Panduan Pemilik Projek

Berkas ini ditulis untuk **dibaca orang yang tidak mengerti pemrograman sama
sekali**. Tidak ada satu pun bagian di sini yang mengharuskan Anda membaca kode.

Kalau Anda hanya punya waktu dua menit, baca **Bagian 1** dan **Bagian 2** saja.
Itu sudah cukup untuk menjalankan programnya dan tahu apa yang sedang dilihat.

---

## Daftar Isi

1. [Apa ini sebenarnya](#1-apa-ini-sebenarnya)
2. [Cara menjalankan](#2-cara-menjalankan)
3. [Apa yang akan Anda lihat di layar](#3-apa-yang-akan-anda-lihat-di-layar)
4. [Penjelasan tiga materinya dengan bahasa sehari-hari](#4-penjelasan-tiga-materinya-dengan-bahasa-sehari-hari)
5. [Isi folder: berkas mana untuk apa](#5-isi-folder-berkas-mana-untuk-apa)
6. [Cara membuktikan programnya benar](#6-cara-membuktikan-programnya-benar)
7. [Kalau ada masalah](#7-kalau-ada-masalah)
8. [Bahan untuk laporan](#8-bahan-untuk-laporan)
9. [Pertanyaan yang mungkin ditanyakan dosen](#9-pertanyaan-yang-mungkin-ditanyakan-dosen)

---

## 1. Apa ini sebenarnya

Ini **alat peraga** untuk mata kuliah Sistem Operasi.

Bayangkan buku pelajaran Sistem Operasi. Di dalamnya ada rumus dan diagram
tentang bagaimana komputer mengatur pekerjaannya. Masalahnya, diagram di buku
itu diam — tidak bisa dicoba, tidak bisa diubah angkanya.

Program ini membuat diagram-diagram itu **bisa dijalankan**. Anda mengubah
angkanya, tekan satu tombol, dan program menghitung ulang semuanya lalu
menggambarkan hasilnya.

Yang penting dipahami: **program ini bukan sistem operasi.** Ia tidak
menggantikan Windows. Ia adalah *simulator* — seperti simulator penerbangan
yang mengajarkan cara menerbangkan pesawat tanpa menjadi pesawat sungguhan.

Tiga materi yang dibahas:

| Materi | Pertanyaan yang dijawab |
|---|---|
| **Penjadwalan Proses** | Kalau banyak pekerjaan minta dikerjakan sekaligus, mana yang didahulukan? |
| **Proses, Thread & IPC** | Bagaimana kalau dua pekerjaan mengubah data yang sama persis di saat yang sama? |
| **Deadlock** | Bagaimana kalau dua pekerjaan saling menunggu sampai keduanya macet selamanya? |

Tugas mensyaratkan minimal 2 materi. Projek ini mengambil **3**.

---

## 2. Cara menjalankan

### Yang dibutuhkan

Hanya **Python**. Tidak ada yang lain. Tidak perlu memasang apa pun lewat
internet, tidak perlu koneksi internet sama sekali.

Cek apakah Python sudah ada. Buka **PowerShell** (tekan tombol Windows, tulis
`powershell`, tekan Enter), lalu ketik:

```
py --version
```

Kalau muncul tulisan seperti `Python 3.13.1`, Anda siap.
Kalau muncul pesan error, lompat ke [Bagian 7](#7-kalau-ada-masalah).

### Menjalankan

Di PowerShell, ketik dua perintah ini satu per satu:

```
cd D:\blessya
py run.py
```

Browser akan **terbuka sendiri**. Kalau tidak, buka browser secara manual dan
kunjungi alamat ini:

```
http://127.0.0.1:8000
```

### Menghentikan

Kembali ke jendela PowerShell, tekan **Ctrl + C**.

> **Penting:** jendela PowerShell itu harus **tetap terbuka** selama Anda memakai
> programnya. Jendela itu *adalah* programnya; browser hanya menampilkan
> hasilnya. Kalau jendela itu ditutup, halaman di browser berhenti bekerja.

### Perintah lain yang mungkin berguna

| Perintah | Gunanya |
|---|---|
| `py run.py` | Jalankan tampilan web (yang biasa dipakai) |
| `py run.py demo` | Tampilkan semua hasil sebagai teks di PowerShell. Bagus untuk screenshot laporan. |
| `py run.py test` | Periksa apakah semua perhitungan program benar |
| `py run.py --port 9000` | Pakai nomor port lain, kalau 8000 sedang dipakai program lain |
| `py run.py --no-browser` | Jalankan tanpa membuka browser otomatis |

---

## 3. Apa yang akan Anda lihat di layar

Ada empat tab di bagian atas halaman.

### Tab 1 — Penjadwalan Proses

Di atas ada **tabel** yang bisa Anda isi. Setiap baris adalah satu pekerjaan:

- **Arrival** = jam berapa pekerjaan itu datang
- **Burst** = berapa lama pekerjaan itu butuh waktu CPU
- **Prioritas** = seberapa penting (angka **lebih kecil** berarti **lebih** penting)

Tekan **Jalankan semua algoritma**. Program akan mencoba **enam cara berbeda**
untuk mengurutkan pekerjaan yang sama, lalu menunjukkan mana yang paling efisien.

Yang muncul:

- **Batang-batang warna** — itu namanya *Gantt chart*. Membaca dari kiri ke
  kanan = perjalanan waktu. Setiap warna adalah satu pekerjaan. Arahkan kursor
  ke sebuah batang untuk melihat jam mulai dan selesainya.
- **Batang bergaris-garis** — CPU sedang menganggur karena belum ada pekerjaan
  yang datang.
- **Kotak-kotak angka** — ringkasan kinerja. Yang paling penting
  **Avg waiting**: rata-rata waktu terbuang untuk menunggu. **Semakin kecil
  semakin baik.**
- **Tabel perbandingan** di bagian atas — langsung menunjukkan algoritma mana
  yang menang.

**Coba ini:** ubah angka *Burst* pekerjaan pertama menjadi `30`, lalu jalankan
lagi. Avg waiting FCFS menjadi **25.25**, sementara SRTF hanya **7.0** — lebih
dari tiga kali lebih baik pada data yang sama persis. Satu pekerjaan panjang di
depan menahan semua yang di belakangnya; istilahnya *convoy effect*, seperti
satu truk lambat menahan antrean mobil di jalan satu jalur.

Perhatikan juga hal yang menarik di percobaan ini: SJF hanya mencapai 24.25,
nyaris sama buruknya dengan FCFS. Penyebabnya, pekerjaan panjang itu tiba
paling awal sehingga saat SJF memilih, ia satu-satunya pilihan yang ada — dan
begitu mulai, SJF tidak boleh menyelanya. Hanya algoritma yang **boleh
menyela** (SRTF dan Priority preemptive) yang bisa menyelamatkan keadaan ini.
Ini bahan analisis yang bagus untuk laporan.

### Tab 2 — Thread & IPC

Tiga percobaan. Bagian ini memakai **thread sungguhan**, bukan simulasi.

**A. Race Condition.** Beberapa pekerja menambah satu angka bersama. Secara
matematika hasilnya sudah pasti. Tapi tanpa pengaman, **hasilnya salah** —
dan salahnya berbeda setiap kali dijalankan.

Perumpamaannya: dua orang kasir melihat stok barang di layar tertulis 10. Keduanya
menjual 1 barang. Keduanya menulis "sekarang 9". Padahal seharusnya 8. Satu
penjualan hilang dari catatan.

Kolom hijau di tabel adalah versi yang sudah diberi pengaman (namanya **lock**).
Angkanya **selalu** benar.

> **Satu hal yang akan ditanyakan:** kenapa ada centang "Paksa perpindahan
> thread"? Karena tanpa dipaksa, kesalahan ini sering **tidak muncul** walaupun
> programnya tetap salah. Coba matikan centangnya dan jalankan — kemungkinan
> besar hasilnya tampak benar. **Itu justru temuan paling penting di projek
> ini:** program yang salah bisa lulus pengujian berkali-kali, lalu rusak di
> komputer lain atau saat sedang sibuk. Jangan hilangkan bagian ini dari
> laporan.

**B. Producer-Consumer.** Satu pihak menaruh barang ke rak terbatas, pihak lain
mengambilnya. Kotak-kotak biru kecil menunjukkan isi rak. Perhatikan dua hal:
jumlah kotak biru **tidak pernah melebihi** kapasitas rak, dan setiap kali rak
penuh, penaruh barang otomatis diberi label merah **BLOKIR** — ia menunggu
dengan tertib, tidak memaksa.

**C. Dining Philosophers.** Lima orang duduk mengelilingi meja dengan lima
garpu. Setiap orang butuh **dua** garpu untuk makan. Ada gambar meja bundar:
hijau = sedang makan, kuning = pegang satu garpu, **merah = macet menunggu**.

Strategi pertama (*naive*) akan **macet total** — semua orang pegang satu garpu
dan menunggu garpu tetangganya, selamanya. Dua strategi berikutnya berhasil.
Ini contoh deadlock yang paling mudah dibayangkan.

### Tab 3 — Deadlock

**A. Banker's Algorithm.** Cara kerjanya seperti bank yang hati-hati. Bank hanya
mau mencairkan pinjaman kalau sesudahnya ia **masih sanggup** melayani semua
nasabah lain. Kalau tidak bisa dijamin, pinjaman ditunda — walaupun uangnya
sedang ada di kas.

Tekan **Periksa keadaan**, lalu coba ajukan permintaan. Perhatikan baik-baik
kasus di mana permintaan **ditolak padahal barangnya tersedia**. Itu bukan bug.
Itu memang inti cara kerjanya: mengorbankan sedikit efisiensi untuk mendapat
jaminan bahwa kemacetan tidak akan pernah terjadi.

**B. Deteksi & Recovery.** Pendekatan sebaliknya: biarkan macet dulu, lalu
deteksi dan perbaiki. Ada gambar panah antar proses — **panah merah yang
membentuk lingkaran** itulah bukti kemacetan. Program lalu memilih satu proses
untuk "dikorbankan" agar yang lain bisa jalan.

Ada juga tombol **Ostrich Algorithm**, yang artinya: *sengaja tidak melakukan
apa-apa*. Ini terdengar seperti lelucon tapi bukan — Windows dan Linux
benar-benar memakai pendekatan ini untuk banyak hal, karena mencegah kemacetan
setiap hari lebih mahal daripada sekadar me-restart program yang macet setahun
sekali.

### Tab 4 — Tentang

Ringkasan singkat yang sama, langsung di dalam program.

---

## 4. Penjelasan tiga materinya dengan bahasa sehari-hari

### Penjadwalan Proses

CPU hanya bisa mengerjakan **satu hal pada satu waktu**. Ketika Anda membuka
browser, musik, dan Word sekaligus, semuanya terasa jalan bersamaan — padahal
sebenarnya CPU berpindah-pindah sangat cepat di antara ketiganya.

Siapa yang menentukan urutannya? Sistem operasi. Aturan yang dipakainya disebut
*algoritma penjadwalan*. Program ini mencoba enam aturan:

| Aturan | Cara kerjanya | Masalahnya |
|---|---|---|
| **FCFS** | Siapa datang dulu, dilayani dulu | Satu pekerjaan panjang menahan semua yang di belakangnya |
| **SJF** | Yang paling cepat selesai, didahulukan | Perlu tahu lama pekerjaan sebelum dikerjakan — di kenyataan tidak mungkin |
| **SRTF** | Seperti SJF, tapi boleh menyela yang sedang jalan | Pekerjaan panjang bisa tidak pernah kebagian |
| **Round Robin** | Semua dapat jatah waktu bergiliran | Sering berpindah = ada biaya overhead |
| **Priority** | Yang penting didahulukan | Yang tidak penting bisa tidak pernah dilayani |

**Kesimpulan yang penting untuk laporan:** tidak ada satu aturan yang terbaik
untuk semua keadaan. Pilihannya tergantung tujuan — mau menyelesaikan sebanyak
mungkin pekerjaan (server), atau mau terasa cepat dan tidak nge-lag saat
dipakai manusia (laptop)?

### Proses, Thread & IPC

Satu program bisa punya banyak *pekerja* di dalamnya, namanya **thread**.
Keuntungannya: mereka bisa bekerja bersamaan sehingga cepat. Bahayanya: mereka
**berbagi memori yang sama**.

Bayangkan dua orang mengedit satu dokumen yang sama persis di saat yang sama,
tanpa saling tahu. Yang disimpan terakhir menimpa pekerjaan yang lain. Di
pemrograman masalah ini namanya **race condition**, dan tab 2A membuktikannya
dengan angka.

Solusinya: **lock** (kunci). Sebelum menyentuh data bersama, pekerja harus
mengambil kunci dulu. Yang tidak dapat kunci, menunggu di luar. Satu orang
masuk, satu orang keluar, tertib.

### Deadlock

Deadlock adalah kemacetan total yang **tidak bisa pulih sendiri**.

Perumpamaan paling pas: perempatan tanpa lampu lalu lintas. Empat mobil masuk
dari empat arah bersamaan. Masing-masing sudah separuh masuk dan tidak bisa
maju karena terhalang mobil di depannya, juga tidak bisa mundur karena ada
mobil di belakangnya. Semuanya berhenti. Selamanya.

Empat syarat harus terpenuhi **bersamaan** agar deadlock terjadi:

1. Sumber daya hanya bisa dipakai satu pihak pada satu waktu
2. Pihak yang sudah memegang sesuatu masih meminta yang lain
3. Yang sudah dipegang tidak bisa dirampas paksa
4. Tunggu-menunggunya membentuk lingkaran

**Menghilangkan satu saja sudah cukup** untuk mencegah deadlock. Itulah yang
dilakukan dua strategi yang berhasil di tab 2C.

Ada empat sikap yang bisa diambil sistem operasi:

| Sikap | Artinya | Dipakai di mana |
|---|---|---|
| **Prevention** | Rancang sistem agar deadlock mustahil terjadi | Sistem kritis |
| **Avoidance** | Periksa setiap permintaan sebelum dikabulkan (Banker's) | Jarang, karena mahal |
| **Detection & Recovery** | Biarkan terjadi, deteksi, lalu perbaiki | Basis data |
| **Ostrich** | Sengaja diabaikan | Windows, Linux, untuk banyak hal |

---

## 5. Isi folder: berkas mana untuk apa

```
blessya/
├── OWNER.md          <-- berkas yang sedang Anda baca
├── README.md             ringkasan teknis singkat
├── tugas.md              soal tugas aslinya
├── run.py                tombol start. Jalankan ini.
│
├── src/                  isi program (kode Python)
│   ├── server.py         penghubung antara browser dan perhitungan
│   ├── scheduling/       materi 1: penjadwalan proses
│   ├── ipc/              materi 2: thread, race condition, IPC
│   └── deadlock/         materi 3: deadlock
│
├── web/                  tampilan yang muncul di browser
│   ├── index.html        susunan halaman
│   ├── css/              warna dan tata letak
│   └── js/               yang menggambar grafik
│
├── tests/                pemeriksa kebenaran perhitungan
└── docs/                 bahan untuk menulis laporan
```

Yang perlu Anda sentuh: **hanya `run.py`**, dan itu pun cukup dijalankan.

---

## 6. Cara membuktikan programnya benar

Ini pertanyaan yang wajar: bagaimana tahu angka-angka itu bukan karangan?

Jalankan:

```
cd D:\blessya
py run.py test
```

Program akan memeriksa dirinya sendiri dan menampilkan daftar panjang berisi
kata **LULUS**. Di bagian paling bawah muncul ringkasan seperti:

```
HASIL: seluruh 2 berkas pengujian LULUS
```

Ada **79 pemeriksaan** yang dijalankan. Yang diperiksa antara lain:

- Hasil perhitungan dicocokkan dengan **jawaban dari buku teks**
  (Silberschatz, *Operating System Concepts*). Kalau program menghitung
  berbeda dari buku, pengujiannya gagal.
- Rumusnya konsisten: *waiting time* harus selalu sama dengan
  *turnaround* dikurangi *burst*, di keenam algoritma.
- Total waktu CPU yang terpakai harus sama dengan total pekerjaan yang masuk —
  tidak boleh ada waktu yang hilang atau tercipta.
- Rak di Producer-Consumer **tidak pernah** melebihi kapasitasnya, diperiksa
  di setiap kejadian.
- Versi dengan lock **selalu** memberi hasil yang benar.
- Masukan yang salah (misal burst time nol) harus ditolak dengan pesan jelas,
  bukan membuat program mati.

Kalau nanti ada yang mengubah kode dan merusak sesuatu, pengujian ini akan
menunjukkannya.

### Satu catatan kejujuran yang penting

Angka di **tab 1 dan tab 3 selalu sama** setiap dijalankan. Itu memang
seharusnya — perhitungannya pasti.

Angka di **tab 2 berubah setiap kali dijalankan**. Itu **bukan kerusakan**.
Tab 2 memakai thread sungguhan yang berebut CPU, dan hasil perebutan itu
memang tidak bisa diramalkan. Justru **ketidakpastian itulah yang sedang
ditunjukkan**. Kalau ada yang bertanya kenapa hasilnya tidak konsisten,
jawabannya: karena begitulah kenyataannya, dan itu sebabnya lock dibutuhkan.

---

## 7. Kalau ada masalah

### `py : The term 'py' is not recognized`

Python belum terpasang, atau belum terdaftar di sistem. Coba dulu:

```
python --version
```

Kalau yang ini jalan, pakai `python` di semua perintah, bukan `py`.

Kalau dua-duanya gagal: unduh Python dari <https://www.python.org/downloads/>.
Saat memasang, **centang kotak "Add Python to PATH"** di layar pertama. Kotak
ini mudah terlewat dan merupakan penyebab masalah paling umum.

### `Port 8000 sedang dipakai program lain`

Ada program lain memakai nomor itu. Pakai nomor lain:

```
py run.py --port 9000
```

Lalu buka `http://127.0.0.1:9000`.

### Halaman browser kosong atau tulisannya berantakan

1. Pastikan jendela PowerShell masih terbuka dan belum ditekan Ctrl+C.
2. Muat ulang halaman dengan **Ctrl + F5** (bukan F5 biasa — ini memaksa
   browser mengambil versi terbaru).
3. Periksa alamatnya: harus `http://127.0.0.1:8000`, bukan `https`.

### Program ini butuh Python 3.10 atau lebih baru

Python yang terpasang terlalu tua. Unduh versi terbaru dari tautan di atas.

### Tab 2 memberi hasil berbeda setiap kali ditekan

Itu normal dan memang disengaja. Lihat penjelasan di akhir
[Bagian 6](#6-cara-membuktikan-programnya-benar).

### Strategi *naive* di Dining Philosophers kadang tidak macet

Juga normal. Deadlock bergantung pada waktu, jadi kadang kebetulan lolos.
Tekan tombolnya beberapa kali. Kalau ingin peluang macetnya lebih besar,
naikkan angka "Target makan per filsuf".

---

## 8. Bahan untuk laporan

Tugas mensyaratkan laporan **minimal 20 halaman** berisi penjelasan materi dan
dokumentasi.

Rangka bab dan saran isinya ada di **`docs/LAPORAN.md`**. Di situ sudah
tertulis bab apa saja, perkiraan jumlah halaman per bab, dan screenshot mana
yang perlu diambil dari program.

Cara mengambil bahan dengan cepat:

1. Jalankan `py run.py demo` di PowerShell. Semua hasil keluar sebagai teks
   yang bisa langsung di-copy ke Word.
2. Jalankan `py run.py` dan ambil screenshot dari browser untuk gambar-gambar
   yang berwarna (Gantt chart, meja filsuf, graf panah).
3. Jalankan `py run.py test` dan screenshot hasilnya — ini bukti bahwa
   programnya diuji, bukan sekadar jadi.

Saran kuat: **ambil screenshot tab 2 beberapa kali** dan tunjukkan bahwa
hasilnya berbeda-beda. Itu bukti kuat bahwa threadnya sungguhan, bukan angka
yang ditulis manual.

---

## 9. Pertanyaan yang mungkin ditanyakan dosen

Pertanyaan-pertanyaan ini kemungkinan muncul saat demo. Jawabannya ada di
projek, tapi lebih baik Anda sudah tahu sebelumnya.

**"Kenapa pakai Python, bukan C? Sistem operasi kan ditulis dengan C."**
Benar, dan C memang lebih dekat ke sistem operasi nyata. Tapi tujuan tugas ini
adalah menjelaskan *konsep*, bukan membuat sistem operasi. Dengan Python,
waktu terpakai untuk membuat visualisasi dan analisis, bukan untuk mengurus
pointer dan kebocoran memori. Perlu dicatat juga bahwa thread yang dipakai di
tab 2 adalah **thread sungguhan dari sistem operasi**, bukan tiruan.

**"Race condition-nya kan dipaksa pakai `sleep(0)`. Bukan curang?"**
Tidak, dan ini sengaja ditulis di komentar kodenya. `time.sleep(0)` tidak
menidurkan apa pun — ia hanya memaksa pergantian thread terjadi pada titik
tertentu. Bug-nya **sudah ada** di kode itu tanpa perintah tersebut; yang
dilakukan hanya mengatur agar pergantiannya jatuh di saat terburuk sehingga
bug-nya terlihat setiap kali. Buktinya: matikan centangnya, dan bug yang sama
sering tidak muncul walau kodenya tidak diubah sama sekali.

**"Kenapa safe sequence-nya berbeda dari yang di buku?"**
Karena sebuah keadaan bisa punya **lebih dari satu** safe sequence yang sama
benarnya. Program ini memeriksa proses secara berurutan dan mengambil yang
pertama cocok, jadi bisa menemukan urutan berbeda dari buku. Yang penting dan
yang diuji adalah apakah keadaannya *safe* atau *unsafe* — dan itu selalu cocok.

**"Kenapa Banker's Algorithm tidak dipakai sistem operasi sungguhan?"**
Dua alasan. Pertama, ia mensyaratkan setiap proses mengumumkan kebutuhan
maksimalnya di awal — program biasa tidak tahu itu. Kedua, biayanya mahal
karena harus diperiksa pada setiap permintaan. Karena itu sistem operasi nyata
lebih memilih deteksi, atau bahkan Ostrich Algorithm.

**"Round Robin quantum berapa yang paling bagus?"**
Tidak ada satu angka yang benar — ini trade-off. Program bisa menunjukkannya
secara langsung: jalankan `py run.py demo` dan lihat tabel "Pengaruh Time
Quantum". Saat quantum turun dari 12 ke 1, response time membaik tajam tapi
jumlah context switch melonjak dari 0 ke 22. Quantum kecil terasa responsif
tapi banyak waktu habis untuk berpindah; quantum besar efisien tapi
perilakunya kembali seperti FCFS.

---

*Dokumen ini bagian dari tugas mata kuliah Sistem Operasi. Pertanyaan teknis
yang lebih rinci dijawab di `README.md` dan di komentar dalam berkas kode.*
