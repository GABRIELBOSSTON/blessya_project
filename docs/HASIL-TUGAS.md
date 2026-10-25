# T41 — Desain ulang antarmuka (gaya shadcn)

Tanggal: 25 Oktober 2026. Pelaksana dan pemeriksa: Claude, atas permintaan
langsung pemilik dengan spesifikasi desain shadcn. **LULUS pemeriksaan mandiri**.

| Berkas | Perubahan |
|---|---|
| web/css/tokens.css (baru) | Token warna, huruf 12–32, jarak 4–32, sudut 4/8, @font-face lokal |
| web/fonts/ (baru) | Geist dan Fira Code woff2 dari @fontsource-variable 5.3.0, lisensi OFL disertakan |
| web/css/belajar.css, style.css | Ditulis ulang; nama kelas dipertahankan untuk JS dan tes |
| web/index.html, lanjutan.html | Tautan token dan preload font; tombol kembali dan kontainer tab di halaman tambahan |
| web/js/belajar.js, util.js | Palet Gantt memakai token chart; kelas `idle` |
| web/js/ipc.js, deadlock.js | Warna SVG untuk tema terang; teks "kotak hitam"; panah `&rarr;` yang tampil mentah diperbaiki |
| src/server.py | `mimetypes.add_type("font/woff2", ".woff2")` |
| docs/PANDUAN-PENGGUNA.md, README.md | Warna dan tombol kembali disesuaikan; folder fonts dicatat |

Keputusan aksesibilitas: warna success/warning dari desain (3,3:1 dan 3,2:1)
hanya untuk garis/isian; teks memakai #15803d dan #b45309 (≥4,8:1). Batas
input #8a8a93 (3,42:1) memenuhi WCAG 1.4.11. Fokus keyboard: cincin hitam 2px.

Bukti: `evidence/tests-desain.txt` (exit 0), `evidence/browser-desain.txt` dan
`browser-results.json` (20 lulus), `evidence/report-build-desain.txt`
(40 halaman, 35 isi), `evidence/package-check.json` (105 entri, 8 cek).
Port 8765 dipakai dua proses lain (server sesi lama dan `python -m
http.server`); keduanya tidak dihentikan. Uji browser memakai salinan skrip
yang hanya mengganti port ke 8799. Salinan lama CSS/JS/HTML di `arsip/*-T40.*`.

# T40 — Panduan pengguna untuk pembaca awam

Tanggal: 25 Oktober 2026. Pelaksana dan pemeriksa: Claude, atas permintaan
langsung pemilik. **LULUS pemeriksaan mandiri**.

- `docs/PANDUAN-PENGGUNA.md` ditulis ulang (versi T39 di
  `arsip/PANDUAN-PENGGUNA-T39.md`): kamus istilah dengan kolom bahasa mudah,
  langkah menjalankan, fungsi setiap kolom/tombol dan hasil pada kedua tab,
  halaman materi tambahan, daftar pesan kesalahan, pemecahan masalah, FAQ.
- Isi dicocokkan dengan `web/index.html`, `web/js/belajar.js`, `web/lanjutan.html`,
  `web/js/scheduling.js`, `web/js/ipc.js`, `src/server.py`, dan `run.py`.
  Angka percobaan yang disarankan dihitung dari `src/scheduling/algorithms.py`
  dan `run_demo` (kapasitas 1: produsen menunggu 7 kali pada 3 run).
- `mulai.bat` dan `web/lanjutan.html` sebelumnya merujuk `OWNER.md`, yang tidak
  ikut ZIP; kini merujuk `docs/PANDUAN-PENGGUNA.md`. Salinan lama di arsip.
- Bukti: `run.py test` exit 0 (`evidence/tests-panduan.txt`); paket 100 entri,
  8 cek lulus (`evidence/package-check.json`). Tes browser BELUM DIJALANKAN
  ulang; perubahan web hanya teks pada halaman Tentang.

# T39 — Keterbacaan laporan dan panduan

Tanggal: 25 Oktober 2026. Pelaksana dan pemeriksa: Claude, atas permintaan
langsung pemilik ("utamakan mudah dimengerti"). **LULUS pemeriksaan mandiri**,
bukan review independen. Bagian T32–T38 di bawah tetap sebagai riwayat.

| Fokus | Berkas | Perubahan |
|---|---|---|
| Bahasa laporan | scripts/report_content.py | Paragraf penyangkalan dan istilah (liveness, assertion, hash, interleaving tanpa penjelasan) diganti bahasa sederhana; angka tidak diubah |
| Daftar istilah | report_content.py: glossary, subbab 1.4 | 23 istilah dengan arti sehari-hari, analogi mutex dan semaphore |
| Analogi | subbab 2.4, 2.5, 2.9 | Antrean kasir dan convoy effect, giliran mainan, papan parkir |
| Rumusan dan kesimpulan | 1.2, 5.1–5.3 | Tiga pertanyaan bernomor; kesimpulan menjawab satu per satu |
| Gambar | 4.6 | Gambar 4.3 hasil Round Robin dari docs/evidence/detail-rr.png |
| Kata pengantar | PREFACE | Format lazim, terima kasih kepada dosen, AI disebut (Codex dan Claude) |
| Panduan di ZIP | docs/PANDUAN-PENGGUNA.md | Judul netral; contekan tanya-jawab dan sapaan "kamu" dihapus; latihan dan pemecahan masalah ditambah |
| Panduan pemilik | OWNER.md | Tabel berkas dan apakah ikut ZIP; jumlah halaman dan konfirmasi mata kuliah diperbarui |
| Perhitungan manual | docs/PERHITUNGAN-MANUAL.md | Alasan P3 masuk sebelum P1 ditulis eksplisit |
| AI | docs/PENGGUNAAN-AI.md | Claude disebut bersama Codex |
| Pemeriksa paket | scripts/check_package.py | `.\mulai.bat test`; sebelumnya gagal palsu jika NoDefaultCurrentDirectoryInExePath=1 |

Versi sebelum T39 diarsipkan: `arsip/report_content-T38.py.txt`,
`arsip/Laporan-T38-sebelum-keterbacaan.pdf`, `arsip/OWNER-T38.md`.

| Pemeriksaan | Perintah | Hasil | Bukti |
|---|---|---|---|
| Suite aplikasi | .tools\python\python.exe run.py test | exit 0; tiga berkas lulus | evidence/tests-keterbacaan.txt |
| Render PDF | Python Blender 4.5 scripts/build_report.py | 40 halaman, isi 5–39 (35 halaman) | evidence/report-build-keterbacaan.txt, report-check.json |
| Tinjau visual | 40 render PNG dalam lembar kontak | Tidak ada luapan/tumpang tindih; beberapa halaman berakhir lebih awal karena gambar dijaga utuh | evidence/report-pages/ |
| Rujukan | grep [1]–[11] pada LAPORAN.md | Semua rujukan masih dikutip | — |
| Paket | package_project.py lalu check_package.py | 100 entri; 8 cek lulus, launcher exit 0 | evidence/package-check.json, package-tests.txt |

Kegagalan yang dicatat: check_package pertama gagal (`'mulai.bat' is not
recognized`) karena variabel lingkungan sesi; dari folder ekstraksi yang sama
`.\mulai.bat test` lulus. Kode aplikasi (src/, web/) tidak diubah pada T39;
tes browser dan screenshot tidak dijalankan ulang (BELUM DIJALANKAN untuk T39).

# Hasil revisi audit — T32 sampai T38

Tanggal review: 25 Oktober 2026, Asia/Jakarta.
Pelaksana dan pemeriksa: Codex. **LULUS pemeriksaan mandiri teknis**, bukan
review independen atau bukti penguasaan materi oleh mahasiswa.
Versi hasil T31 ada pada `arsip/HASIL-T31-sebelum-audit.md`; semua riwayat
tetap dipertahankan. Klasifikasi masukan anonim ada di `REVIEW-AUDIT.md`.

## Artefak terbaru

- `output/pdf/Laporan-Simulator-Sistem-Operasi.pdf`: 37 halaman, lima BAB.
  Halaman isi 5–36 (32 halaman), di luar sampul, kata pengantar, abstrak,
  daftar isi dan daftar pustaka. Jumlah berasal dari render, bukan perkiraan.
- `output/Proyek-Blessya.zip`: paket akademik 100 entri termasuk MANIFEST.json.
  Kode, runtime, tes, laporan, panduan dan data ikut; dokumen koordinasi kerja
  serta arsip tidak ikut. Semua modul tambahan dipertahankan.
- `docs/LAPORAN.md`: salinan isi; generator memakai scripts/report_content.py.
- `docs/PANDUAN-PENGGUNA.md`: penggunaan dan latihan presentasi terpisah.
- `docs/PENGGUNAAN-AI.md`: bantuan AI diungkapkan, juga pada kata pengantar.

Sampul berisi Blessya, NIM 001202400107, kelas Cyber Security, President
University, dosen Mam Ocha. Nama tugas **Data Structure** mengikuti jawaban
awal; pertanyaan konfirmasi ulang mata kuliah belum dijawab. Fakultas dan
gelar/nama lengkap dosen tidak ditebak. Kebijakan AI kampus belum diberikan.

## Perubahan yang diverifikasi

| Fokus | Lokasi | Hasil |
|---|---|---|
| Soal asli | tugas.md | Hanya persyaratan sampai minimum 20 halaman; jawaban chat diarsipkan |
| JSON kompleks | src/server.py: Handler.do_POST | RecursionError/ValueError saat parsing menjadi HTTP 400 |
| Regresi HTTP | tests/test_core.py: HTTPRobustnessTests | JSON 10.000 tingkat dan angka 5.000 digit; request valid sesudahnya tetap 200 |
| Penjelasan jeda | web/index.html: delay-note | Parameter ms dibedakan dari waktu aktual |
| Aktor tunggal | web/js/belajar.js: renderReplay | Tampilan Produsen/Konsumen; ID raw log tidak diubah |
| Analisis data | scripts/analyze_timing.py | Hitungan BLOKIR, FIFO, snapshot dan kapasitas 15 run cocok |
| Laporan | report_content.py, build_report.py | Lima BAB, teori tambahan, diagram, sumber primer, nada akademik |
| Paket | scripts/package_project.py, check_package.py | Daftar izin eksplisit dan pemeriksaan isi/hash dari hasil ekstraksi |

## Bukti dan perintah aktual

| Pemeriksaan | Perintah dari root proyek | Hasil | Bukti |
|---|---|---|---|
| Regresi parser | .tools\python\python.exe tests/test_core.py HTTPRobustnessTests | 1 kasus dengan subkasus, OK; 400/400/200 | evidence/json-after-fix.txt |
| Seluruh aplikasi | .tools\python\python.exe run.py test | 59 pemeriksaan HTTP, 20 scheduling, 21 kasus unittest; exit 0 | evidence/tests-audit.txt |
| Trace tersimpan | .tools\python\python.exe scripts/analyze_timing.py | 15 run terverifikasi, data asal tidak diubah | evidence/timing-analysis.json |
| Browser | node scripts/check_browser.cjs, server port 8765 | 20 alur lulus; tidak ada pageerror | evidence/browser-audit.txt, browser-results.json |
| Screenshot detail | node scripts/report_screenshots.cjs | Gambar aktual versi revisi | evidence/detail-*.png |
| Render PDF | Python Blender 3.11.11 menjalankan scripts/build_report.py dengan paket lokal ReportLab/PyMuPDF | 37 halaman, 32 halaman isi | evidence/report-build-audit.txt, report-check.json |
| Paket | .tools\python\python.exe scripts/package_project.py | ZIP dan MANIFEST.json dengan SHA-256 | output/package-manifest.json |
| Ekstraksi | .tools\python\python.exe scripts/check_package.py | 8 cek lulus, launcher exit 0, server uji dihentikan | evidence/package-check.json, package-tests.txt |

Angka pemeriksaan/assertion tidak disamakan dengan jumlah kasus unittest.
Tes paket menjalankan ulang ketiga suite lewat mulai.bat di folder ekstraksi,
kemudian memuat halaman/aset dan menjalankan dua endpoint inti. Runtime
aplikasi tetap Python portable 3.13.1 tanpa package tambahan.

## Hasil audit data dan sumber

Empat interval PRODUKSI pertama di setiap lima run produsen cepat menghasilkan
20 pengamatan dengan rentang **14,54–21,82 ms**, meskipun parameter jeda 10 ms.
Ini interval antarpencatatan, bukan pengukuran terisolasi Event.wait. Penyebab
spesifik resolusi timer Windows belum diisolasi. Rekonstruksi BLOKIR cocok
dengan ringkasan: dua kali per run produsen cepat. Angka ideal tiga tidak
menggantikan hasil log. Sumber data dan hash disimpan pada timing-analysis.json.

Sumber tambahan benar-benar dibaca: slide resmi OSC Bab 3/5/6; sampel resmi
Tanenbaum bagian 2.2 halaman 81–83; Dijkstra EWD123 bagian 3.2. Referensi teori
tidak dipakai sebagai sumber angka runtime. Tidak disimpulkan bahwa Tanenbaum
pasti buku pegangan kelas. URL dan bagian sumber ada pada SUMBER-TEORI.md
serta daftar pustaka. Berkas rujukan penuh tidak ikut didistribusikan.

## Pemeriksaan isi dan tampilan PDF

Semua halaman ditinjau dari render PNG, termasuk diagram, tabel, pseudocode,
gambar dan daftar pustaka. Tidak ditemukan teks/gambar keluar halaman atau
tumpang tindih. Pseudocode dijaga dalam satu halaman. Tabel lintas halaman
mengulang kepala tabel. Subbab tidak memakai pemisah halaman paksa; hanya
BAB dan bagian awal/akhir yang memulai halaman baru.

Iterasi layout awal revisi menghasilkan 44 halaman dengan luapan pendek.
Spasi, margin dan paragraf berulang dirapikan sampai 37 halaman. Perbaikan
nomor gambar terakhir hanya mengubah halaman 24/25 berdasarkan hash render,
dan keduanya ditinjau ulang pada ukuran penuh. Identitas diperiksa lewat
render dan teks PDF. Istilah pemilik, bab audit internal, dan tabel contekan
presentasi tidak ada lagi dalam isi laporan.

## Kegagalan yang tetap dicatat

Regresi baru awalnya gagal pada integer 5.000 digit. Penanganan RecursionError
saja belum menyelesaikan subkasus ini; ValueError parsing kemudian ditangani.
Log sebelum perbaikan dan perbaikan parsial tetap tersedia. Kedalaman awal
2.000 belum memicu batas decoder lingkungan ini, sehingga kasus dinaikkan
ke 10.000. Hasil terakhir lulus. Tidak mengubah log gagal menjadi klaim lulus.

Pengambilan sumber melalui web sempat gagal untuk berkas PPTX/PDF tertentu;
berkas kemudian diperoleh dari situs penulis melalui unduhan langsung dan
dibaca lokal. Presentasi audit privat tidak berhasil diakses; penilaian
berdasarkan teks audit yang ditempelkan, kode, data dan dokumen proyek.

## Keterbatasan tersisa

- Konfirmasi ulang nama mata kuliah belum dijawab; sampul mengikuti data
  eksplisit sebelumnya. Format khusus kampus/kebijakan AI belum diberikan.
- Pengujian di luar Windows/Chrome BELUM DIJALANKAN. Seluruh interleaving
  thread dan kemungkinan input tidak dicakup; bounded waiting tidak dibuktikan.
- Review visual mendalam seluruh modul tambahan BELUM DIJALANKAN; akses
  halaman lanjutan dan pemeriksaan HTTP terkait lulus.
- Pemahaman mahasiswa dan efektivitas pembelajaran belum dinilai.
- Proyek lokal tidak dipublikasikan dan tidak diklaim siap sebagai layanan publik.

Tidak ada revisi teknis wajib yang tertunda. Bukti terbaru menggantikan klaim
kesiapan laporan/paket versi T31, sementara riwayat lama tetap dapat ditelusuri.
