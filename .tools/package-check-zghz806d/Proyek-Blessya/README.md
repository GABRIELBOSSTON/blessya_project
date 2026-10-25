# Belajar Sistem Operasi

Aplikasi lokal untuk memperagakan dua materi: Process Scheduling melalui
FCFS dan Round Robin, serta IPC & Classical Problems melalui Producer-Consumer.
Panduan langkah demi langkah dan latihan tersedia di
[PANDUAN-PENGGUNA.md](docs/PANDUAN-PENGGUNA.md).

## Menjalankan aplikasi

Pada Windows 64-bit, ekstrak ZIP lalu klik dua kali **mulai.bat**. Biarkan
terminal terbuka selama aplikasi digunakan. Browser membuka
http://127.0.0.1:8000. Untuk berhenti, tekan Ctrl+C pada terminal.

```text
mulai.bat
mulai.bat --port 9000
mulai.bat test
```

Runtime Python 3.13.1 Windows 64-bit disertakan pada `.tools/python`.
Aplikasi memakai pustaka standar Python dan tidak memerlukan internet atau
instalasi package untuk demo. Dengan Python 3.10+ sendiri, gunakan:

```text
python run.py
python run.py --no-browser
python run.py test
```

Jangan membuka `web/index.html` langsung sebagai file; antarmuka membutuhkan
server Python. Pengujian paket dilakukan pada Windows. Cara memakai Python
sendiri di sistem lain tersedia, tetapi lingkungan tersebut belum diuji.

## Materi dan batas model

- FCFS/RR memakai satu CPU konseptual, burst diketahui, tanpa I/O dan tanpa
  durasi overhead perpindahan. Waktu adalah satuan simulasi.
- Kedatangan bersamaan diurutkan berdasarkan nama secara leksikal. RR menerima
  kedatangan sampai akhir quantum sebelum mengantrekan ulang proses aktif.
- Pergantian dihitung hanya pada dua segmen aktif berbeda yang berurutan;
  dispatch pertama, idle, dan giliran berulang proses sama tidak dihitung.
- Producer-Consumer memakai thread nyata dalam satu proses, buffer terbatas,
  semaphore empty/full, serta mutex. Ini bukan IPC dua proses OS terpisah.
- Tampilan buffer memutar rekaman setelah thread selesai. Jeda 10/40/80 ms
  adalah parameter yang diminta; interval kejadian aktual dapat berbeda.
- Fitur tambahan tetap tersedia pada `web/lanjutan.html`, termasuk deadlock,
  race condition, Dining Philosophers dan algoritma scheduling lainnya.

## Berkas utama

| Lokasi | Fungsi |
|---|---|
| run.py dan mulai.bat | Titik masuk aplikasi dan launcher Windows |
| src/server.py | HTTP lokal, validasi dan endpoint JSON |
| src/scheduling/ | Model proses, algoritma dan metrik |
| src/ipc/producer_consumer.py | Thread, buffer, semaphore, mutex dan log |
| web/ | Halaman utama, materi tambahan, CSS dan JavaScript |
| tests/ | Tes HTTP, scheduling dan regresi |
| docs/LAPORAN.md | Salinan laporan yang dihasilkan generator |
| output/pdf/Laporan-Simulator-Sistem-Operasi.pdf | Laporan final lima BAB |
| docs/evidence/ | Data mentah, log pengujian dan screenshot |
| docs/PERHITUNGAN-MANUAL.md | Contoh FCFS/RR untuk pemeriksaan manual |
| docs/IDENTITAS.json | Data sampul dari mahasiswa |
| docs/PENGGUNAAN-AI.md | Pengungkapan penggunaan bantuan AI |
| docs/SUMBER-TEORI.md | Bagian sumber primer yang digunakan |
| scripts/report_content.py | Isi laporan dan pengaitan data percobaan |
| scripts/build_report.py | Generator PDF dan salinan Markdown |

## Kontrak API inti

`POST /api/scheduling` menerima `algorithm: fcfs`, `rr`, atau `all` untuk
modul tambahan. `processes` memuat 1–12 objek: nama unik 1–12 karakter,
arrival 0–100, burst 1–50; IDLE dilarang. Quantum integer 1–20. Angka di luar
batas ditolak HTTP 400. Mode single mengembalikan satu hasil tanpa field
`insight`; antarmuka inti tidak bergantung pada field tersebut.

`POST /api/ipc/producer-consumer` menerima kapasitas 1–10, barang per produsen
1–12, pekerja tiap peran 1–5 dan jeda 0–100 ms. UI menetapkan satu pekerja
tiap peran. Hasil memuat `completed`, `errors`, `stuck_threads` dan `events`.
Snapshot `items` dicatat bersama perubahan buffer di dalam mutex.

## Pengujian dan reproduksi

`mulai.bat test` menjalankan 59 pemeriksaan HTTP/modul tambahan, 20 pemeriksaan
scheduling dan 21 kasus unittest regresi. Angka ini bukan jumlah seluruh
assertion/subkasus. Regresi mencakup perhitungan manual, batas quantum, FIFO,
kapasitas, pembatalan, serta JSON terlalu bersarang/panjang.

Tes browser memakai Chrome dan Playwright. Tooling ini terpisah dari aplikasi
dan tidak disertakan di ZIP. Setelah memasang Node.js, siapkan dengan:

```text
npm install --prefix .tools/browser playwright@1.58.2
```

Jalankan server di port 8765 pada terminal pertama, lalu tes pada terminal kedua:

```text
mulai.bat --no-browser --port 8765
node scripts/check_browser.cjs
node scripts/report_screenshots.cjs
```

Terdapat 20 alur pemeriksaan browser pada ukuran 1440×1080 dan 390×844.
Log versi yang diuji ada pada `docs/evidence/tests-audit.txt` dan
`browser-results.json`. Profil browser tes bersifat sementara.

Data laporan berada pada `docs/evidence/experiments.json`, dikumpulkan
24 Oktober 2026. Untuk menganalisis ulang data yang sama:

```text
.tools\python\python.exe scripts/analyze_timing.py
```

`scripts/collect_evidence.py` menjalankan percobaan baru dan **mengganti**
experiments.json. Salin data lama terlebih dahulu jika ingin mempertahankan
hasil yang dibahas laporan. Timestamp dan jumlah penantian thread boleh
berubah pada run baru; tabel laporan perlu dibuat ulang jika datanya diganti.

## Membuat ulang laporan

PDF memiliki lima BAB, kata pengantar, abstrak, daftar isi, dan daftar pustaka.
Jumlah halaman aktual direkam pada `docs/evidence/report-check.json`.
Isi utama berada pada `scripts/report_content.py`, identitas pada
`docs/IDENTITAS.json`, dan data/screenshot pada `docs/evidence/`.

Pada Windows dengan Python biasa, ReportLab, PyMuPDF, dan Times New Roman:

```text
python -m pip install reportlab pymupdf
python scripts/build_report.py
```

Perubahan langsung pada `docs/LAPORAN.md` tidak masuk ke PDF dan akan tertimpa
oleh generator. Untuk mengedit di Word, salin ke dokumen terpisah dan periksa
kembali halaman setelah mengubah format. Pembuatan laporan tidak diperlukan
untuk menggunakan aplikasi atau membaca PDF yang sudah disertakan.

## Isi dan pemeriksaan paket

Paket penyerahan berisi program, seluruh modul tambahan, runtime, tes, tooling
yang relevan, laporan, panduan dan data pendukung. Dokumen koordinasi kerja
serta arsip revisi tidak termasuk. Pengungkapan bantuan AI tetap disertakan.
`MANIFEST.json` di dalam ZIP mencatat hash SHA-256 setiap berkas lain.

```text
.tools\python\python.exe scripts/package_project.py
.tools\python\python.exe scripts/check_package.py
```

Pemeriksaan paket mengekstrak ke `.tools/package-check-*`, memvalidasi manifest
dan isi paket, menjalankan tes lewat launcher, serta memeriksa halaman dan API.
Server pemeriksaan dihentikan setelah selesai.

Runtime resmi berasal dari:
https://www.python.org/ftp/python/3.13.1/python-3.13.1-embed-amd64.zip
Lisensi distribusi ada pada `.tools/python/LICENSE.txt`.
