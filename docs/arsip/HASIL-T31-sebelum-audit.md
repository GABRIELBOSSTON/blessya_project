# Hasil akhir proyek — T01 sampai T31

Tanggal review akhir: **25 Oktober 2026, Asia/Jakarta**.
Pelaksana dan pemeriksa: Codex, mengikuti mandat penyelesaian penuh pemilik.
Keputusan: **LULUS pemeriksaan mandiri**; ini bukan review independen.
Hasil audit T01 awal tersimpan utuh pada `arsip/T01.md`.

## Hasil yang dapat digunakan

- `mulai.bat`: menjalankan aplikasi lokal pada Windows 64-bit.
- `web/index.html`: dua tab inti dengan bahasa Indonesia dan tampilan sederhana.
- `web/lanjutan.html`: akses modul tambahan yang dipertahankan.
- `output/pdf/Laporan-Simulator-Sistem-Operasi.pdf`: 28 halaman; 25 halaman isi.
- `output/Proyek-Blessya.zip`: kode, runtime portable, panduan, PDF dan bukti.
- `OWNER.md`: langkah demo dan penjelasan untuk pemilik.
- `docs/LAPORAN.md`: salinan isi laporan; generator berada di scripts/build_report.py.

Sampul memuat Blessya, NIM 001202400107, kelas Cyber Security. Nama tugas
Data Structure mengikuti jawaban pemilik. Daftar persyaratan tetap memuat
materi Sistem Operasi, sehingga implementasi tetap pada dua materi yang
disepakati. Institusi dan dosen belum diberikan, tidak dicantumkan/diisi tebakan.

## Implementasi dan perbaikan yang diperiksa

| Fokus | File/fungsi | Hasil |
|---|---|---|
| FCFS/RR | src/scheduling/algorithms.py: fcfs, round_robin | Antrean, idle, kedatangan bersamaan dan batas quantum jelas |
| Metrik | src/scheduling/models.py: build_metrics, count_context_switches | Switch hanya antarproses berbeda; quantum habis sendiri bukan switch |
| Input | models.py: Process, validate_processes; server.py: _integer, api_scheduling | ID unik, IDLE dilarang, integer/rentang ditolak secara eksplisit |
| Buffer | src/ipc/producer_consumer.py: BoundedBuffer.put/get/_log | Perubahan buffer dan snapshot dicatat di dalam mutex |
| Penghentian | producer_consumer.py: run_demo, worker, _acquire | Error/timeout memicu cancel; tunggu semaphore dapat dibatalkan |
| HTTP | src/server.py: Handler.do_GET/do_POST | Batas direktori statis diperbaiki; JSON dan Content-Length salah ditolak |
| UI inti | web/js/belajar.js: runCPU, scheduleHTML, runPC, renderReplay | Dua topik, FCFS/RR/compare, buffer langkah demi langkah, ekspor JSON |
| Kejujuran model | web/index.html, belajar.js, OWNER.md, laporan | Satu CPU simulasi; dua thread dalam satu proses; replay setelah selesai |
| Peluncuran | mulai.bat, .tools/python | Python resmi lokal 3.13.1; aplikasi memakai standard library |
| Dokumentasi | OWNER.md, README.md, PERHITUNGAN-MANUAL.md | Cocok dengan fitur dan hasil yang diuji |

Materi tambahan (deadlock, race condition, Dining Philosophers, SJF, SRTF,
priority) tetap ada. Penyederhanaan navigasi bukan penghapusan modul.

## Bukti aktual dan perintah

Jalankan perintah dari folder proyek. Tes awal dan percobaan berlangsung
24 Oktober 2026; review identitas, PDF terbaru dan tes paket pada 25 Oktober.

| Pemeriksaan | Perintah/aktivitas | Hasil aktual | Bukti |
|---|---|---|---|
| Baseline sebelum perbaikan | Python Blender 3.11.11 menjalankan run.py test | 79 pemeriksaan lama lulus | evidence/baseline.txt |
| Aplikasi setelah perbaikan | .tools\python\python.exe run.py test | 59 pemeriksaan HTTP, 20 pemeriksaan scheduling, 20 kasus unittest; semua lulus | evidence/tests-final.txt |
| Browser desktop/ponsel | node scripts/check_browser.cjs, server port 8765 | 18 alur lulus, tidak tercatat error JavaScript | evidence/browser-results.json dan ui-*.png |
| Data laporan | .tools\python\python.exe scripts/collect_evidence.py | Dataset scheduling dan 15 run buffer tersimpan | evidence/experiments.json |
| Detail gambar laporan | node scripts/report_screenshots.cjs | Screenshot elemen dari aplikasi berjalan | evidence/detail-fcfs.png, detail-rr.png, detail-buffer.png |
| Membuat PDF | Python Blender 3.11.11 menjalankan scripts/build_report.py dengan ReportLab/PyMuPDF lokal | 28 halaman; 25 bagian isi masing-masing satu halaman | evidence/report-build.txt, report-check.json |
| Pemeriksaan visual PDF | PNG hasil render semua halaman diperiksa; revisi sampul/halaman 24 dan 26 diperiksa kembali | Tidak ditemukan teks/tabel terpotong atau tumpang tindih; gambar terbaca | evidence/report-pages/ pada workspace; PDF final dalam paket |
| Paket ZIP | .tools\python\python.exe scripts/package_project.py | ZIP dengan CRC valid; manifest SHA-256 tersedia | output/package-manifest.json |
| Paket setelah ekstraksi | .tools\python\python.exe scripts/check_package.py | 6 cek lulus; launcher test exit 0; halaman, aset dan dua endpoint berhasil | evidence/package-check.json, package-tests.txt |

Perintah render aktual menggunakan executable
`C:/Program Files/Blender Foundation/Blender 4.5/4.5/python/bin/python.exe`.
Ini tooling pembuatan laporan, bukan syarat untuk menjalankan aplikasi.
Runtime/tooling tidak dipasang secara global. Paket menyerahkan Python
portable saja; package ReportLab/PyMuPDF/Playwright tidak ikut disertakan.

Angka 59, 20 dan 20 adalah jumlah yang dilaporkan masing-masing suite; jumlah
assertion/subkasus tidak disamakan dengan jumlah kasus unittest. Output
unittest menulis progres ke stderr; indikator kelulusannya exit 0 dan `OK`,
bukan warna terminal. Tes paket mengeksekusi kembali ketiga suite melalui
`mulai.bat test` di folder ekstraksi, lalu memeriksa halaman dan API.

## Pemeriksaan konsep dan angka

Contoh: P1 datang 0/burst 5, P2 datang 1/burst 3, P3 datang 2/burst 1.

| Metrik rata-rata | FCFS | RR quantum 2 |
|---|---|---|
| Menunggu | 3,33 | 3,33 |
| Turnaround | 6,33 | 6,33 |
| Respons | 3,33 | 1 |
| Pergantian antarproses | 2 | 5 |

Perhitungan manual sama dengan hasil fungsi, API dan tampilan. Satu proses
burst 5/quantum 2 memiliki tiga giliran tetapi nol pergantian antarproses.
Biaya waktu switch tidak dimodelkan. Kedatangan pada akhir quantum diterima
sebelum proses aktif diantrekan ulang; kedatangan sama diurutkan leksikal.

Buffer memakai semaphore empty/full dan mutex. Produksi/konsumsi tercatat
bersama isi buffer sehingga rekonstruksi FIFO dapat diperiksa. Event menunggu
menandakan izin gagal diperoleh saat dicoba; snapshot bisa dicatat setelah
thread lain mengubah buffer. UI dan laporan menjelaskan batas ini.

Semua 15 run buffer pada data laporan menyelesaikan target, menjaga kapasitas,
dan tidak menyisakan thread. Angka menunggu bergantung penjadwalan thread;
screenshot merupakan eksekusi tersendiri, bukan sumber angka ulangan tabel.

## Review laporan dan artefak

PDF dihitung langsung setelah render: halaman 1 sampul, 2 daftar isi,
3–27 isi, 28 daftar pustaka. Jumlah halaman bukan perkiraan Markdown.
Font Times New Roman disertakan di PDF; kertas A4; teks isi 12 pt.
Screenshot berasal dari program, referensi [1]–[6] dari OSTEP dan dokumentasi
resmi Python yang diakses 24 Oktober. Referensi teori tidak dijadikan sumber
angka percobaan. Identitas tersimpan pada `docs/IDENTITAS.json`.

Riwayat perubahan tata letak: render awal menghasilkan 41 halaman dengan
beberapa luapan pendek. Leading, jarak tabel dan batas ukuran gambar dirapikan,
kemudian dirender ulang menjadi 28 halaman tanpa halaman luapan tersebut.
Daftar isi juga diperbaiki dan diperiksa setelah render. Tidak ada kegagalan
tes aplikasi yang masih terbuka pada hasil terakhir.

## Keterbatasan dan yang tidak diklaim

- Pengujian pada Windows/Chrome desktop 1440×1080 dan viewport 390×844;
  browser/perangkat lain BELUM DIJALANKAN.
- Semua kemungkinan input dan interleaving thread tidak dapat dicakup tes ini.
- Uji visual mendalam semua modul tambahan BELUM DIJALANKAN; suite HTTP lama
  dan akses halaman lanjutan lulus, sedangkan fokus demo/laporan dua topik inti.
- Aplikasi lokal untuk belajar; tidak dipublikasikan atau diklaim siap produksi.
- Tidak ada IPC dua proses OS terpisah; Producer–Consumer menggunakan thread.
- Pemilik tetap perlu mempelajari demo. Pemahaman pemilik belum dinilai.
- Format khusus institusi/dosen belum diberikan; PDF memenuhi syarat halaman
  yang tersedia, tetapi tidak mengklaim mengikuti template kampus yang belum ada.

Tidak ada implementasi wajib yang tertunda. Pembaruan berikutnya hanya jika
pemilik meminta revisi atau memberikan ketentuan akademik tambahan.
