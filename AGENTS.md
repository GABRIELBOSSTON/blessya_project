# Aturan kerja proyek

## Arahan pemilik terbaru 24 Oktober 2026

Pemilik meminta Codex menyelesaikan seluruh proyek, memperbaiki bug dan
melakukan perubahan yang diperlukan sampai selesai. Arahan ini menggantikan
kewajiban menyerahkan implementasi kepada Antigravity dan berhenti menunggu
perintah setiap tugas. Codex boleh mengerjakan dan memeriksa tahap berikutnya
secara berurutan, mencatat bukti dan keputusan review. Ketentuan bukti,
kesederhanaan, dua materi inti, dan mempertahankan modul tambahan tetap berlaku.
Tidak ada agen tambahan yang diperlukan; kerja dilakukan oleh Codex.
Bagian pembagian peran lama di bawah dipertahankan sebagai riwayat awal.

## Mulai di sini

Baca `docs/RENCANA-KERJA.md`, lalu `docs/STATUS-KERJA.md`, lalu
`docs/TUGAS-AKTIF.md` sebelum bekerja. Instruksi langsung pemilik mengungguli
dokumen ini. Jika ada konflik antardokumen, catat konflik; jangan menebak.

## Tujuan dan pembagian peran

Proyek individu untuk memperagakan minimal dua materi Sistem Operasi dan
menghasilkan laporan minimal 20 halaman. Cakupan inti yang disepakati:
Process Scheduling (FCFS dan Round Robin) serta IPC & Classical Problems
(Producer–Consumer menggunakan thread, buffer terbatas, semaphore, mutex).

- Pemilik menetapkan kebutuhan dan menilai kemudahan pemahaman.
- Codex menyiapkan satu tugas kecil, mereview hasil, dan mencatat keputusan review.
- Antigravity mengerjakan hanya tugas aktif dan menyerahkan bukti hasil.
- Jangan menjalankan agen lain atau mengirim tugas secara otomatis.
- Satu tugas aktif saja. Pelaksana berhenti setelah menyerahkan hasil; tidak
  mengambil pekerjaan berikutnya sampai review Codex menyatakan LULUS.

## Disiplin bukti

- Percakapan lama dan dokumentasi lama adalah petunjuk, bukan bukti tes terbaru.
- Bedakan: fakta yang diperiksa, klaim belum diverifikasi, dan rencana.
- Jangan mengarang keluaran terminal, screenshot, referensi, atau jumlah halaman.
- Klaim implementasi harus menunjuk file/fungsi; klaim pengujian harus memiliki
  perintah, hasil aktual, tanggal, serta keterbatasan pemeriksaan.
- Tes gagal tetap dilaporkan. Tes yang tidak dijalankan ditulis BELUM DIJALANKAN.
- Perkiraan halaman Markdown bukan jumlah halaman laporan final.
- Thread dalam satu proses tidak boleh disebut IPC antarproses yang terpisah.

## Batas perubahan

- Jangan menulis ulang proyek dari nol atau menambah materi/dependency tanpa kebutuhan.
- Pertahankan kode fitur tambahan yang sudah ada. Pengurangan tampilan utama
  bukan izin menghapus modul deadlock, race condition, atau Dining Philosophers.
- Jangan memperbaiki hal di luar tugas aktif. Catat sebagai temuan untuk tugas lain.
- Jika tugas terlalu besar, berhenti pada temuan dan usulkan pemecahan tugas.
- Jangan menimpa perubahan pemilik. Periksa kondisi file sebelum mengedit.
- Baca `docs/TUGAS-AKTIF.md` sebagai kontrak batas file dan kriteria penerimaan.

## Serah terima dan review

Pelaksana mengisi `docs/HASIL-TUGAS.md` menggunakan format yang tersedia dan
menandai tugas SIAP REVIEW di status, tanpa menyatakan LULUS sendiri.
Codex memeriksa perubahan serta bukti yang relevan, lalu memutuskan LULUS,
PERLU REVISI, atau TERHAMBAT beserta alasannya. Lulus tes saja tidak menggantikan
pemeriksaan konsep dan tampilan ketika tugas menyangkut keduanya.

Setelah review, tambahkan riwayat di `docs/STATUS-KERJA.md`. Jangan hapus
riwayat lama. Tugas berikutnya baru dibuat konkret setelah hasil ini diterima.
