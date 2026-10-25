# Status dan ingatan kerja

Terakhir diperbarui: 25 Oktober 2026 (Asia/Jakarta).

## Posisi saat ini

**T39 KETERBACAAN SELESAI (25 Oktober 2026, Claude atas permintaan langsung pemilik).**
Laporan kini 40 halaman (35 halaman isi), ada daftar istilah, analogi, gambar
Round Robin, dan kesimpulan yang menjawab rumusan masalah. Panduan di ZIP dibuat
netral (tanpa contekan presentasi). Nama tugas **Data Structure dikonfirmasi
pemilik** pada 25 Oktober 2026. Rincian di `HASIL-TUGAS.md` bagian T39.
Angka "37 halaman" dan "konfirmasi ulang belum dijawab" di bawah adalah riwayat T38.

**REVISI TEKNIS SELESAI — T32–T38 lulus pemeriksaan mandiri.** Review T01–T31 sebelumnya dipertahankan
sebagai riwayat, tetapi penyerahan laporan dan paket ditinjau ulang setelah
masukan anonim. Persoalan sudut pandang akademik dan isi ZIP terlewat pada
review awal; status lulus lama bukan bukti bahwa temuan baru sudah ditangani.
Mandat terbaru pemilik mengizinkan penyelesaian penuh tanpa menunggu per tugas.
Ini bukan review independen; tidak ada hasil yang diatribusikan ke Antigravity.

- Aplikasi: dua materi inti, FCFS/Round Robin dan Producer–Consumer.
- Halaman utama disederhanakan; modul tambahan tetap tersedia.
- Laporan revisi: lima BAB, PDF 37 halaman, termasuk 32 halaman isi.
- Paket Windows: `output/Proyek-Blessya.zip`, runtime Python ikut disertakan.
- Mulai: klik `mulai.bat`; panduan demo ada di `OWNER.md`.
- Sampul: Blessya, 001202400107, Cyber Security, nama tugas Data Structure.
- Institusi: President University; dosen: Mam Ocha (sesuai informasi pemilik).
- Hasil terbaru: 59 pemeriksaan HTTP, 20 scheduling, 21 kasus unittest;
  20 alur browser dan 8 pemeriksaan paket lulus.
- ZIP akademik tidak memuat AGENTS, status, kontrak tugas, atau arsip internal;
  pengungkapan penggunaan AI tetap disertakan.
- Bukti dan keterbatasan: `HASIL-TUGAS.md` serta `evidence/`.

Nama tugas Data Structure mengikuti jawaban pemilik sebelumnya; pertanyaan
konfirmasi ulang nama mata kuliah belum dijawab. Materi tetap sesuai daftar
dosen dalam `tugas.md`. Kampus/dosen sudah diberikan; fakultas tidak ditebak. Tambahan
chat pada `tugas.md` sebelumnya keliru disebut catatan pemilik. Audit memberi
konteks bahwa itu jawaban asisten yang tersalin; soal dipulihkan pada T32
dan versi tercampur disimpan sebagai arsip internal. Format khusus dosen
belum tersedia, sehingga dipakai A4, Times New Roman 12 pt untuk isi laporan.

## Posisi audit awal 24 Oktober (riwayat yang telah digantikan)

Persiapan dokumen rencana: SELESAI.
Pelaksanaan oleh Antigravity: BELUM DIMULAI.
Tugas aktif: T01, SIAP REVIEW; hasil berada di `HASIL-TUGAS.md`.
Pelaksana T01: Codex, berdasarkan permintaan langsung pemilik untuk mengerjakan
tugas yang telah disiapkan. Tidak ada hasil yang diatribusikan ke Antigravity.
Langkah terdekat: review hasil T01; T02 BELUM DIMULAI.
Tidak ada tugas implementasi yang dinyatakan lulus.

## Fakta yang diperiksa pada audit awal (riwayat)

- `tugas.md` berisi syarat minimal dua materi dan laporan minimal 20 halaman.
- Ada `run.py`, `src/server.py`, direktori scheduling, ipc, deadlock,
  direktori web, serta dua file tes: `test_scheduling.py` dan `test_api.py`.
- Ada `OWNER.md`, `README.md`, `docs/LAPORAN.md`, dan
  `docs/PERHITUNGAN-MANUAL.md`.
- Bagian awal README dan rangka laporan masih menjelaskan cakupan tiga materi.
- README menyebut 79 pemeriksaan. Ini klaim dokumentasi lama, BELUM diverifikasi
  ulang dalam pekerjaan ini.

Bukti inspeksi awal: daftar file dengan `rg --files`, pembacaan `tugas.md`,
95 baris awal README dan 65 baris awal rangka laporan pada 24 Oktober 2026.
Inspeksi ini tidak membuktikan fungsi program benar atau server dapat berjalan.

## Belum diketahui pada audit awal (riwayat)

- Hasil tes aktual, kebenaran tiap algoritma, dan kondisi tampilan browser.
- Kesesuaian implementasi Producer–Consumer dengan cakupan baru.
- Isi lengkap dan ketepatan OWNER serta perhitungan manual.
- Format laporan dosen dan aturan penghitungan halaman di luar isi.

Butir teknis di atas sudah diperiksa pada hasil akhir. Format khusus dari dosen
tetap belum diketahui; 25 halaman isi melampaui batas 20 tanpa menghitung sampul.
Salinan status awal lengkap ada di `arsip/STATUS-AWAL.md`.

## Keputusan awal (digantikan mandat penyelesaian penuh)

- Fokus dua modul sesuai `RENCANA-KERJA.md`; kode tambahan dipertahankan.
- Antigravity pelaksana; Codex pemberi tugas dan reviewer.
- Satu tugas, satu hasil review; tidak melanjutkan otomatis.
- Dokumen lama belum diselaraskan; gunakan rencana baru untuk cakupan dan
  gunakan kode/output aktual untuk membuktikan perilaku program.

## Riwayat

| Tanggal | ID | Status | Bukti dan keputusan |
|---|---|---|---|
| 2026-10-24 | Persiapan | SELESAI | Aturan, rencana, status, kontrak T01 dan template hasil dibuat; kode aplikasi tidak diubah |
| 2026-10-24 | T01 | SIAP DIBERIKAN | Audit baca-saja disiapkan; belum dikirim atau dikerjakan |
| 2026-10-24 | Persiapan | DIPERJELAS | T01 diperkecil menjadi alur FCFS; audit RR dan Producer–Consumer dipisah. Antrean diperbarui menjadi T01–T31 sebelum pelaksanaan |
| 2026-10-24 | T01 | SIAP REVIEW | Codex memetakan alur FCFS lewat pembacaan kode; bukti di HASIL-TUGAS.md. Temuan F01–F06 meliputi penyederhanaan UI, kontrak mode single, validasi angka, nama IDLE dan batas model. Kode aplikasi serta tes tidak dijalankan/diubah; belum ada keputusan review |

## Melanjutkan setelah percakapan terputus

Baca aturan dan ketiga dokumen awal sesuai `AGENTS.md`, kemudian hasil akhir.
Tidak ada tugas implementasi wajib yang tersisa. Untuk revisi berikutnya,
buat fokus kecil baru, simpan bukti lama, dan periksa bagian yang berubah.
Program selesai tidak berarti pemilik sudah mempelajari cara menjelaskannya.

## Review T01–T31 — versi sebelum audit, 25 Oktober 2026

Tanggal berikut adalah tanggal keputusan review. Tes, percobaan dan browser
awal berlangsung 24 Oktober; pengujian paket dan identitas akhir 25 Oktober.
Implementasi dan review dilakukan Codex berdasarkan mandat terbaru pemilik.

| ID | Hasil | Bukti dan keputusan |
|---|---|---|
| Mandat | DIPERBARUI | Kewajiban menunggu Antigravity/per tugas diganti penyelesaian berurutan; bukti dan kesederhanaan tetap wajib |
| T01 | LULUS | Audit FCFS disimpan di arsip/T01.md; alur akhir runCPU → api_scheduling → fcfs diperiksa |
| T02 | LULUS | round_robin: kedatangan pada batas quantum sebelum antre ulang; batas giliran tetap terlihat |
| T03 | LULUS | run_demo memakai thread nyata; semaphore dan mutex melindungi buffer; UI memutar rekaman |
| T04 | LULUS | baseline.txt: 79 pemeriksaan lama; tes akhir menambah 20 kasus regresi |
| T05 | LULUS | FCFS manual 0–5, 5–8, 8–9; waiting 0,4,6 cocok dengan fungsi, HTTP dan browser |
| T06 | LULUS | RR quantum 2: waiting rata-rata 3,33, respons 1; batas kedatangan, idle dan quantum besar diuji |
| T07 | LULUS | FIFO, snapshot, kapasitas, banyak pekerja, error dan timeout; thread selesai/bersih pada tes |
| T08 | LULUS | Dua tab inti dan tautan lanjutan; kode materi tambahan dipertahankan |
| T09 | LULUS | FCFS, RR, perbandingan, grafik dan metrik; ui-fcfs.png dan ui-perbandingan.png |
| T10 | LULUS | Buffer, preset kecepatan, langkah/putar/jeda dan ringkasan akhir; ui-buffer.png |
| T11 | LULUS | Integer/rentang/ID unik/IDLE dan pesan kesalahan diuji pada API dan browser |
| T12 | LULUS | Kapasitas, barang, pekerja dan jeda divalidasi; kapasitas nol ditolak di browser |
| T13 | LULUS | Alur scheduling, perbandingan, ekspor dan input salah termasuk 18 cek browser |
| T14 | LULUS | Seluruh langkah replay, kontrol, preset dan layout ponsel diperiksa |
| T15 | LULUS | OWNER.md cocok dengan launcher, dua demo, rumus, pertanyaan dan batas model |
| T16 | LULUS | README.md cocok dengan endpoint, runtime, struktur dan tooling terpisah |
| T17 | LULUS | PERHITUNGAN-MANUAL.md memakai contoh yang sama dengan UI/experiments.json |
| T18 | LULUS | Struktur 25 bagian berisi teori, rancangan, implementasi, percobaan dan dokumentasi |
| T19 | LULUS | Enam referensi primer OSTEP/Python diakses 24 Oktober dan dipakai sesuai konsep |
| T20 | LULUS | Pendahuluan, tujuan dan ruang lingkup sesuai dua materi |
| T21 | LULUS | FCFS/RR, rumus, tie-break dan definisi switch sesuai kode |
| T22 | LULUS | Thread, semaphore, mutex dan batas satu proses dijelaskan |
| T23 | LULUS | Arsitektur browser/server/fungsi serta kontrak input sesuai implementasi |
| T24 | LULUS | Implementasi dan screenshot hasil scheduling aktual masuk laporan |
| T25 | LULUS | Implementasi dan screenshot replay Producer–Consumer aktual masuk laporan |
| T26 | LULUS | Percobaan quantum, convoy dan idle dianalisis dari experiments.json |
| T27 | LULUS | Lima ulangan pada tiga skenario buffer; 15 run selesai tanpa thread tertinggal |
| T28 | LULUS | Kesimpulan dibatasi pada dataset/model; tidak mengklaim algoritma terbaik universal |
| T29 | LULUS | Kutipan [1]–[6] dan URL primer konsisten; hasil aplikasi dibedakan dari teori |
| T30 | LULUS | PDF 28 halaman dirender dan diperiksa visual, termasuk revisi sampul |
| T31 | LULUS | Paket diekstrak; mulai.bat test, aset web dan dua endpoint berjalan; 6 cek paket lulus |

## Format entri review berikutnya

## Riwayat revisi audit — 25 Oktober 2026

| ID | Hasil | Bukti dan keputusan |
|---|---|---|
| T32 | LULUS | Soal asli dipulihkan; chat diarsipkan, atribusi keliru dikoreksi; REVIEW-AUDIT.md membedakan temuan benar dan klaim belum terbukti |
| T33 | LULUS | JSON 10.000 tingkat dan angka 5.000 digit ditolak HTTP 400; request valid berikutnya 200; log gagal/berhasil dipertahankan |
| T34 | LULUS | 15 trace direkonstruksi; 20 interval awal 14,54–21,82 ms; hitungan menunggu cocok. UI menyebut jeda diminta dan label aktor tunggal |
| T35 | LULUS | Lima BAB, sudut pandang akademik, teori tambahan dan 11 rujukan; panduan latihan terpisah; bantuan AI diungkapkan |
| T36 | LULUS | 37 halaman dirender, 32 halaman isi. Semua halaman diperiksa melalui render; revisi nomor gambar hanya mengubah halaman 24/25 dan diperiksa kembali |
| T37 | LULUS | ZIP akademik berisi 100 entri termasuk MANIFEST.json; daftar izin berkas memisahkan dokumen koordinasi/arsip dari penyerahan |
| T38 | LULUS TEKNIS | 59+20 pemeriksaan, 21 kasus unittest; 20 alur browser; 8 cek paket lulus. Sampul memakai nama mata kuliah terakhir dari pemilik; konfirmasi ulang belum dijawab |
| T41 | LULUS (pemeriksaan mandiri Claude) | Desain ulang gaya shadcn: tokens.css bersama, belajar.css dan style.css ditulis ulang (halaman tambahan dari gelap ke terang), font Geist/Fira Code lokal (OFL), MIME woff2 di server, warna SVG/palet, tombol kembali, bug panah `&rarr;` diperbaiki. Kontras teks ≥4,5:1 diverifikasi. run.py test exit 0; 20 alur browser lulus (salinan skrip di port 8799 karena 8765 dipakai proses lain); 11 screenshot dan PDF 40 hlm diperbarui; 8 cek paket lulus |
| T40 | LULUS (pemeriksaan mandiri Claude) | PANDUAN-PENGGUNA ditulis ulang untuk pembaca awam: kamus istilah 3 tabel, langkah menjalankan, fungsi setiap tombol/kolom kedua tab dan halaman tambahan, pesan kesalahan, 5 screenshot. Angka contoh dicocokkan dengan kode. mulai.bat dan lanjutan.html kini merujuk panduan (OWNER.md tidak ikut ZIP). run.py test exit 0; 8 cek paket lulus |
| T39 | LULUS (pemeriksaan mandiri Claude) | Bahasa laporan disederhanakan, daftar istilah 1.4, gambar RR 4.3; PDF 40 hlm/35 isi, 40 render ditinjau; PANDUAN-PENGGUNA netral; check_package memakai .\mulai.bat; run.py test exit 0; 8 cek paket lulus. Data Structure dikonfirmasi pemilik |

## Format entri review berikutnya

- ID tugas dan tanggal:
- File yang berubah:
- Bukti yang diperiksa reviewer:
- Hasil: LULUS / PERLU REVISI / TERHAMBAT.
- Alasan dan keterbatasan:
- Temuan di luar tugas untuk antrean:
- Langkah berikutnya:

Pertahankan riwayat ringkas di sini sebelum mengganti hasil tugas aktif.
