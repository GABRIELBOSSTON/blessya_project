2. To create a simple system to illustrate (for educational purposes)
min 2 materials from this list:
- Process and Threads
- IPC & Classical Problems
- Process Scheduling
- Deadlock: Ostrich & Detection Recovery Algs
- Deadlock: Avoidance & Prevention Algs
- Memory mgt, Swapping & Memory Allocation
- Fit Algorithms & Virtual Memory
- Page Replacement Alg & Modeling
- Segmentation
- Principle of IO hardware and software
- Block stream & Character Oriented Terminals
- File System & Review for exam
3. Report, consist of materials/explanation and the documentations, min pages is 20 pages


Aplikasi dan tes dua-duanya jalan. Berikut cara menjalankannya.

## Menjalankan tes

```
cd D:\blessya
py run.py test
```

**Jangan tambahkan `| Select-String` atau `| Select-Object`.** Itu penyebab "GAGAL" palsu yang saya temui tadi: pipe PowerShell menutup aliran lebih awal, Python kena *broken pipe*, exit code jadi 1 padahal semua tes lulus. Kalau mau menyimpan hasilnya, alihkan ke berkas:

```
py run.py test > hasil-tes.txt 2>&1
```

Bisa juga per berkas kalau mau cepat:

```
py tests\test_core.py
py tests\test_api.py
py tests\test_scheduling.py
```

## Menjalankan aplikasinya

```
py run.py
```

Browser terbuka sendiri. Kalau port 8000 dipakai: `py run.py --port 9000`. Untuk keluaran teks yang bisa di-copy ke laporan: `py run.py demo`.

## Hasil tes aktual — 24 Oktober 2026

| Berkas | Hasil |
|---|---|
| `test_api.py` | 59 lulus, 0 gagal |
| `test_core.py` | 20 tes unittest, `OK` (1.123s) |
| `test_scheduling.py` | 20 lulus, 0 gagal |
| **Total** | **99 pemeriksaan, 0 gagal**, exit code 0 |

Verifikasi tambahan yang saya jalankan sendiri: `GET /` → 200 (6599 byte), `POST /api/scheduling` → 200.

## Dua hal yang perlu kamu tahu

**Output merah di PowerShell itu normal.** `test_core.py` pakai `unittest`, yang menulis progresnya (`... ok`) ke **stderr**. PowerShell merender stderr sebagai blok merah `NativeCommandError` yang tampak seperti crash. Bukan error — isinya `ok` semua, ditutup `Ran 20 tests ... OK`. Kalau mau tidak merah: `py run.py test 2>&1 | Out-Host`, atau redirect ke berkas seperti di atas.

**Dua angka berubah dibanding pemeriksaan sebelumnya.** Pesan validasi burst sekarang "Lama proses P1 harus bilangan bulat 1 sampai 50" (sebelumnya nilainya dipotong diam-diam — ini perbaikan), dan `index.html` turun ke 6599 byte dari 10.8 KB, konsisten dengan penyederhanaan UI di T08–T10. Keduanya tampak sejalan dengan rencana, jadi saya tidak mengubah apa pun.

## Batas pemeriksaan ini

Yang saya buktikan hanya: tes lulus, server merespons, satu endpoint menjawab 200. Saya **belum** memeriksa tampilan di browser secara visual, belum menjalankan demo Producer–Consumer di layar, dan belum menilai apakah penjelasannya mudah dipahami. Itu cakupan T13–T14.

Mau saya catat hasil ini sebagai bukti baseline **T04** di [docs/STATUS-KERJA.md](docs/STATUS-KERJA.md) dan [docs/HASIL-TUGAS.md](docs/HASIL-TUGAS.md)? Formatnya sudah ada di sana, dan T04 memang persis meminta ini — perintah, hasil aktual, kegagalan, dan batas cakupan tes.