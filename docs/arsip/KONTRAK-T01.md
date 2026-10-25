# T01 — Petakan alur FCFS

Status: SIAP DIBERIKAN, belum dikerjakan.
Pelaksana: Antigravity. Reviewer: Codex.

## Tujuan tunggal

Mengetahui alur FCFS dari input pengguna sampai hasil ditampilkan. Ini audit
baca-saja terhadap satu fitur, bukan tugas perbaikan atau pembuatan fitur.

## Baca terlebih dahulu

`AGENTS.md`, `docs/RENCANA-KERJA.md`, dan `docs/STATUS-KERJA.md`.

## Pekerjaan

Telusuri implementasi FCFS, endpoint yang memanggilnya, serta kontrol dan
hasilnya di web. Titik awal pencarian: `src/scheduling/algorithms.py`,
`src/scheduling/models.py`, `src/server.py`, `web/index.html`, dan
`web/js/scheduling.js`. Lokasi tersebut petunjuk; pastikan fungsi yang nyata
ada di kode. Tulis peta ringkas:

| Bagian alur FCFS | File dan fungsi/elemen terkait | Perilaku menurut kode | Kesenjangan terhadap rencana |
|---|---|---|---|

Jelaskan input yang diterima, aturan pemilihan proses menurut kode, serta
asal Gantt chart dan metrik yang ditampilkan. Cukup ringkasan dan rujukan
fungsi/elemen; tidak perlu menyalin kode panjang. Jika tidak dapat dipastikan,
tulis BELUM DIKETAHUI dengan alasan.

## Batas

- Boleh membaca file proyek yang relevan.
- Hanya boleh mengubah `docs/HASIL-TUGAS.md` dan bagian status T01 di
  `docs/STATUS-KERJA.md` menjadi SIAP REVIEW.
- Tidak mengubah kode, dokumentasi lain, dependency, atau konfigurasi.
- Tidak menjalankan server, tes, atau instalasi dalam tugas ini; baseline
  eksekusi adalah tugas T04.
- Jangan mengaudit Round Robin, Producer–Consumer, atau fitur tambahan.

## Diterima jika

- Input, endpoint, algoritma FCFS dan tampilan hasil mempunyai lokasi file
  serta fungsi/elemen yang dapat diperiksa.
- Hubungan backend dengan tampilan dijelaskan ringkas.
- Fakta dari pembacaan kode dibedakan dari perilaku runtime yang belum diuji.
- Ada daftar kesenjangan konkret, atau pernyataan bahwa belum ada kesenjangan
  yang ditemukan dalam batas audit ini; bukan klaim bahwa sistem pasti benar.
- Tidak ada file aplikasi yang diubah dan tidak ada klaim tes lulus.

## Penyerahan

Isi `docs/HASIL-TUGAS.md`, catat daftar file yang berubah, lalu berhenti.
Jangan mengerjakan T02 sebelum Codex mereview T01.

## Prompt siap salin untuk Antigravity

```text
Bekerjalah di D:\blessya. Baca AGENTS.md, docs/RENCANA-KERJA.md,
docs/STATUS-KERJA.md, lalu docs/TUGAS-AKTIF.md.
Kerjakan hanya T01: petakan alur FCFS dari input sampai hasil.
Ikuti batas file dan kriteria penerimaan dalam kontrak tugas tersebut.
Ini audit baca-saja pada aplikasi; jangan ubah kode atau jalankan tes/server.
Isi docs/HASIL-TUGAS.md dengan temuan dan bukti lokasi file/fungsi.
Perbarui status T01 menjadi SIAP REVIEW, lalu berhenti untuk review Codex.
Jangan melanjutkan ke T02 atau menyatakan tugas LULUS sendiri.
```
