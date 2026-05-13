# routes/admin.py
# ============================================================
# ROUTE ADMIN — Halaman yang hanya bisa diakses admin
# ============================================================
# URL yang di-handle:
#   /admin/          → Dashboard
#   /admin/login     → Login
#   /admin/logout    → Logout
#   /admin/artikel   → Kelola Artikel
#   /admin/kajian    → Kelola Kajian
#   /admin/pengumuman→ Kelola Pengumuman
# ============================================================

from flask import (Blueprint, render_template, redirect,
                   url_for, request, flash, session)
from flask_login import login_user, logout_user, login_required, current_user
from config import Config
from models.masjid import masjid
from models.artikel import Artikel
from models.kajian import Kajian
from models.pengumuman import Pengumuman

# Import AdminUser dari app — tapi ini akan circular!
# Solusi: buat helper function load admin langsung di sini
from flask_login import UserMixin

admin_bp = Blueprint("admin", __name__)


# ── HELPER: Admin User Object ─────────────────────────────────
class _AdminUser(UserMixin):
    """Local admin user untuk keperluan login."""
    def __init__(self):
        self.id       = "1"
        self.username = Config.ADMIN_USERNAME


# ── LOGIN ─────────────────────────────────────────────────────
@admin_bp.route("/login", methods=["GET", "POST"])
def login():
    """
    Halaman login admin.
    GET  → tampilkan form login
    POST → proses login
    """
    # Jika sudah login, langsung ke dashboard
    if current_user.is_authenticated:
        return redirect(url_for("admin.dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        # Validasi credential
        if (username == Config.ADMIN_USERNAME and
                password == Config.ADMIN_PASSWORD):
            # Login berhasil
            user = _AdminUser()
            login_user(user, remember=True)
            flash("Selamat datang, Admin!", "success")

            # Redirect ke halaman yang dituju sebelum login
            next_page = request.args.get("next")
            return redirect(next_page or url_for("admin.dashboard"))
        else:
            flash("Username atau password salah!", "danger")

    return render_template("admin/login.html")


# ── LOGOUT ────────────────────────────────────────────────────
@admin_bp.route("/logout")
@login_required
def logout():
    """Logout admin dan redirect ke login."""
    logout_user()
    flash("Anda telah logout.", "info")
    return redirect(url_for("admin.login"))


# ── DASHBOARD ─────────────────────────────────────────────────
@admin_bp.route("/")
@login_required
def dashboard():
    """
    Dashboard admin — menampilkan statistik.
    @login_required → otomatis redirect ke login jika belum login.
    """
    statistik = masjid.get_statistik()
    artikel_terbaru  = masjid.get_artikel()[-5:][::-1]
    kajian_terbaru   = masjid.get_kajian()[-5:][::-1]

    return render_template(
        "admin/dashboard.html",
        statistik       = statistik,
        artikel_terbaru = artikel_terbaru,
        kajian_terbaru  = kajian_terbaru
    )


# ═══════════════════════════════════════════════════════════════
# CRUD ARTIKEL
# ═══════════════════════════════════════════════════════════════

@admin_bp.route("/artikel")
@login_required
def kelola_artikel():
    """Halaman daftar semua artikel untuk admin."""
    semua_artikel = masjid.get_artikel()[::-1]
    return render_template(
        "admin/artikel.html",
        artikel_list = semua_artikel
    )


@admin_bp.route("/artikel/tambah", methods=["GET", "POST"])
@login_required
def tambah_artikel():
    """Halaman form tambah artikel baru."""
    if request.method == "POST":
        try:
            artikel_baru = Artikel(
                judul    = request.form.get("judul", "").strip(),
                konten   = request.form.get("konten", "").strip(),
                penulis  = request.form.get("penulis", "Admin").strip(),
                kategori = request.form.get("kategori", "Umum"),
                status   = request.form.get("status", "draft")
            )
            sukses, pesan = masjid.tambah_artikel(artikel_baru)

            if sukses:
                flash(pesan, "success")
                return redirect(url_for("admin.kelola_artikel"))
            else:
                flash(pesan, "danger")

        except Exception as e:
            flash(f"Error: {str(e)}", "danger")

    return render_template(
        "admin/artikel_form.html",
        judul_halaman = "Tambah Artikel",
        artikel       = None,
        kategori_list = Artikel.KATEGORI_VALID
    )


@admin_bp.route("/artikel/edit/<id>", methods=["GET", "POST"])
@login_required
def edit_artikel(id):
    """Halaman form edit artikel."""
    artikel = masjid.get_artikel_by_id(id)
    if not artikel:
        flash("Artikel tidak ditemukan!", "danger")
        return redirect(url_for("admin.kelola_artikel"))

    if request.method == "POST":
        data_baru = {
            "judul"   : request.form.get("judul", "").strip(),
            "konten"  : request.form.get("konten", "").strip(),
            "penulis" : request.form.get("penulis", "Admin").strip(),
            "kategori": request.form.get("kategori", "Umum"),
            "status"  : request.form.get("status", "draft")
        }
        sukses, pesan = masjid.edit_artikel(id, data_baru)

        if sukses:
            flash(pesan, "success")
            return redirect(url_for("admin.kelola_artikel"))
        else:
            flash(pesan, "danger")

    return render_template(
        "admin/artikel_form.html",
        judul_halaman = "Edit Artikel",
        artikel       = artikel,
        kategori_list = Artikel.KATEGORI_VALID
    )


@admin_bp.route("/artikel/hapus/<id>", methods=["POST"])
@login_required
def hapus_artikel(id):
    """Hapus artikel berdasarkan ID."""
    sukses, pesan = masjid.hapus_artikel(id)
    flash(pesan, "success" if sukses else "danger")
    return redirect(url_for("admin.kelola_artikel"))


@admin_bp.route("/artikel/publish/<id>", methods=["POST"])
@login_required
def publish_artikel(id):
    """Toggle publish/draft artikel."""
    artikel = masjid.get_artikel_by_id(id)
    if artikel:
        if artikel.status == "draft":
            artikel.publish()
        else:
            artikel.unpublish()
        masjid._simpan_artikel()
        flash(f"Status artikel berhasil diubah!", "success")
    return redirect(url_for("admin.kelola_artikel"))


# ═══════════════════════════════════════════════════════════════
# CRUD KAJIAN
# ═══════════════════════════════════════════════════════════════

@admin_bp.route("/kajian")
@login_required
def kelola_kajian():
    """Halaman daftar semua kajian untuk admin."""
    semua_kajian = masjid.get_kajian()[::-1]
    return render_template(
        "admin/kajian.html",
        kajian_list = semua_kajian
    )


@admin_bp.route("/kajian/tambah", methods=["GET", "POST"])
@login_required
def tambah_kajian():
    """Halaman form tambah kajian baru."""
    if request.method == "POST":
        try:
            kajian_baru = Kajian(
                judul     = request.form.get("judul", "").strip(),
                pemateri  = request.form.get("pemateri", "").strip(),
                lokasi    = request.form.get("lokasi", "").strip(),
                hari      = request.form.get("hari", "Ahad"),
                waktu     = request.form.get("waktu", ""),
                deskripsi = request.form.get("deskripsi", "").strip(),
                kuota     = int(request.form.get("kuota", 100))
            )
            sukses, pesan = masjid.tambah_kajian(kajian_baru)

            if sukses:
                flash(pesan, "success")
                return redirect(url_for("admin.kelola_kajian"))
            else:
                flash(pesan, "danger")

        except Exception as e:
            flash(f"Error: {str(e)}", "danger")

    return render_template(
        "admin/kajian_form.html",
        judul_halaman = "Tambah Kajian",
        kajian        = None,
        hari_list     = Kajian.HARI_VALID
    )


@admin_bp.route("/kajian/edit/<id>", methods=["GET", "POST"])
@login_required
def edit_kajian(id):
    """Halaman form edit kajian."""
    kajian = masjid.get_kajian_by_id(id)
    if not kajian:
        flash("Kajian tidak ditemukan!", "danger")
        return redirect(url_for("admin.kelola_kajian"))

    if request.method == "POST":
        data_baru = {
            "judul"    : request.form.get("judul", "").strip(),
            "pemateri" : request.form.get("pemateri", "").strip(),
            "lokasi"   : request.form.get("lokasi", "").strip(),
            "hari"     : request.form.get("hari", "Ahad"),
            "waktu"    : request.form.get("waktu", ""),
            "deskripsi": request.form.get("deskripsi", "").strip(),
            "kuota"    : int(request.form.get("kuota", 100))
        }
        sukses, pesan = masjid.edit_kajian(id, data_baru)

        if sukses:
            flash(pesan, "success")
            return redirect(url_for("admin.kelola_kajian"))
        else:
            flash(pesan, "danger")

    return render_template(
        "admin/kajian_form.html",
        judul_halaman = "Edit Kajian",
        kajian        = kajian,
        hari_list     = Kajian.HARI_VALID
    )


@admin_bp.route("/kajian/hapus/<id>", methods=["POST"])
@login_required
def hapus_kajian(id):
    """Hapus kajian berdasarkan ID."""
    sukses, pesan = masjid.hapus_kajian(id)
    flash(pesan, "success" if sukses else "danger")
    return redirect(url_for("admin.kelola_kajian"))


# ═══════════════════════════════════════════════════════════════
# CRUD PENGUMUMAN
# ═══════════════════════════════════════════════════════════════

@admin_bp.route("/pengumuman")
@login_required
def kelola_pengumuman():
    """Halaman daftar semua pengumuman untuk admin."""
    semua_pengumuman = masjid.get_pengumuman()[::-1]
    return render_template(
        "admin/pengumuman.html",
        pengumuman_list = semua_pengumuman
    )


@admin_bp.route("/pengumuman/tambah", methods=["GET", "POST"])
@login_required
def tambah_pengumuman():
    """Halaman form tambah pengumuman baru."""
    if request.method == "POST":
        try:
            p_baru = Pengumuman(
                judul           = request.form.get("judul", "").strip(),
                isi             = request.form.get("isi", "").strip(),
                tipe            = request.form.get("tipe", "Umum"),
                tanggal_berlaku = request.form.get("tanggal_berlaku", ""),
                prioritas       = request.form.get("prioritas", "normal"),
                aktif           = request.form.get("aktif") == "true"
            )
            sukses, pesan = masjid.tambah_pengumuman(p_baru)

            if sukses:
                flash(pesan, "success")
                return redirect(url_for("admin.kelola_pengumuman"))
            else:
                flash(pesan, "danger")

        except Exception as e:
            flash(f"Error: {str(e)}", "danger")

    return render_template(
        "admin/pengumuman_form.html",
        judul_halaman  = "Tambah Pengumuman",
        pengumuman     = None,
        tipe_list      = Pengumuman.TIPE_VALID,
        prioritas_list = Pengumuman.PRIORITAS_VALID
    )


@admin_bp.route("/pengumuman/edit/<id>", methods=["GET", "POST"])
@login_required
def edit_pengumuman(id):
    """Halaman form edit pengumuman."""
    p = masjid.get_pengumuman_by_id(id)
    if not p:
        flash("Pengumuman tidak ditemukan!", "danger")
        return redirect(url_for("admin.kelola_pengumuman"))

    if request.method == "POST":
        data_baru = {
            "judul"          : request.form.get("judul", "").strip(),
            "isi"            : request.form.get("isi", "").strip(),
            "tipe"           : request.form.get("tipe", "Umum"),
            "tanggal_berlaku": request.form.get("tanggal_berlaku", ""),
            "prioritas"      : request.form.get("prioritas", "normal"),
            "aktif"          : request.form.get("aktif") == "true"
        }
        sukses, pesan = masjid.edit_pengumuman(id, data_baru)

        if sukses:
            flash(pesan, "success")
            return redirect(url_for("admin.kelola_pengumuman"))
        else:
            flash(pesan, "danger")

    return render_template(
        "admin/pengumuman_form.html",
        judul_halaman  = "Edit Pengumuman",
        pengumuman     = p,
        tipe_list      = Pengumuman.TIPE_VALID,
        prioritas_list = Pengumuman.PRIORITAS_VALID
    )


@admin_bp.route("/pengumuman/hapus/<id>", methods=["POST"])
@login_required
def hapus_pengumuman(id):
    """Hapus pengumuman berdasarkan ID."""
    sukses, pesan = masjid.hapus_pengumuman(id)
    flash(pesan, "success" if sukses else "danger")
    return redirect(url_for("admin.kelola_pengumuman"))