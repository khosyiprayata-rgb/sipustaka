from django.shortcuts import render, redirect
from django.http import Http404
from django.db import connection
from django.contrib import messages
from datetime import date, timedelta

KATEGORI_CHOICES = ["Novel", "Sejarah", "Pendidikan"]
RAK_CHOICES = [f"Rak A-0{i}" for i in range(1, 6)]
KEPERLUAN_CHOICES = ["Tugas sekolah", "Bacaan pribadi", "Penelitian", "Lain-lain"]
STATUS_CHOICES = ["Dipinjam", "Dikembalikan", "Terlambat"]


def dictfetchall(cursor):
    cols = [c[0] for c in cursor.description]
    return [dict(zip(cols, row)) for row in cursor.fetchall()]


def dictfetchone(cursor):
    row = cursor.fetchone()
    if row is None:
        return None
    cols = [c[0] for c in cursor.description]
    return dict(zip(cols, row))


# ---------- DASHBOARD ----------
def dashboard(request):
    with connection.cursor() as c:
        c.execute("SELECT COALESCE(SUM(stok),0) FROM buku")
        total_buku = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM buku")
        total_judul = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM peminjaman WHERE status='Dipinjam'")
        sedang = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM peminjaman WHERE status='Dikembalikan'")
        kembali = c.fetchone()[0]
        c.execute("SELECT judul, stok FROM buku ORDER BY id")
        stok_buku = dictfetchall(c)

    max_stok = max([b["stok"] for b in stok_buku], default=1) or 1
    for b in stok_buku:
        b["pct"] = int(b["stok"] / max_stok * 100)

    max_trx = max(sedang, kembali, 1)
    transaksi = [
        {"label": "Sedang Dipinjam", "value": sedang, "pct": int(sedang / max_trx * 100), "color": "amber"},
        {"label": "Sudah Dikembalikan", "value": kembali, "pct": int(kembali / max_trx * 100), "color": "emerald"},
    ]
    ctx = {
        "active": "dashboard",
        "total_buku": total_buku,
        "total_judul": total_judul,
        "sedang": sedang,
        "kembali": kembali,
        "stok_buku": stok_buku,
        "transaksi": transaksi,
    }
    return render(request, "perpustakaan/dashboard.html", ctx)


# ---------- BUKU ----------
def buku_list(request):
    with connection.cursor() as c:
        c.execute("SELECT * FROM buku ORDER BY id")
        rows = dictfetchall(c)
    return render(request, "perpustakaan/buku_list.html", {"rows": rows, "active": "buku"})


def _validate_buku(post):
    errors = {}
    data = {
        "judul": post.get("judul", "").strip(),
        "pengarang": post.get("pengarang", "").strip(),
        "kategori": post.get("kategori", "").strip(),
        "penerbit": post.get("penerbit", "").strip(),
        "tahun_terbit": post.get("tahun_terbit", "").strip(),
        "isbn": post.get("isbn", "").strip(),
        "rak": post.get("rak", "").strip(),
        "stok": post.get("stok", "").strip(),
        "deskripsi": post.get("deskripsi", "").strip(),
    }
    if not data["judul"]:
        errors["judul"] = "Judul wajib diisi."
    if not data["pengarang"]:
        errors["pengarang"] = "Pengarang wajib diisi."
    if data["kategori"] not in KATEGORI_CHOICES:
        errors["kategori"] = "Pilih kategori yang valid."
    if not data["penerbit"]:
        errors["penerbit"] = "Penerbit wajib diisi."
    if data["rak"] not in RAK_CHOICES:
        errors["rak"] = "Pilih rak yang valid."
    try:
        data["tahun_terbit"] = int(data["tahun_terbit"])
    except ValueError:
        errors["tahun_terbit"] = "Tahun harus berupa angka."
    try:
        data["stok"] = int(data["stok"])
        if data["stok"] < 0:
            errors["stok"] = "Stok tidak boleh negatif."
    except ValueError:
        errors["stok"] = "Stok harus berupa angka."
    return data, errors


def buku_create(request):
    data, errors = {}, {}
    if request.method == "POST":
        data, errors = _validate_buku(request.POST)
        if not errors:
            with connection.cursor() as c:
                c.execute("""INSERT INTO buku (judul,pengarang,kategori,penerbit,tahun_terbit,isbn,rak,stok,deskripsi)
                             VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                          [data["judul"], data["pengarang"], data["kategori"], data["penerbit"],
                           data["tahun_terbit"], data["isbn"], data["rak"], data["stok"], data["deskripsi"]])
            messages.success(request, "Buku berhasil ditambahkan.")
            return redirect("buku_list")
    return render(request, "perpustakaan/buku_form.html", {
        "mode": "create", "data": data, "errors": errors,
        "kategori_choices": KATEGORI_CHOICES, "rak_choices": RAK_CHOICES, "active": "buku",
    })


def _get_buku(pk):
    with connection.cursor() as c:
        c.execute("SELECT * FROM buku WHERE id=%s", [pk])
        row = dictfetchone(c)
    if not row:
        raise Http404
    return row


def buku_detail(request, pk):
    return render(request, "perpustakaan/buku_detail.html", {"b": _get_buku(pk), "active": "buku"})


def buku_edit(request, pk):
    buku = _get_buku(pk)
    data, errors = buku, {}
    if request.method == "POST":
        data, errors = _validate_buku(request.POST)
        if not errors:
            with connection.cursor() as c:
                c.execute("""UPDATE buku SET judul=%s,pengarang=%s,kategori=%s,penerbit=%s,tahun_terbit=%s,
                             isbn=%s,rak=%s,stok=%s,deskripsi=%s WHERE id=%s""",
                          [data["judul"], data["pengarang"], data["kategori"], data["penerbit"],
                           data["tahun_terbit"], data["isbn"], data["rak"], data["stok"], data["deskripsi"], pk])
            messages.success(request, "Buku berhasil diperbarui.")
            return redirect("buku_detail", pk=pk)
    return render(request, "perpustakaan/buku_form.html", {
        "mode": "edit", "data": data, "errors": errors,
        "kategori_choices": KATEGORI_CHOICES, "rak_choices": RAK_CHOICES, "active": "buku", "pk": pk,
    })


def buku_delete(request, pk):
    buku = _get_buku(pk)
    if request.method == "POST":
        with connection.cursor() as c:
            c.execute("DELETE FROM buku WHERE id=%s", [pk])
        messages.success(request, "Buku berhasil dihapus.")
        return redirect("buku_list")
    return render(request, "perpustakaan/buku_delete.html", {"b": buku, "active": "buku"})


# ---------- SISWA ----------
def siswa_list(request):
    with connection.cursor() as c:
        c.execute("SELECT * FROM siswa ORDER BY id")
        rows = dictfetchall(c)
    return render(request, "perpustakaan/siswa_list.html", {"rows": rows, "active": "user"})


def _validate_siswa(post, exclude_id=None):
    errors = {}
    data = {
        "nama": post.get("nama", "").strip(),
        "kelas": post.get("kelas", "").strip(),
        "nis": post.get("nis", "").strip(),
        "is_active": post.get("status", "Aktif") == "Aktif",
    }
    if not data["nama"]:
        errors["nama"] = "Nama wajib diisi."
    if not data["kelas"]:
        errors["kelas"] = "Kelas wajib diisi."
    if not data["nis"]:
        errors["nis"] = "NIS wajib diisi."
    else:
        with connection.cursor() as c:
            if exclude_id:
                c.execute("SELECT id FROM siswa WHERE nis=%s AND id<>%s", [data["nis"], exclude_id])
            else:
                c.execute("SELECT id FROM siswa WHERE nis=%s", [data["nis"]])
            if c.fetchone():
                errors["nis"] = "NIS sudah digunakan."
    return data, errors


def siswa_create(request):
    data, errors = {"is_active": True}, {}
    if request.method == "POST":
        data, errors = _validate_siswa(request.POST)
        if not errors:
            with connection.cursor() as c:
                c.execute("INSERT INTO siswa (nama,kelas,nis,is_active) VALUES (%s,%s,%s,%s)",
                          [data["nama"], data["kelas"], data["nis"], data["is_active"]])
            messages.success(request, "User berhasil ditambahkan.")
            return redirect("siswa_list")
    return render(request, "perpustakaan/siswa_form.html",
                  {"mode": "create", "data": data, "errors": errors, "active": "user"})


def _get_siswa(pk):
    with connection.cursor() as c:
        c.execute("SELECT * FROM siswa WHERE id=%s", [pk])
        row = dictfetchone(c)
    if not row:
        raise Http404
    return row


def siswa_detail(request, pk):
    s = _get_siswa(pk)
    with connection.cursor() as c:
        c.execute("SELECT COUNT(*) FROM peminjaman WHERE siswa_id=%s", [pk])
        total = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM peminjaman WHERE siswa_id=%s AND status='Dipinjam'", [pk])
        aktif = c.fetchone()[0]
    return render(request, "perpustakaan/siswa_detail.html",
                  {"s": s, "total": total, "aktif": aktif, "active": "user"})


def siswa_edit(request, pk):
    siswa = _get_siswa(pk)
    data = dict(siswa)
    errors = {}
    if request.method == "POST":
        data, errors = _validate_siswa(request.POST, exclude_id=pk)
        if not errors:
            with connection.cursor() as c:
                c.execute("UPDATE siswa SET nama=%s,kelas=%s,nis=%s,is_active=%s WHERE id=%s",
                          [data["nama"], data["kelas"], data["nis"], data["is_active"], pk])
            messages.success(request, "User berhasil diperbarui.")
            return redirect("siswa_detail", pk=pk)
    return render(request, "perpustakaan/siswa_form.html",
                  {"mode": "edit", "data": data, "errors": errors, "active": "user", "pk": pk})


def siswa_delete(request, pk):
    s = _get_siswa(pk)
    if request.method == "POST":
        with connection.cursor() as c:
            c.execute("DELETE FROM siswa WHERE id=%s", [pk])
        messages.success(request, "User berhasil dihapus.")
        return redirect("siswa_list")
    return render(request, "perpustakaan/siswa_delete.html", {"s": s, "active": "user"})


# ---------- PEMINJAMAN ----------
def peminjaman_list(request):
    with connection.cursor() as c:
        c.execute("""SELECT p.*, s.nama AS nama_siswa, b.judul AS judul_buku
                     FROM peminjaman p
                     JOIN siswa s ON s.id=p.siswa_id
                     JOIN buku b ON b.id=p.buku_id
                     ORDER BY p.id""")
        rows = dictfetchall(c)
    return render(request, "perpustakaan/peminjaman_list.html", {"rows": rows, "active": "peminjaman"})


def peminjaman_create(request):
    with connection.cursor() as c:
        c.execute("SELECT id,nama,kelas,nis FROM siswa WHERE is_active=TRUE ORDER BY nama")
        siswa_opts = dictfetchall(c)
        c.execute("SELECT id,judul,stok FROM buku WHERE stok>0 ORDER BY judul")
        buku_opts = dictfetchall(c)

    today = date.today()
    data = {
        "tanggal_pinjam": today.isoformat(),
        "jatuh_tempo": (today + timedelta(days=7)).isoformat(),
        "petugas": "Budi Siregar",
        "keperluan": "Tugas sekolah",
        "status": "Dipinjam",
    }
    errors = {}
    if request.method == "POST":
        data = {k: request.POST.get(k, "").strip() for k in
                ["siswa_id", "buku_id", "tanggal_pinjam", "jatuh_tempo",
                 "keperluan", "catatan", "petugas", "status"]}
        if not data["siswa_id"]:
            errors["siswa_id"] = "Pilih peminjam."
        if not data["buku_id"]:
            errors["buku_id"] = "Pilih buku."
        if not data["tanggal_pinjam"]:
            errors["tanggal_pinjam"] = "Tanggal pinjam wajib."
        if not data["jatuh_tempo"]:
            errors["jatuh_tempo"] = "Jatuh tempo wajib."
        if data["keperluan"] not in KEPERLUAN_CHOICES:
            errors["keperluan"] = "Pilih keperluan."
        if data["status"] not in STATUS_CHOICES:
            data["status"] = "Dipinjam"
        if not errors:
            with connection.cursor() as c:
                c.execute("""INSERT INTO peminjaman
                    (siswa_id,buku_id,tanggal_pinjam,jatuh_tempo,keperluan,catatan,petugas,status)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""",
                    [data["siswa_id"], data["buku_id"], data["tanggal_pinjam"], data["jatuh_tempo"],
                     data["keperluan"], data.get("catatan", ""), data["petugas"] or "Budi Siregar", data["status"]])
                c.execute("UPDATE buku SET stok = stok - 1 WHERE id=%s AND stok>0", [data["buku_id"]])
            messages.success(request, "Peminjaman berhasil dicatat.")
            return redirect("peminjaman_list")
    return render(request, "perpustakaan/peminjaman_form.html", {
        "data": data, "errors": errors,
        "siswa_opts": siswa_opts, "buku_opts": buku_opts,
        "keperluan_choices": KEPERLUAN_CHOICES, "status_choices": STATUS_CHOICES,
        "active": "peminjaman",
    })


def peminjaman_return(request, pk):
    if request.method == "POST":
        with connection.cursor() as c:
            c.execute("SELECT buku_id, status FROM peminjaman WHERE id=%s", [pk])
            row = c.fetchone()
            if not row:
                raise Http404
            buku_id, status = row
            if status != "Dikembalikan":
                c.execute("UPDATE peminjaman SET status='Dikembalikan' WHERE id=%s", [pk])
                c.execute("UPDATE buku SET stok = stok + 1 WHERE id=%s", [buku_id])
        messages.success(request, "Buku berhasil dikembalikan.")
    return redirect("peminjaman_list")
