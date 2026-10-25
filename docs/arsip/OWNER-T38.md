# Panduan pemilik — Belajar Sistem Operasi

## Mulai dari sini

Buka folder proyek, lalu klik dua kali **mulai.bat**. Biarkan jendela terminal
terbuka. Browser membuka http://127.0.0.1:8000. Jika browser belum terbuka,
ketik alamat tersebut sendiri. Untuk berhenti, tekan Ctrl+C pada terminal.

Folder ini sudah menyertakan Python lokal untuk Windows 64-bit pada
`.tools/python`. Aplikasi tidak memerlukan internet atau pip install.
Jika Python lokal tidak ikut disalin, instal Python 3.10+ lalu gunakan
`py run.py` pada Windows atau `python3 run.py` pada Linux/macOS.

## Apa yang dibuat untuk tugas dosen

Satu aplikasi edukasi dengan dua materi inti:

| Materi dalam tugas | Yang dapat diperagakan |
|---|---|
| Process Scheduling | FCFS, Round Robin, Gantt chart, waktu tunggu, turnaround dan respons |
| IPC & Classical Problems | Producer–Consumer, buffer terbatas, semaphore dan mutex |

Demo Producer–Consumer memakai dua thread dalam satu proses Python. Jangan
menyebutnya dua proses OS terpisah. Modul scheduling adalah model satu CPU/core,
bukan pengatur proses yang sedang berjalan pada laptop.

Materi tambahan dari proyek sebelumnya tetap ada pada tautan paling bawah.
Kamu tidak perlu mempresentasikannya untuk menjelaskan dua materi inti.

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

Semua angka scheduling menggunakan satuan simulasi, bukan pengukuran milidetik
laptop. Biaya waktu pergantian proses tidak dihitung. Nama proses dengan waktu
kedatangan sama diurutkan sebagai teks; P10 dapat mendahului P2.

## Demo kedua — barang masuk dan keluar buffer

1. Pilih tab Producer–Consumer.
2. Gunakan kapasitas 5 dan jumlah barang 8.
3. Klik Produsen lebih cepat, lalu Jalankan percobaan.
4. Klik Berikutnya untuk mengamati satu kejadian, atau Putar ulang untuk
   memutar seluruh rekaman. Tombol yang sama berubah menjadi Jeda.
5. Kotak berwarna berisi barang; kotak bertuliskan kosong masih tersedia.
6. Jalankan kembali dengan Konsumen lebih cepat. Amati konsumen menunggu barang.

Produsen dan konsumen benar-benar bekerja sebagai thread. Setelah mereka selesai,
browser menampilkan rekaman kejadian dengan pemutaran lambat 0,6 detik per langkah.
Ini bukan streaming langsung. Waktu asli setiap kejadian tertulis dalam ms.

Ketika buffer penuh, produsen memerlukan slot kosong. Ketika buffer kosong,
konsumen memerlukan barang. Semaphore mengatur izin tersebut. Mutex melindungi
perubahan isi buffer agar tidak dilakukan dua thread pada saat bersamaan.

Hasil akhir yang sehat: dibuat = diambil = 8, buffer akhir kosong, isi tertinggi
tidak melebihi kapasitas dan thread belum selesai = 0. Jumlah menunggu boleh
berbeda setiap percobaan; jangan menghafalnya sebagai angka tetap.

## Persiapan presentasi sekitar lima menit

1. Jelaskan dua materi dan tujuan alat peraga.
2. Peragakan contoh FCFS dan tunjukkan satu perhitungan manual P2.
3. Bandingkan dengan Round Robin quantum 2 dan 5.
4. Peragakan produsen cepat, lalu konsumen cepat.
5. Tutup dengan batas model dan kesimpulan hasil yang terlihat.

Pertanyaan yang mungkin muncul:

**Mengapa memilih dua materi ini?** Keduanya memenuhi dua butir tugas dan dapat
terlihat melalui perubahan urutan proses serta perubahan isi buffer.

**Mengapa tidak cukup memakai mutex?** Mutex melindungi bagian kode, tetapi
produsen juga perlu menunggu kapasitas dan konsumen perlu menunggu barang.
Semaphore menyatakan ketersediaan izin untuk kedua kondisi tersebut.

**Apakah quantum kecil selalu lebih baik?** Tidak. Pada model, respons bisa
lebih cepat tetapi pergantian proses lebih sering. Waktu overhead perpindahan
belum dimodelkan, sehingga jangan menyimpulkan kinerja CPU nyata dari angka ini.

**Bagaimana membuktikan hasilnya?** Ada perhitungan manual, pengujian algoritma,
pengujian HTTP, pengujian thread termasuk kegagalan, serta pemeriksaan browser.
Data mentah laporan tersimpan di `docs/evidence/experiments.json`.

**Apakah menunggu berarti deadlock?** Tidak. Produsen atau konsumen menunggu
izin yang akan disediakan pasangannya. Pada percobaan berhasil seluruh barang
selesai dipindahkan dan semua thread berhenti.

## Berkas yang perlu diketahui

- `output/pdf/Laporan-Simulator-Sistem-Operasi.pdf`: laporan final.
- `docs/LAPORAN.md`: salinan isi laporan untuk dibaca atau dipindahkan ke Word.
- `docs/IDENTITAS.json`: identitas yang dipakai pembuat PDF.
- `docs/PERHITUNGAN-MANUAL.md`: contoh hitungan yang bisa dipelajari.
- `docs/STATUS-KERJA.md`: hasil pekerjaan dan bukti pemeriksaan.
- `README.md`: panduan teknis.
- `docs/arsip/`: dokumentasi lama, bukan panduan versi sekarang.

Sampul memuat Blessya, NIM 001202400107, kelas Cyber Security, dengan nama
tugas Data Structure sesuai informasi pemilik. Materi tetap mengikuti daftar
dosen pada `tugas.md`: scheduling dan IPC & Classical Problems. Sampul sudah
memuat President University dan Mam Ocha sesuai informasi terbaru. Nama mata
kuliah belum dikonfirmasi ulang. Panduan untuk paket akademik berada pada
`docs/PANDUAN-PENGGUNA.md`; PDF revisi terdiri dari 37 halaman (32 halaman isi).

## Jika ada masalah

| Gejala | Langkah |
|---|---|
| Port 8000 sudah dipakai | Buka terminal di folder proyek, jalankan `mulai.bat --port 9000` |
| Browser tidak terbuka | Buka sendiri http://127.0.0.1:8000, sesuai port yang digunakan |
| Server tidak terhubung | Pastikan terminal masih terbuka dan tidak menampilkan kesalahan |
| Masukan ditolak | Baca pesan; gunakan angka bulat dan batas di dekat kolom |
| Gantt chart panjang | Geser grafik mendatar; ini tidak mengubah urutan waktunya |
| Ingin memeriksa program | Jalankan `mulai.bat test` dari terminal agar hasil tetap terlihat |
| Pindah laptop | Salin seluruh folder termasuk `.tools/python`, atau gunakan Python sendiri |

Jangan membuka `web/index.html` langsung sebagai file karena halaman perlu
memanggil server Python. Aplikasi ini dijalankan lokal untuk belajar.
