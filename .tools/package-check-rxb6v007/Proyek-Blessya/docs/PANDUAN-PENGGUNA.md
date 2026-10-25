# Panduan Pengguna — Belajar Sistem Operasi

## Menjalankan aplikasi

Buka folder proyek, lalu klik dua kali **mulai.bat**. Biarkan jendela terminal
terbuka. Browser membuka http://127.0.0.1:8000. Jika browser belum terbuka,
ketik alamat tersebut sendiri. Untuk berhenti, tekan Ctrl+C pada terminal.

Folder ini sudah menyertakan Python lokal untuk Windows 64-bit pada
`.tools/python`. Aplikasi tidak memerlukan internet atau pip install.
Jika Python lokal tidak ikut disalin, instal Python 3.10+ lalu gunakan
`py run.py` pada Windows atau `python3 run.py` pada Linux/macOS.

## Materi yang diperagakan

Satu aplikasi edukasi dengan dua materi inti:

| Materi dalam tugas | Yang dapat diperagakan |
|---|---|
| Process Scheduling | FCFS, Round Robin, Gantt chart, waktu tunggu, turnaround dan respons |
| IPC & Classical Problems | Producer–Consumer, buffer terbatas, semaphore dan mutex |

Demo Producer–Consumer memakai dua thread di dalam satu program Python, bukan
dua proses OS yang terpisah. Modul scheduling adalah model satu CPU, bukan
pengatur proses yang sedang berjalan pada laptop.

Materi tambahan (algoritma scheduling lain, race condition, Dining
Philosophers, dan deadlock) tersedia lewat tautan **Buka materi tambahan** di
bagian paling bawah halaman.

## Demo pertama — pembagian giliran CPU

1. Pilih tab Penjadwalan CPU. Tiga proses contoh sudah terisi.
2. Biarkan pilihan FCFS, tekan Jalankan penjadwalan.
3. Gantt chart menunjukkan P1 pada waktu 0–5, P2 pada 5–8, P3 pada 8–9.
4. Pilih Bandingkan FCFS dan Round Robin. Gunakan quantum 2, lalu jalankan.
5. Perhatikan rata-rata respons: FCFS 3,33; Round Robin 1. Waktu tunggu
   rata-ratanya sama-sama 3,33 pada contoh ini.
6. Ubah quantum menjadi 5. Hasilnya sama dengan FCFS pada data contoh tersebut.

Artinya: FCFS seperti kasir yang menyelesaikan satu pelanggan lebih dahulu.
Round Robin seperti kasir yang membagi waktu bergantian. Quantum menentukan
panjang setiap giliran. Tidak ada algoritma yang selalu terbaik untuk semua data.

### Cara membaca angka

- **Datang:** kapan proses siap masuk antrean.
- **Lama:** berapa satuan waktu CPU yang diperlukan.
- **Selesai:** kapan seluruh pekerjaan proses berakhir.
- **Menunggu:** total waktu proses siap tetapi belum mendapatkan CPU.
- **Turnaround:** dari proses datang sampai selesai.
- **Respons:** dari proses datang sampai pertama mendapat CPU.

Contoh P2 dalam FCFS: datang 1, mulai 5, selesai 8, lama 3.
Turnaround = 8 − 1 = 7; menunggu = 7 − 3 = 4; respons = 5 − 1 = 4.

Semua angka scheduling menggunakan satuan simulasi, bukan milidetik laptop.
Waktu pergantian proses tidak dihitung. Proses yang datang pada waktu sama
diurutkan menurut nama sebagai teks, sehingga P10 dapat mendahului P2.

## Demo kedua — barang masuk dan keluar buffer

1. Pilih tab Producer–Consumer.
2. Gunakan kapasitas 5 dan jumlah barang 8.
3. Klik Produsen lebih cepat, lalu Jalankan percobaan.
4. Klik Berikutnya untuk mengamati satu kejadian, atau Putar ulang untuk
   memutar seluruh rekaman. Tombol yang sama berubah menjadi Jeda.
5. Kotak berwarna berisi barang; kotak bertuliskan kosong masih tersedia.
6. Jalankan kembali dengan Konsumen lebih cepat. Amati konsumen menunggu barang.

Produsen dan konsumen benar-benar bekerja sebagai thread. Setelah mereka selesai,
browser memutar ulang rekaman kejadian dengan kecepatan 0,6 detik per langkah.
Ini bukan tayangan langsung. Waktu asli setiap kejadian tertulis dalam ms.

Pilihan 10, 40, atau 80 ms adalah jeda yang diminta. Jarak waktu antarbarang
yang tercatat bisa lebih panjang karena thread juga menunggu giliran dari
sistem operasi dan menunggu buffer.

Ketika buffer penuh, produsen memerlukan slot kosong. Ketika buffer kosong,
konsumen memerlukan barang. Semaphore mengatur izin tersebut. Mutex melindungi
perubahan isi buffer agar tidak dilakukan dua thread pada saat bersamaan.

Hasil akhir yang benar: dibuat = diambil = 8, buffer akhir kosong, isi tertinggi
tidak melebihi kapasitas, dan thread belum selesai = 0. Jumlah menunggu boleh
berbeda setiap percobaan karena urutan kerja thread diatur sistem operasi.

## Latihan

1. Hitung contoh FCFS dan Round Robin quantum 2 di kertas sebelum menekan
   tombol, lalu bandingkan dengan hasil aplikasi.
2. Jelaskan mengapa P3 yang datang pada waktu 2 masuk antrean sebelum P1
   yang baru dipotong pada waktu 2.
3. Ubah lama P1 menjadi 24 dan bandingkan waktu tunggu FCFS dengan Round Robin.

Jawaban latihan 1 dan 2 ada di `docs/PERHITUNGAN-MANUAL.md`.

## Berkas pendukung

- `output/pdf/Laporan-Simulator-Sistem-Operasi.pdf`: laporan lengkap.
- `docs/LAPORAN.md`: isi laporan dalam bentuk teks.
- `docs/PERHITUNGAN-MANUAL.md`: perhitungan FCFS dan Round Robin langkah demi langkah.
- `docs/evidence/experiments.json`: data percobaan yang dipakai laporan.
- `docs/evidence/timing-analysis.json`: perhitungan ulang jarak waktu kejadian.
- `README.md`: struktur teknis, cara tes, dan pembuatan ulang laporan.
- `docs/PENGGUNAAN-AI.md`: catatan penggunaan alat bantu AI.

## Jika ada masalah

| Gejala | Langkah |
|---|---|
| Port 8000 sudah dipakai | Buka terminal di folder proyek, jalankan `mulai.bat --port 9000` |
| Browser tidak terbuka | Buka sendiri http://127.0.0.1:8000, sesuai port yang digunakan |
| Server tidak terhubung | Pastikan terminal masih terbuka dan tidak menampilkan kesalahan |
| Masukan ditolak | Baca pesan; gunakan angka bulat dan batas di dekat kolom |
| Ingin memeriksa program | Jalankan `mulai.bat test` dari terminal |

Jangan membuka `web/index.html` langsung sebagai file karena halaman perlu
memanggil server Python.
