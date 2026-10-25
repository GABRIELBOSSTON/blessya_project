# Rencana kerja yang bisa direview satu per satu

Tanggal keputusan: 24 Oktober 2026 (Asia/Jakarta).

Pembaruan mandat: pemilik mengizinkan Codex menyelesaikan semua tahap dan
perbaikan tanpa menunggu persetujuan per tugas. Antrean T01–T31 tetap menjadi
daftar pemeriksaan; pekerjaan yang berkaitan dapat ditangani dalam satu tahap
terukur, dengan bukti dan hasil review ditulis pada STATUS-KERJA.md.

Status 25 Oktober 2026: T01–T31 selesai pada versi awal; setelah audit,
T32–T38 menyelesaikan revisi laporan, ketahanan parser JSON dan paket akademik.
Rincian fokus dan bukti revisi ada pada TUGAS-AKTIF.md dan REVIEW-AUDIT.md. Prosedur
lama tentang menunggu Antigravity di bawah dipertahankan sebagai riwayat;
mandat terbaru di atas menjadi acuan pelaksanaan. Lihat STATUS-KERJA.md dan
HASIL-TUGAS.md untuk bukti aktual, bukan perkiraan pada rencana awal.

## Kesepakatan

Judul kerja: **Simulator Edukasi Penjadwalan CPU dan Sinkronisasi Producer–Consumer**.
Sumber persyaratan dosen: `tugas.md`. Minimal dua materi dan laporan minimal
20 halaman. Tidak ada dasar untuk menganggap penambahan fitur menjamin nilai lebih tinggi.

Sistem inti mempunyai dua halaman/modul:

1. Scheduling: input proses, arrival time, burst time; FCFS dan Round Robin
   dengan quantum; Gantt chart, waktu tunggu dan turnaround, serta penjelasan hasil.
2. Producer–Consumer: satu produsen dan satu konsumen, buffer terbatas
   (contoh awal lima tempat), pengaturan kecepatan, isi buffer dan penjelasan
   kondisi menunggu saat penuh/kosong. Implementasi menggunakan thread Python.

Gunakan Python dan HTML/CSS/JavaScript yang sudah ada. Hindari penambahan
framework. Simulator CPU adalah model edukasi, bukan pengendali scheduler OS.
Producer–Consumer memperagakan masalah klasik sinkronisasi dalam satu proses.
Detail apakah visual diputar dari log atau diperbarui saat eksekusi ditentukan
setelah audit; antarmuka harus menjelaskannya dengan benar.

Fitur lain yang sudah ada menjadi tambahan di luar pembahasan inti. Jangan
menghapusnya hanya untuk menyederhanakan proyek.

## Cara menjalankan rencana

Urutan berikut adalah antrean, bukan satu instruksi untuk mengerjakan semuanya.
Setiap baris harus mendapat kontrak tugas sendiri di `TUGAS-AKTIF.md`, batas
file, bukti yang diminta, dan review sebelum melanjutkan. Jika ditemukan bug,
buat satu tugas per bug yang relevan sebelum pekerjaan bergantung padanya.
Jangan mengubah kode hanya untuk memenuhi antrean jika implementasi sudah benar.

| ID | Satu fokus pekerjaan | Hasil yang direview |
|---|---|---|
| T01 | Petakan alur FCFS tanpa edit kode | Lokasi input, endpoint, algoritma dan tampilan hasil |
| T02 | Petakan alur Round Robin tanpa edit kode | Lokasi quantum, antrean, algoritma dan hasil |
| T03 | Petakan alur Producer–Consumer tanpa edit kode | Thread, sinkronisasi, kontrol dan sumber visualisasi |
| T04 | Jalankan pemeriksaan bawaan sebagai baseline | Perintah, hasil aktual, kegagalan dan batas cakupan tes |
| T05 | Verifikasi FCFS dengan contoh manual kecil | Input, Gantt dan metrik manual dibandingkan program |
| T06 | Verifikasi Round Robin dengan contoh manual kecil | Quantum, aturan antrean termasuk kedatangan di batas quantum, hasil pembanding |
| T07 | Periksa sinkronisasi Producer–Consumer | Bukti urutan data, batas buffer, menunggu, dan penghentian thread |
| T08 | Sederhanakan navigasi ke dua modul inti | Tampilan awal jelas; fitur lama tetap tersimpan |
| T09 | Sederhanakan tampilan scheduling | Input FCFS/RR, hasil dan penjelasan mudah dibaca |
| T10 | Sederhanakan tampilan Producer–Consumer | Buffer, kontrol dan kondisi menunggu mudah dipahami |
| T11 | Periksa input tidak valid pada scheduling | Pesan yang jelas; tidak crash atau menggantung |
| T12 | Periksa input tidak valid pada Producer–Consumer | Pesan yang jelas; tidak crash atau menggantung |
| T13 | Verifikasi demo scheduling di browser | Bukti demo dan daftar masalah tersisa |
| T14 | Verifikasi demo Producer–Consumer di browser | Bukti demo dan daftar masalah tersisa |
| T15 | Sesuaikan OWNER.md dengan sistem yang direview | Panduan awam dan langkah demo yang benar-benar cocok |
| T16 | Sesuaikan README.md | Cara menjalankan dan cakupan teknis yang terverifikasi |
| T17 | Perbarui perhitungan manual inti | Contoh scheduling yang cocok dengan hasil review |
| T18 | Tetapkan kerangka laporan | Struktur dua materi dan pembagian isi |
| T19 | Periksa sumber teori laporan | Referensi yang benar-benar diakses dan relevansinya |
| T20 | Tulis pendahuluan laporan | Tujuan, masalah dan batasan sesuai sistem |
| T21 | Tulis teori scheduling | Teori FCFS/RR, rumus dan sumber yang jelas |
| T22 | Tulis teori Producer–Consumer | Buffer, thread, semaphore, mutex dan batas model |
| T23 | Tulis perancangan sistem | Diagram dan alur sesuai implementasi aktual |
| T24 | Dokumentasikan implementasi scheduling | Penjelasan dan screenshot hasil aktual |
| T25 | Dokumentasikan implementasi Producer–Consumer | Penjelasan dan screenshot hasil aktual |
| T26 | Tulis analisis percobaan scheduling | Perbandingan FCFS/RR dan pengaruh quantum |
| T27 | Tulis analisis percobaan Producer–Consumer | Percobaan produsen cepat dan konsumen cepat |
| T28 | Tulis kesimpulan | Kesimpulan didukung hasil percobaan |
| T29 | Rapikan kutipan dan daftar pustaka | Sumber konsisten dengan teori yang digunakan |
| T30 | Susun dokumen final dan periksa halaman | Dokumen dirender, minimal 20 halaman dan layout diperiksa |
| T31 | Review penyerahan akhir | Program, panduan, laporan dan bukti konsisten |

Tugas tampilan yang ternyata memerlukan perubahan backend harus dipecah;
jangan menyelipkan perubahan backend besar ke dalam tugas tampilan.
Antrean dapat diperkecil lagi berdasarkan temuan review. Nomor bukan ukuran
kemajuan: satu tugas hanya selesai setelah hasilnya diterima. Untuk tugas
yang menghasilkan banyak temuan, pilih satu temuan untuk satu tugas perbaikan.

## Rencana laporan

Target awal 22 halaman isi, di luar sampul dan daftar isi: pendahuluan 2,
teori 5, perancangan 4, implementasi 4, pengujian/analisis 6, kesimpulan 1.
Ini perkiraan alokasi, bukan janji jumlah halaman. Format dari dosen belum
tersedia; format final dicatat saat penyusunan. Referensi ditambahkan sesuai
sumber yang benar-benar dipakai. Jangan memenuhi halaman dengan pengulangan.

## Selesai berarti

- Dua materi dapat diperagakan dan dijelaskan oleh pemilik.
- Hasil algoritma dan sinkronisasi mempunyai bukti verifikasi.
- Alur browser diuji, bukan hanya API.
- Panduan cocok dengan versi yang diserahkan.
- Laporan final benar-benar dirender dan memenuhi minimal 20 halaman.
- Tidak ada temuan penting yang ditutup tanpa bukti atau dicatat seolah selesai.
