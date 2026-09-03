# Sistem Absensi Face Recognition (YuNet + SFace)

Sistem absensi pegawai berbasis **Face Recognition** menggunakan **YuNet** untuk deteksi wajah dan **SFace** untuk pengenalan wajah, dilengkapi dengan **liveness detection** dan pencatatan lokasi **GPS**. Dibangun menggunakan **Flask** dan **SQLite**.

## Daftar Isi

- [Latar Belakang](#latar-belakang)
- [Tujuan](#tujuan)
- [Manfaat](#manfaat)
- [Alat dan Bahan](#alat-dan-bahan)
- [Source Code](#source-code)
- [Instalasi](#instalasi)
- [Konfigurasi Model](#konfigurasi-model)
- [Penggunaan](#penggunaan)

## Latar Belakang

Kehadiran pegawai merupakan bagian penting dalam administrasi perusahaan sehingga diperlukan sistem absensi yang akurat dan aman. Sistem absensi konvensional masih memiliki risiko kesalahan pencatatan dan manipulasi identitas.

Sistem ini dikembangkan menggunakan:
- **YuNet** — deteksi wajah
- **SFace** — pengenalan wajah
- **Liveness detection** — memastikan pengguna berada langsung di depan kamera
- **GPS** — mencatat koordinat, akurasi, dan lokasi saat absensi

Aplikasi dibangun menggunakan Flask dan SQLite dengan pengelolaan akses untuk administrator dan pegawai.

## Tujuan

1. Mengembangkan aplikasi absensi pegawai berbasis Face Recognition.
2. Menerapkan deteksi wajah dan pengenalan wajah untuk verifikasi identitas pegawai.
3. Menerapkan liveness detection untuk meningkatkan keamanan proses verifikasi.
4. Menambahkan pencatatan lokasi GPS saat pegawai melakukan absensi.
5. Menyimpan data absensi, informasi lokasi, confidence, dan foto hasil absensi ke dalam basis data.
6. Menyediakan halaman riwayat absensi bagi pegawai dan administrator.
7. Menerapkan sistem autentikasi dan pembatasan akses berdasarkan role pengguna.
8. Menghasilkan sistem absensi yang dapat digunakan melalui antarmuka web secara terintegrasi.

## Manfaat

**Bagi Pegawai**
Absensi dapat dilakukan melalui kamera tanpa kartu atau input identitas manual. Pegawai juga dapat melihat riwayat absensinya sendiri.

**Bagi Administrator**
Dapat mengelola data pegawai, dataset wajah, serta melihat riwayat absensi lengkap dengan informasi lokasi.

**Bagi Perusahaan**
Proses pencatatan kehadiran menjadi lebih terstruktur, dengan informasi tambahan dari Face Recognition, liveness detection, dan GPS.

**Bagi Pengembangan Teknologi**
Menjadi implementasi Computer Vision, Face Recognition, liveness detection, GPS, web framework, dan basis data dalam satu sistem terintegrasi.

## Alat dan Bahan

### Perangkat Keras (Hardware)

| No. | Alat | Fungsi |
|---|---|---|
| 1 | Laptop/PC/Server | Menjalankan aplikasi dan pengolahan data |
| 2 | Kamera/Webcam | Mengambil gambar wajah pegawai |
| 3 | Jaringan Wi-Fi/LAN | Menghubungkan perangkat dengan server |
| 4 | Smartphone | Melakukan absensi dan mendapatkan lokasi GPS |
| 5 | Media penyimpanan | Menyimpan dataset wajah dan foto absensi |

### Perangkat Lunak (Software)

| No. | Software | Fungsi |
|---|---|---|
| 1 | Python | Bahasa pemrograman utama |
| 2 | Flask | Framework aplikasi web |
| 3 | OpenCV | Pengolahan citra dan kamera |
| 4 | YuNet | Deteksi wajah |
| 5 | SFace | Pengenalan wajah |
| 6 | SQLite | Penyimpanan database |
| 7 | HTML, CSS, JavaScript | Tampilan aplikasi |
| 8 | Browser | Mengakses sistem absensi |

### Library Python yang Digunakan

| No. | Library | Fungsi |
|---|---|---|
| 1 | Flask | Membuat aplikasi web |
| 2 | OpenCV (cv2) | Pengolahan gambar, kamera, dan deteksi wajah |
| 3 | NumPy | Pengolahan data numerik dan citra |
| 4 | YuNet | Deteksi wajah |
| 5 | SFace | Pengenalan dan pencocokan wajah |
| 6 | SQLite3 | Pengelolaan database |
| 7 | Werkzeug | Pengelolaan password dan kebutuhan Flask |
| 8 | Base64 | Konversi gambar ke format data |
| 9 | UUID | Membuat identitas unik |
| 10 | OS / Shutil | Pengelolaan file dan folder |
| 11 | Threading | Menjalankan proses secara bersamaan |
| 12 | Datetime | Pengelolaan tanggal dan waktu |

### Versi yang Digunakan

| Komponen | Versi |
|---|---|
| Ubuntu | 18.04 |
| Python | 3.6.7 |
| OpenCV | 4.8.1 |
| CMake | 3.10.2 |
| GCC/G++ | 7.5.0 |
| NumPy | 2.2.4 |
| YuNet | `face_detection_yunet_2023mar.onnx` |
| SFace | `face_recognition_sface_2021dec.onnx` |

## Source Code

- **GitHub:** https://github.com/Diardii/face_recoginition
- **Google Drive:** https://drive.google.com/file/d/1SB8DcUMpB3_udJHJEqaWAi3AQ65PIP6D/view?usp=drive_link

## Instalasi

### 1. Install Python

1. Download dan install Python.
2. Saat instalasi, aktifkan opsi **Add Python to PATH**.
3. Periksa instalasi dengan:

   ```bash
   python --version
   ```

### 2. Membuat Virtual Environment

1. Buka Command Prompt dan masuk ke folder project.
2. Buat virtual environment:

   ```bash
   python -m venv venv
   ```

3. Aktifkan virtual environment:

   ```bash
   venv\Scripts\activate
   ```

   Jika berhasil, akan muncul `(venv)` di awal baris Command Prompt.

### 3. Install Library

Install seluruh library yang dibutuhkan menggunakan `pip` (lihat daftar library pada bagian [Alat dan Bahan](#alat-dan-bahan)).

### 4. Persiapan Project

- Salin folder project `face-recognition0.1` ke komputer/server.
- Buka folder tersebut menggunakan Visual Studio Code atau text editor lainnya.

## Konfigurasi Model

1. Siapkan file model **YuNet** untuk deteksi wajah: `face_detection_yunet_2023mar.onnx`
2. Siapkan file model **SFace** untuk pengenalan wajah: `face_recognition_sface_2021dec.onnx`
3. Letakkan kedua file model pada folder yang sesuai dengan konfigurasi project.
4. Pastikan nama dan lokasi file model sesuai dengan yang digunakan program.
5. Siapkan folder dataset untuk menyimpan data wajah pegawai (digunakan sebagai referensi pengenalan wajah), dan pastikan aplikasi memiliki akses baca/tulis pada folder tersebut.

## Penggunaan

### Setup Data Person (Admin)

1. Jalankan sistem dengan menjalankan `app.py`.
2. Akses aplikasi melalui IP tempat Flask dijalankan, lalu login menggunakan akun admin:

   | Field | Nilai |
   |---|---|
   | Username | `admin` |
   | Password | `Username` |

3. Masuk ke halaman **Tambah Person** melalui menu navigasi.
4. Tekan tombol **Tambah Person** untuk menambahkan pegawai baru.

   > Catatan: Username dan Password yang dibuat di sini digunakan sebagai login akun user.

5. Setelah user dibuat, akun tersebut dapat digunakan untuk menambahkan dataset wajah di halaman user.

### Alur Penggunaan (User)

1. User login menggunakan akun yang dibuat oleh admin. Pada login pertama, user akan diarahkan ke halaman **registrasi wajah** untuk membuat dataset.
2. Setelah proses pembuatan embedding wajah selesai, sistem siap digunakan. Setiap pengguna hanya dapat melakukan absensi **1x datang** dan **1x pulang** per hari. Halaman utama juga menampilkan **riwayat absensi** pengguna.

---

*Dokumentasi disusun oleh: Lorent Chascha Ahmad Ibrahim, Moch Ardiansyah, Rafky Rayhan Abimanyu — 2026*