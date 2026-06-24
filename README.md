# SIPUSTAKA — Sistem Peminjaman Buku (Django + PostgreSQL Raw SQL)

Tugas Akhir CRUD Django. UI sesuai mockup (sidebar gelap, konten terang),
Raw SQL via `connection.cursor()`, validasi form, dropdown untuk pilihan tetap,
Foreign Key pada tabel peminjaman, bonus dashboard counter + bar chart.

## Modul
- Dashboard: counter Total Buku, Total Judul, Sedang Dipinjam, Dikembalikan + analisis stok & ringkasan transaksi.
- Buku: List, Tambah, Detail, Edit, Hapus.
- User (Siswa): List, Tambah, Detail, Edit, Hapus.
- Peminjaman: List, Pinjam Buku, Tombol Kembalikan.

## Jalankan

```bash
pip install -r requirements.txt

# === PostgreSQL (default, sesuai ketentuan) ===
# Buat database dulu: CREATE DATABASE sipustaka;
# Konfigurasi via env var: DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT
python manage.py migrate
python manage.py seed_data        # data dummy sesuai mockup
python manage.py runserver

# === ATAU pakai SQLite untuk uji cepat ===
USE_SQLITE=1 python manage.py migrate
USE_SQLITE=1 python manage.py seed_data
USE_SQLITE=1 python manage.py runserver
```

Buka http://127.0.0.1:8000/

## Struktur Database (Raw SQL — `0001_initial.py`)
- `buku` (id PK, judul, pengarang, kategori, penerbit, tahun_terbit, isbn, rak, stok, deskripsi)
- `siswa` (id PK, nama, kelas, nis UNIQUE, is_active)
- `peminjaman` (id PK, siswa_id FK→siswa, buku_id FK→buku, tanggal_pinjam, jatuh_tempo, keperluan, catatan, petugas, status)

Dropdown:
- Kategori: Novel, Sejarah, Pendidikan
- Rak: Rak A-01 … Rak A-05
- Status peminjaman: Dipinjam, Dikembalikan, Terlambat
