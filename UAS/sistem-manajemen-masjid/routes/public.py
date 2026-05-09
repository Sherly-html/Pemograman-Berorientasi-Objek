# routes/public.py
# ============================================================
# ROUTE PUBLIC — Halaman yang bisa diakses semua orang
# ============================================================
# URL yang di-handle:
#   /                → Home
#   /kajian          → Jadwal Kajian
#   /artikel         → Daftar Artikel
#   /artikel/<id>    → Detail Artikel
#   /pengumuman      → Pengumuman
#   /donasi          → Donasi Masjid
# ============================================================

from flask import Blueprint, render_template, abort
from models.masjid import masjid

# Buat Blueprint object
# "public" = nama blueprint (dipakai untuk url_for)
public_bp = Blueprint("public", __name__)


# ── HOME ──────────────────────────────────────────────────────
@public_bp.route("/")
def home():
    """
    Halaman utama website.
    Menampilkan artikel terbaru & pengumuman aktif.
    """
    # Ambil 3 artikel published terbaru untuk ditampilkan di home
    semua_artikel = masjid.get_artikel(hanya_published=True)
    artikel_terbaru = semua_artikel[-3:][::-1]  # 3 terakhir, urutan terbalik

    # Ambil pengumuman aktif
    pengumuman_aktif = masjid.get_pengumuman(hanya_aktif=True)[-3:][::-1]

    # Ambil 3 kajian terbaru
    kajian_terbaru = masjid.get_kajian()[-3:][::-1]

    return render_template(
        "public/home.html",
        artikel_terbaru   = artikel_terbaru,
        pengumuman_aktif  = pengumuman_aktif,
        kajian_terbaru    = kajian_terbaru
    )


# ── KAJIAN ────────────────────────────────────────────────────
@public_bp.route("/kajian")
def kajian():
    """Halaman daftar semua jadwal kajian."""
    semua_kajian = masjid.get_kajian()[::-1]  # Terbaru di atas
    return render_template(
        "public/kajian.html",
        kajian_list = semua_kajian
    )


# ── ARTIKEL ───────────────────────────────────────────────────
@public_bp.route("/artikel")
def artikel():
    """Halaman daftar semua artikel published."""
    semua_artikel = masjid.get_artikel(hanya_published=True)[::-1]
    return render_template(
        "public/artikel.html",
        artikel_list = semua_artikel
    )


@public_bp.route("/artikel/<id>")
def artikel_detail(id):
    """
    Halaman detail satu artikel.
    Jika artikel tidak ditemukan → 404.
    """
    artikel = masjid.get_artikel_by_id(id)

    # EXCEPTION HANDLING: artikel tidak ada → abort 404
    if not artikel or artikel.status != "published":
        abort(404)

    return render_template(
        "public/artikel_detail.html",
        artikel = artikel
    )


# ── PENGUMUMAN ────────────────────────────────────────────────
@public_bp.route("/pengumuman")
def pengumuman():
    """Halaman daftar semua pengumuman aktif."""
    semua_pengumuman = masjid.get_pengumuman(hanya_aktif=True)[::-1]
    return render_template(
        "public/pengumuman.html",
        pengumuman_list = semua_pengumuman
    )


# ── DONASI ────────────────────────────────────────────────────
@public_bp.route("/donasi")
def donasi():
    """Halaman informasi donasi masjid."""
    return render_template("public/donasi.html")


# ── ERROR HANDLERS ────────────────────────────────────────────
@public_bp.app_errorhandler(404)
def page_not_found(e):
    """Halaman 404 custom."""
    return render_template("public/404.html"), 404