# Status dan ingatan kerja

Terakhir diperbarui: 24 Oktober 2026 (Asia/Jakarta).

## Posisi saat ini

Persiapan dokumen rencana: SELESAI.
Pelaksanaan oleh Antigravity: BELUM DIMULAI.
Tugas aktif: T01, SIAP REVIEW; hasil berada di `HASIL-TUGAS.md`.
Pelaksana T01: Codex, berdasarkan permintaan langsung pemilik untuk mengerjakan
tugas yang telah disiapkan. Tidak ada hasil yang diatribusikan ke Antigravity.
Langkah terdekat: review hasil T01; T02 BELUM DIMULAI.
Tidak ada tugas implementasi yang dinyatakan lulus.

## Fakta yang sudah diperiksa oleh Codex

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

## Belum diketahui

- Hasil tes aktual, kebenaran tiap algoritma, dan kondisi tampilan browser.
- Kesesuaian implementasi Producer–Consumer dengan cakupan baru.
- Isi lengkap dan ketepatan OWNER serta perhitungan manual.
- Format laporan dosen dan aturan penghitungan halaman di luar isi.

## Keputusan tetap

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

Baca aturan dan ketiga dokumen awal sesuai `AGENTS.md`. Periksa hasil tugas:
jika masih template, jangan menganggap Antigravity sudah bekerja; jika ada
hasil baru, cocokkan dengan kode dan bukti sebelum memutuskan review. Setelah
hasil diterima, simpan bukti dan keputusan dalam riwayat sebelum mengganti
kontrak atau hasil tugas aktif. Antrean bukan izin menjalankan semua tugas.

## Format entri review berikutnya

- ID tugas dan tanggal:
- File yang berubah:
- Bukti yang diperiksa reviewer:
- Hasil: LULUS / PERLU REVISI / TERHAMBAT.
- Alasan dan keterbatasan:
- Temuan di luar tugas untuk antrean:
- Langkah berikutnya:

Pertahankan riwayat ringkas di sini sebelum mengganti hasil tugas aktif.
