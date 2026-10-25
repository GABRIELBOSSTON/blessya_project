# Tindak lanjut audit anonim

Tanggal review: 25 Oktober 2026, Asia/Jakarta. Sumber masukan: teks audit
yang ditempelkan pemilik. Tautan slide privat tidak dapat dibuka melalui alat
web, sehingga isi slide/catatan pembicara tidak diklaim sudah diperiksa.

| Temuan | Penilaian berdasarkan berkas saat ini | Tindakan |
|---|---|---|
| Sudut pandang pemilik/pihak ketiga | BENAR; penulisan akademik tercampur penyerahan pekerjaan | Revisi isi dan hilangkan panduan presentasi dari laporan |
| Nama mata kuliah salah | BELUM PASTI; Data Structure berasal dari jawaban pemilik | Klarifikasi diminta, tidak menyimpulkan mata kuliah hanya dari daftar topik |
| Institusi/dosen wajib | BELUM PASTI; template tidak diberikan | Minta data, tidak membuat nama atau aturan kampus |
| tugas.md tercampur jawaban chat | BENAR; atribusi catatan pemilik sebelumnya keliru | T32: soal dipulihkan; versi bercampur diarsipkan |
| Laporan 25 bagian datar | BENAR | Kelompokkan lima BAB, subbab mengalir, tambah teori relevan |
| Banyak halaman kosong | Audit kedua mengoreksi klaimnya sendiri | Tidak memakai dugaan; jumlah dan layout diperiksa setelah render |
| Sumber hanya dua keluarga | BENAR | Baca sumber primer tambahan; tidak menganggap Tanenbaum pasti buku kuliah |
| Riwayat berhenti T01 | TIDAK SESUAI versi yang diperiksa | T01–T31 sudah ada pada tabel Review penyelesaian; judul tabel diperjelas |
| Aktor Produsen-1 membingungkan | Perbaikan kejelasan, bukan bug | Tampilan inti menyebut Produsen/Konsumen; ID log tetap dipertahankan |
| ZIP membawa dokumen kerja | BENAR | Paket akademik memakai daftar izin berkas; dokumen kerja/arsip tetap lokal |
| Jeda 10 ms bukan interval 10 ms | BENAR | UI dan laporan membedakan parameter, interval kejadian, serta pemutaran |
| Semua interval 15–17 ms disebabkan timer Windows | TERLALU PASTI | 20 interval produksi awal berjangkauan 14,54–21,82 ms; penyebab tidak diisolasi |
| Hitungan tunggu seharusnya 3 | TIDAK MENGGANTIKAN DATA | Rekonstruksi log cocok: 2 kejadian pada setiap run produsen cepat |
| RecursionError JSON tidak ditangani | BENAR pada pembacaan handler awal | T33: tangkap RecursionError dan ValueError; uji HTTP 400 lalu request normal |
| Sinkronisasi tanpa risiko deadlock sama sekali | TERLALU MUTLAK | Urutan semaphore-before-mutex benar; tes empiris dan cancel bukan bukti semua jadwal pasti selesai |

## Bukti fokus yang sudah ditutup

- **T32 LULUS:** `tugas.md` hanya berisi soal sampai syarat 20 halaman.
  Versi chat di `arsip/tugas-sebelum-pemulihan.md`; bukan lagi berkas soal aktif.
  Ukuran hasil 607 byte dengan akhir baris Windows; ukuran byte audit bukan
  kriteria dibandingkan kesamaan isi instruksi.
- **T33 LULUS:** satu kasus HTTP memiliki subkasus JSON 10.000 tingkat dan
  integer 5.000 digit. Keduanya HTTP 400; request valid berikutnya HTTP 200.
  Perintah `.tools/python/python.exe tests/test_core.py HTTPRobustnessTests`.
  Log `evidence/json-after-fix.txt` berakhir `Ran 1 test ... OK`.
  Percobaan sebelum perbaikan dan perbaikan parsial gagal pada integer panjang;
  log kegagalan tetap di `json-before-fix.txt` dan `json-partial-fix.txt`.
  Kedalaman awal 2.000 belum memicu batas decoder lingkungan ini, sehingga
  kasus ditingkatkan ke 10.000; tidak mengklaim log awal membuktikan keduanya.
- **T34 LULUS:** `scripts/analyze_timing.py` merekonstruksi 15 run, FIFO,
  snapshot, kapasitas dan hitungan BLOKIR cocok. Bukti `timing-analysis.json`
  mencatat hash data asal dan metode interval. Nilai asli tidak diganti.
  Browser memeriksa keterangan jeda dan label aktor; 20 alur lulus pada
  `browser-results.json`. Screenshot detail laporan diperbarui terpisah.

## Ruang kerja dan pengungkapan bantuan

Dokumen kerja dipisahkan karena tidak termasuk materi penyerahan akademik,
bukan untuk membuat klaim pengerjaan tanpa bantuan. Laporan mencantumkan
bantuan AI pada penyusunan kode, dokumentasi dan pemeriksaan. Belum ada
informasi kebijakan AI kampus, sehingga tidak dinyatakan sudah mendapat izin.
Tidak ada klaim bahwa pemilik sudah memahami atau memvalidasi sendiri hasilnya.

## Hasil T35–T38

- T35: laporan menjadi lima BAB dengan kata pengantar, abstrak, daftar isi,
  tambahan teori dan 11 entri rujukan. Panduan presentasi dipisahkan;
  narasi pemilik/penyerahan internal dihapus. Bantuan AI dinyatakan terbuka.
- T36: PDF 37 halaman, 32 halaman isi (halaman 5–36), daftar pustaka halaman
  37. Semua render ditinjau; pseudocode dijaga agar tidak terbelah halaman.
  Perbaikan nomor gambar hanya mengubah halaman 24/25 (diperiksa ulang).
- T37: ZIP akademik memakai daftar izin eksplisit, 100 entri termasuk manifest;
  dokumen kerja/arsip tidak ikut, pengungkapan bantuan AI tetap ikut.
- T38: suite aplikasi lulus (59 HTTP, 20 scheduling, 21 kasus unittest),
  20 alur browser dan 8 cek paket hasil ekstraksi lulus. Log paket ada pada
  package-check.json dan package-tests.txt. CRC dan hash manifest cocok.

Sampul: President University, Mam Ocha, Blessya, 001202400107, Cyber Security.
Nama mata kuliah tetap Data Structure dari jawaban awal; konfirmasi ulang
pertanyaan pertama belum dijawab. Ini ketidakpastian administrasi yang tetap
dinyatakan, bukan alasan mengganti nama mata kuliah secara sepihak.
