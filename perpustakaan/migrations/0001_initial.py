from django.db import migrations

SQL_UP = """
CREATE TABLE IF NOT EXISTS buku (
    id SERIAL PRIMARY KEY,
    judul VARCHAR(200) NOT NULL,
    pengarang VARCHAR(150) NOT NULL,
    kategori VARCHAR(50) NOT NULL,
    penerbit VARCHAR(150) NOT NULL,
    tahun_terbit INTEGER NOT NULL,
    isbn VARCHAR(30) DEFAULT '',
    rak VARCHAR(20) NOT NULL,
    stok INTEGER NOT NULL DEFAULT 0,
    deskripsi TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS siswa (
    id SERIAL PRIMARY KEY,
    nama VARCHAR(150) NOT NULL,
    kelas VARCHAR(50) NOT NULL,
    nis VARCHAR(30) UNIQUE NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS peminjaman (
    id SERIAL PRIMARY KEY,
    siswa_id INTEGER NOT NULL REFERENCES siswa(id) ON DELETE CASCADE,
    buku_id INTEGER NOT NULL REFERENCES buku(id) ON DELETE CASCADE,
    tanggal_pinjam DATE NOT NULL,
    jatuh_tempo DATE NOT NULL,
    keperluan TEXT DEFAULT '',
    catatan TEXT DEFAULT '',
    petugas VARCHAR(100) DEFAULT 'Budi Siregar',
    status VARCHAR(20) NOT NULL DEFAULT 'Dipinjam'
);
"""

# SQLite-compatible version (untuk fallback testing)
SQL_UP_SQLITE = """
CREATE TABLE IF NOT EXISTS buku (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    judul VARCHAR(200) NOT NULL,
    pengarang VARCHAR(150) NOT NULL,
    kategori VARCHAR(50) NOT NULL,
    penerbit VARCHAR(150) NOT NULL,
    tahun_terbit INTEGER NOT NULL,
    isbn VARCHAR(30) DEFAULT '',
    rak VARCHAR(20) NOT NULL,
    stok INTEGER NOT NULL DEFAULT 0,
    deskripsi TEXT DEFAULT ''
);
CREATE TABLE IF NOT EXISTS siswa (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nama VARCHAR(150) NOT NULL,
    kelas VARCHAR(50) NOT NULL,
    nis VARCHAR(30) UNIQUE NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT 1
);
CREATE TABLE IF NOT EXISTS peminjaman (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    siswa_id INTEGER NOT NULL REFERENCES siswa(id) ON DELETE CASCADE,
    buku_id INTEGER NOT NULL REFERENCES buku(id) ON DELETE CASCADE,
    tanggal_pinjam DATE NOT NULL,
    jatuh_tempo DATE NOT NULL,
    keperluan TEXT DEFAULT '',
    catatan TEXT DEFAULT '',
    petugas VARCHAR(100) DEFAULT 'Budi Siregar',
    status VARCHAR(20) NOT NULL DEFAULT 'Dipinjam'
);
"""

SQL_DOWN = """
DROP TABLE IF EXISTS peminjaman;
DROP TABLE IF EXISTS siswa;
DROP TABLE IF EXISTS buku;
"""

def run_sql(apps, schema_editor):
    vendor = schema_editor.connection.vendor
    sql = SQL_UP_SQLITE if vendor == "sqlite" else SQL_UP
    with schema_editor.connection.cursor() as c:
        for stmt in sql.strip().split(";"):
            s = stmt.strip()
            if s:
                c.execute(s)

def run_sql_reverse(apps, schema_editor):
    with schema_editor.connection.cursor() as c:
        for stmt in SQL_DOWN.strip().split(";"):
            s = stmt.strip()
            if s:
                c.execute(s)

class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [migrations.RunPython(run_sql, run_sql_reverse)]
