# Belajar Sistem Operasi

Simulator lokal dengan dua materi inti: Process Scheduling (FCFS dan Round
Robin) serta IPC & Classical Problems (Producer–Consumer). Panduan nonteknis:
[OWNER.md](OWNER.md).

## Menjalankan

Windows 64-bit: klik `mulai.bat`, atau dari terminal:

```powershell
.\mulai.bat
.\mulai.bat --port 9000
.\mulai.bat test
```

Python lokal resmi 3.13.1 terdapat pada `.tools/python`; runtime aplikasi hanya
memakai standard library. Pada komputer dengan Python 3.10+:

```text
python run.py
python run.py --no-browser
python run.py test
```

Alamat default http://127.0.0.1:8000. Matikan server dengan Ctrl+C.

## Struktur inti

| Lokasi | Fungsi |
|---|---|
| `run.py`, `mulai.bat` | Titik masuk dan launcher Windows |
| `src/server.py` | HTTP lokal, validasi dan endpoint JSON |
| `src/scheduling/models.py` | Data proses, metrik dan definisi pergantian proses |
| `src/scheduling/algorithms.py` | FCFS, RR dan algoritma tambahan |
| `src/ipc/producer_consumer.py` | Buffer, semaphore, mutex, snapshot kejadian dan pembatalan |
| `web/index.html`, `web/css/belajar.css`, `web/js/belajar.js` | Antarmuka dua materi inti |
| `web/lanjutan.html` dan JS/CSS lama | Akses materi tambahan yang dipertahankan |
| `tests/` | Pengujian HTTP, algoritma, regresi dan thread |
| `scripts/collect_evidence.py` | Menghasilkan percobaan untuk laporan |
| `scripts/check_browser.cjs` | Pengujian browser dengan Playwright |
| `scripts/build_report.py` | Sumber isi dan generator PDF serta salinan Markdown |
| `docs/IDENTITAS.json` | Identitas mahasiswa dan nama tugas pada sampul |
| `docs/evidence/` | Data percobaan, log tes dan screenshot aktual |
| `output/pdf/` | Laporan final |

## Kontrak inti

`POST /api/scheduling`: `algorithm` adalah `fcfs`, `rr`, atau `all` (tambahan).
`processes` berisi 1–12 objek dengan nama unik 1–12 karakter, arrival 0–100,
burst 1–50. Nama IDLE tidak boleh dipakai. Quantum adalah integer 1–20.
Angka di luar batas ditolak HTTP 400, bukan diubah diam-diam. API mengembalikan
`results`, input dan mode. Mode single tidak memiliki `insight`; UI utama tidak
mengandalkan field tersebut.

`POST /api/ipc/producer-consumer`: kapasitas 1–10, barang per produsen 1–12,
produsen/konsumen 1–5, jeda 0–100 ms. UI utama menetapkan satu pekerja tiap peran.
Hasil menyertakan `completed`, `errors`, `stuck_threads` dan `events` dengan
snapshot `items`. Urutan snapshot terlindungi mutex. Rekaman diputar ulang di
browser setelah respons diterima, bukan realtime streaming.

FCFS/RR mengurutkan kedatangan yang bersamaan berdasarkan nama secara leksikal.
RR menerima kedatangan sampai batas quantum sebelum mengantrekan ulang proses
aktif. Batas giliran tetap terlihat meskipun proses yang sama berjalan lagi.
Context switch didefinisikan sebagai peralihan langsung antara dua proses
berbeda, tidak termasuk idle atau dispatch awal. Tidak ada biaya waktu switch.

## Verifikasi dan batas

Jalankan `run.py test` untuk 59 pemeriksaan HTTP, 20 pemeriksaan scheduling lama,
dan 20 kasus unittest regresi inti. Jumlah assertion/subkasus tidak disamakan
dengan jumlah kasus unittest. Browser diuji terpisah; bukti lengkap ada di
`docs/evidence/browser-results.json`. Tes HTTP saja bukan tes visual browser.

Aplikasi tidak memerlukan package tambahan. Tooling pembuatan laporan memakai
ReportLab dan PyMuPDF, sedangkan tes browser memakai Playwright; semuanya
terpisah di `.tools/packages` dan `.tools/browser`, tidak diperlukan untuk demo.
Runtime/tooling ini tidak dipasang ke instalasi Python sistem. Paket ZIP
penyerahan menyertakan runtime Python, tanpa dependency tooling laporan/browser.

Data aktual laporan: `docs/evidence/experiments.json`. Ulangi dengan:

```text
.tools\python\python.exe scripts\collect_evidence.py
node scripts\check_browser.cjs
```

Tes browser memerlukan server di port 8765 dan instalasi Chrome serta package
Playwright pada `.tools/browser`. Tes otomatis sengaja memakai profil browser
sementara, bukan profil pribadi pengguna. Python lokal tidak memerlukan pip.

Modul tambahan tetap tersedia untuk eksplorasi, bukan cakupan pembahasan utama
laporan. Pengujian tidak menjamin semua kemungkinan input atau jadwal thread.
Sistem ini alat belajar lokal, bukan server produksi atau simulator seluruh OS.

## Mengubah laporan

PDF final berisi 28 halaman: sampul, daftar isi, 25 halaman isi, dan daftar
pustaka. Identitas berasal dari `docs/IDENTITAS.json`. Nama tugas Data Structure
mengikuti informasi pemilik; dua materi tetap mengikuti `tugas.md`.

Untuk membuat ulang PDF di Windows, gunakan Python biasa dengan ReportLab dan
PyMuPDF terpasang, serta font Times New Roman bawaan Windows:

```text
python -m pip install reportlab pymupdf
python scripts/build_report.py
```

Konten pembuat PDF berada dalam `scripts/build_report.py`; data percobaan dan
screenshot dibaca dari `docs/evidence/`. `docs/LAPORAN.md` adalah salinan yang
dihasilkan generator: perubahan langsung pada salinan tersebut tidak otomatis
masuk ke PDF dan akan tertimpa bila generator dijalankan ulang. Untuk mengedit
di Word, salin Markdown ke dokumen terpisah dan periksa kembali jumlah halaman.

Runtime portable berasal dari distribusi resmi Python 3.13.1 Windows 64-bit:
https://www.python.org/ftp/python/3.13.1/python-3.13.1-embed-amd64.zip
Lisensi distribusi tetap disertakan dalam `.tools/python/LICENSE.txt`.

## Paket penyerahan

`output/Proyek-Blessya.zip` dapat diekstrak ke folder lain lalu dijalankan
melalui `mulai.bat`. Untuk membuat ulang dan memeriksa paket:

```text
.tools\python\python.exe scripts/package_project.py
.tools\python\python.exe scripts/check_package.py
```

Pemeriksaan paket membuat salinan sementara di `.tools/package-check-*`,
menjalankan tes melalui launcher, dan memeriksa server dari salinan tersebut.
Server pemeriksaan dihentikan setelah selesai. Manifest berkas dan checksum
ZIP berada di `output/package-manifest.json`; hasil tes di `docs/evidence/`.
