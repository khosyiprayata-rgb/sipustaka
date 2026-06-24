from django.core.management.base import BaseCommand
from django.db import connection
from datetime import date, timedelta

class Command(BaseCommand):
    help = "Seed sample SIPUSTAKA data"

    def handle(self, *args, **kw):
        with connection.cursor() as c:
            c.execute("DELETE FROM peminjaman")
            c.execute("DELETE FROM siswa")
            c.execute("DELETE FROM buku")
            buku = [
                ("Laskar Pelangi", "Andrea Hirata", "Novel", "Bentang Pustaka", 2005, "978-979-3062-79-2", "Rak A-01", 5,
                 "Novel tentang perjuangan anak-anak Belitung mengejar pendidikan."),
                ("Bumi", "Tere Liye", "Novel", "Gramedia Pustaka Utama", 2014, "978-602-03-0721-6", "Rak A-02", 7,
                 "Petualangan Raib di dunia paralel."),
                ("Negeri 5 Menara", "A. Fuadi", "Novel", "Gramedia Pustaka Utama", 2009, "978-979-22-4861-6", "Rak A-03", 2,
                 "Kisah enam santri dan mantra 'man jadda wajada'."),
            ]
            for b in buku:
                c.execute("""INSERT INTO buku (judul,pengarang,kategori,penerbit,tahun_terbit,isbn,rak,stok,deskripsi)
                             VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""", b)
            siswa = [
                ("Roni", "XI IPA 1", "2026001", True),
                ("Sinta", "XI IPS 2", "2026002", True),
                ("Dewi Anggraini", "X IPA 3", "2026003", True),
                ("Bima Pratama", "XII IPS 1", "2026004", True),
            ]
            for s in siswa:
                c.execute("INSERT INTO siswa (nama,kelas,nis,is_active) VALUES (%s,%s,%s,%s)", s)

            c.execute("SELECT id FROM siswa ORDER BY id")
            sids = [r[0] for r in c.fetchall()]
            c.execute("SELECT id FROM buku ORDER BY id")
            bids = [r[0] for r in c.fetchall()]

            today = date.today()
            pinjam = [
                (sids[0], bids[0], today - timedelta(days=2), today + timedelta(days=5),
                 "Tugas sekolah", "Referensi tugas Bahasa Indonesia.", "Budi Siregar", "Dipinjam"),
                (sids[1], bids[1], today - timedelta(days=1), today + timedelta(days=6),
                 "Bacaan pribadi", "", "Budi Siregar", "Dipinjam"),
            ]
            for p in pinjam:
                c.execute("""INSERT INTO peminjaman
                    (siswa_id,buku_id,tanggal_pinjam,jatuh_tempo,keperluan,catatan,petugas,status)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""", p)
        self.stdout.write(self.style.SUCCESS("Data dummy berhasil dibuat."))
