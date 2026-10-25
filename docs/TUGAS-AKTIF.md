# Penyelesaian proyek sesuai mandat terbaru

Status 25 Oktober 2026: **T39 keterbacaan selesai** (lihat HASIL-TUGAS.md);
nama tugas Data Structure dikonfirmasi pemilik. Riwayat sebelumnya:
**REVISI TEKNIS SELESAI, T32–T38 lulus**.
bukti ada di `REVIEW-AUDIT.md`. Status selesai T31
adalah hasil review sebelumnya; kualitas laporan dan paket dibuka kembali.
Hasil dan keterbatasan tersedia pada `HASIL-TUGAS.md`; riwayat per fokus
tersedia pada `STATUS-KERJA.md`.

Pemilik meminta proyek selesai sampai aplikasi dan laporan siap digunakan,
tampilan simpel, dan penjelasan mudah dipahami. Codex pelaksana dan pemeriksa;
pemeriksaan mandiri tidak disebut review independen. Kontrak T01 ada di arsip.

Urutan pekerjaan:
1. T01–T07: audit, baseline tes, verifikasi manual dan perbaikan inti.
2. T08–T14: sederhanakan dua halaman utama, periksa browser dan validasi.
3. T15–T19: panduan, perhitungan, kerangka dan sumber teori.
4. T20–T30: laporan, percobaan, screenshot dan PDF minimal 20 halaman.
5. T31: review akhir aplikasi, dokumen dan cara menjalankan.

Batas perubahan: file proyek D:\blessya; modul tambahan dipertahankan.
Tooling laporan/pengujian dipisahkan dari runtime aplikasi. Tidak mengubah
instalasi sistem atau mempublikasikan berkas. Simpan bukti di docs/evidence.

Kriteria selesai: tes relevan lulus, demo browser berjalan, bug inti diperbaiki,
panduan cocok, PDF dirender dan diperiksa serta jumlah halaman diverifikasi.
Identitas akademik yang belum diberikan tidak boleh ditebak.

Identitas: Blessya, NIM 001202400107, kelas Cyber Security, nama tugas
Data Structure. Institusi President University, dosen Mam Ocha, sesuai
informasi terbaru pemilik. Fakultas belum diberikan dan tidak dicantumkan.
Persyaratan materi tetap mengacu pada daftar dalam `tugas.md`.

## Antrean revisi audit

Satu fokus dikerjakan dan dicatat sebelum beralih ke fokus berikutnya.

| ID | Fokus | Batas berkas | Kriteria selesai |
|---|---|---|---|
| T32 | Pulihkan soal dan klasifikasikan audit | tugas.md, docs/arsip, dokumen kerja | Soal cocok dengan teks asli; asal chat dan konflik dicatat |
| T33 | Tangani JSON terlalu bersarang | src/server.py, tests/test_core.py | HTTP 400; server tetap melayani request berikutnya |
| T34 | Bedakan jeda masukan dari waktu aktual | web/index.html, belajar.js, scripts analisis, docs/evidence | Angka berdasarkan trace asli; UI jelas; identitas aktor tetap terlacak |
| T35 | Perbaiki sudut pandang dan struktur laporan | generator/isi laporan, sumber teori, PDF | Lima bab, teori relevan, sumber dibaca, tanpa narasi penyerahan internal |
| T36 | Periksa PDF revisi | PDF, renderer, bukti | Minimal 20 halaman isi setelah render; semua halaman ditinjau |
| T37 | Pisahkan paket akademik dari berkas kerja | scripts paket, README/panduan, ZIP | Daftar isi paket eksplisit; runtime, kode, laporan dan data tersedia; dokumen kerja tidak ikut |
| T38 | Uji dan tutup revisi | tes browser/paket, dokumen kerja | Bukti terbaru, isi ZIP cocok, sisa klarifikasi dilaporkan |

Nama mata kuliah masih mengikuti jawaban awal Data Structure; konfirmasi
ulang pertanyaan pertama belum dijawab. Sampul sudah memuat kampus/dosen.
Tidak menebak kebijakan kampus atau menyatakan AI sudah disetujui dosen.
Tidak ada pekerjaan teknis yang masih aktif. Laporan dan paket revisi ada di
output/; keterbatasan dan bukti terbaru dicatat pada HASIL-TUGAS.md.
