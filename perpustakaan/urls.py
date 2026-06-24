from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),

    path("buku/", views.buku_list, name="buku_list"),
    path("buku/tambah/", views.buku_create, name="buku_create"),
    path("buku/<int:pk>/", views.buku_detail, name="buku_detail"),
    path("buku/<int:pk>/edit/", views.buku_edit, name="buku_edit"),
    path("buku/<int:pk>/hapus/", views.buku_delete, name="buku_delete"),

    path("user/", views.siswa_list, name="siswa_list"),
    path("user/tambah/", views.siswa_create, name="siswa_create"),
    path("user/<int:pk>/", views.siswa_detail, name="siswa_detail"),
    path("user/<int:pk>/edit/", views.siswa_edit, name="siswa_edit"),
    path("user/<int:pk>/hapus/", views.siswa_delete, name="siswa_delete"),

    path("peminjaman/", views.peminjaman_list, name="peminjaman_list"),
    path("peminjaman/tambah/", views.peminjaman_create, name="peminjaman_create"),
    path("peminjaman/<int:pk>/kembalikan/", views.peminjaman_return, name="peminjaman_return"),
]
