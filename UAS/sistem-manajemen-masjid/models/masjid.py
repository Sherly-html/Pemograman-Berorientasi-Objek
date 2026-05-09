# models/masjid.py
# ============================================================
# CLASS MASJID — Object Relationship & Data Manager
# ============================================================
# KONSEP OOP:
#   - Object Relationship : Masjid "has-a" Artikel, Kajian, Pengumuman
#   - Dynamic Behavior    : state berubah saat data ditambah/hapus
#   - Exception Handling  : try/except saat baca/tulis JSON
#   - Encapsulation       : semua operasi data dikumpulkan di sini
#   - Class Attribute     : _instance (Singleton pattern)
# ============================================================

import json
import os
from config import Config
from models.artikel import Artikel
from models.kajian import Kajian
from models.pengumuman import Pengumuman


class Masjid:
    """
    CLASS   : Masjid
    FUNGSI  : Pusat manajemen data masjid.

    OBJECT RELATIONSHIP (Has-A):
    Masjid MEMILIKI kumpulan:
      - artikel[]     → list of Artikel objects
      - kajian[]      → list of Kajian objects
      - pengumuman[]  → list of Pengumuman objects

    Ini berbeda dari Inheritance (Is-A).
    Masjid bukan turunan Artikel — tapi Masjid PUNYA Artikel.
    Hubungan ini disebut: AGGREGATION / COMPOSITION
    """

    def __init__(self, nama, alamat, kota,
                 telepon="", email="", deskripsi=""):
        """
        CONSTRUCTOR Masjid
        ------------------
        Menginisialisasi data masjid + list kosong untuk relasi.

        OBJECT RELATIONSHIP:
        self._artikel, self._kajian, self._pengumuman
        → list yang akan menampung object-object terkait
        """

        # ── PUBLIC ATTRIBUTE ──────────────────────────────────
        self.nama      = nama
        self.alamat    = alamat
        self.kota      = kota
        self.telepon   = telepon
        self.email     = email
        self.deskripsi = deskripsi

        # ── OBJECT RELATIONSHIP ───────────────────────────────
        # Masjid "memiliki" kumpulan object lain
        # Ini adalah contoh nyata Object Relationship (Aggregation)
        self._artikel     = []   # list of Artikel objects
        self._kajian      = []   # list of Kajian objects
        self._pengumuman  = []   # list of Pengumuman objects

    # ═══════════════════════════════════════════════════════════
    # MANAJEMEN ARTIKEL
    # ═══════════════════════════════════════════════════════════

    def get_artikel(self, hanya_published=False):
        """
        Mengambil semua artikel.
        DYNAMIC BEHAVIOR: hasil berubah sesuai parameter.
        """
        if hanya_published:
            return [a for a in self._artikel if a.status == "published"]
        return self._artikel

    def get_artikel_by_id(self, id):
        """Mencari artikel berdasarkan ID."""
        for artikel in self._artikel:
            if artikel.id == id:
                return artikel
        return None

    def tambah_artikel(self, artikel: Artikel):
        """
        Menambah artikel ke dalam masjid.
        OBJECT RELATIONSHIP: Masjid menyimpan object Artikel.

        EXCEPTION HANDLING: validasi sebelum disimpan.
        """
        try:
            artikel.validate()
            self._artikel.append(artikel)
            self._simpan_artikel()
            return True, "Artikel berhasil ditambahkan!"
        except ValueError as e:
            return False, str(e)

    def edit_artikel(self, id, data_baru: dict):
        """
        Mengedit artikel berdasarkan ID.
        DYNAMIC BEHAVIOR: object berubah state setelah di-edit.
        """
        artikel = self.get_artikel_by_id(id)
        if not artikel:
            return False, "Artikel tidak ditemukan!"
        try:
            # Update atribut artikel
            artikel.judul    = data_baru.get("judul", artikel.judul)
            artikel.konten   = data_baru.get("konten", artikel.konten)
            artikel.penulis  = data_baru.get("penulis", artikel.penulis)
            artikel.kategori = data_baru.get("kategori", artikel.kategori)
            artikel._status  = data_baru.get("status", artikel.status)

            artikel.validate()
            self._simpan_artikel()
            return True, "Artikel berhasil diupdate!"
        except ValueError as e:
            return False, str(e)

    def hapus_artikel(self, id):
        """Menghapus artikel berdasarkan ID."""
        artikel = self.get_artikel_by_id(id)
        if not artikel:
            return False, "Artikel tidak ditemukan!"
        self._artikel.remove(artikel)
        self._simpan_artikel()
        return True, "Artikel berhasil dihapus!"

    # ═══════════════════════════════════════════════════════════
    # MANAJEMEN KAJIAN
    # ═══════════════════════════════════════════════════════════

    def get_kajian(self):
        """Mengambil semua kajian."""
        return self._kajian

    def get_kajian_by_id(self, id):
        """Mencari kajian berdasarkan ID."""
        for kajian in self._kajian:
            if kajian.id == id:
                return kajian
        return None

    def tambah_kajian(self, kajian: Kajian):
        """Menambah kajian baru."""
        try:
            kajian.validate()
            self._kajian.append(kajian)
            self._simpan_kajian()
            return True, "Kajian berhasil ditambahkan!"
        except ValueError as e:
            return False, str(e)

    def edit_kajian(self, id, data_baru: dict):
        """Mengedit kajian berdasarkan ID."""
        kajian = self.get_kajian_by_id(id)
        if not kajian:
            return False, "Kajian tidak ditemukan!"
        try:
            kajian.judul     = data_baru.get("judul", kajian.judul)
            kajian.pemateri  = data_baru.get("pemateri", kajian.pemateri)
            kajian.lokasi    = data_baru.get("lokasi", kajian.lokasi)
            kajian.hari      = data_baru.get("hari", kajian.hari)
            kajian.waktu     = data_baru.get("waktu", kajian.waktu)
            kajian.deskripsi = data_baru.get("deskripsi", kajian.deskripsi)
            kajian._kuota    = int(data_baru.get("kuota", kajian.kuota))

            kajian.validate()
            self._simpan_kajian()
            return True, "Kajian berhasil diupdate!"
        except ValueError as e:
            return False, str(e)

    def hapus_kajian(self, id):
        """Menghapus kajian berdasarkan ID."""
        kajian = self.get_kajian_by_id(id)
        if not kajian:
            return False, "Kajian tidak ditemukan!"
        self._kajian.remove(kajian)
        self._simpan_kajian()
        return True, "Kajian berhasil dihapus!"

    # ═══════════════════════════════════════════════════════════
    # MANAJEMEN PENGUMUMAN
    # ═══════════════════════════════════════════════════════════

    def get_pengumuman(self, hanya_aktif=False):
        """Mengambil semua pengumuman."""
        if hanya_aktif:
            return [p for p in self._pengumuman if p.aktif]
        return self._pengumuman

    def get_pengumuman_by_id(self, id):
        """Mencari pengumuman berdasarkan ID."""
        for p in self._pengumuman:
            if p.id == id:
                return p
        return None

    def tambah_pengumuman(self, pengumuman: Pengumuman):
        """Menambah pengumuman baru."""
        try:
            pengumuman.validate()
            self._pengumuman.append(pengumuman)
            self._simpan_pengumuman()
            return True, "Pengumuman berhasil ditambahkan!"
        except ValueError as e:
            return False, str(e)

    def edit_pengumuman(self, id, data_baru: dict):
        """Mengedit pengumuman berdasarkan ID."""
        p = self.get_pengumuman_by_id(id)
        if not p:
            return False, "Pengumuman tidak ditemukan!"
        try:
            p.judul           = data_baru.get("judul", p.judul)
            p.isi             = data_baru.get("isi", p.isi)
            p.tipe            = data_baru.get("tipe", p.tipe)
            p.tanggal_berlaku = data_baru.get("tanggal_berlaku", p.tanggal_berlaku)
            p.prioritas       = data_baru.get("prioritas", p.prioritas)
            p._aktif          = data_baru.get("aktif", p.aktif)

            p.validate()
            self._simpan_pengumuman()
            return True, "Pengumuman berhasil diupdate!"
        except ValueError as e:
            return False, str(e)

    def hapus_pengumuman(self, id):
        """Menghapus pengumuman berdasarkan ID."""
        p = self.get_pengumuman_by_id(id)
        if not p:
            return False, "Pengumuman tidak ditemukan!"
        self._pengumuman.remove(p)
        self._simpan_pengumuman()
        return True, "Pengumuman berhasil dihapus!"

    # ═══════════════════════════════════════════════════════════
    # LOAD & SIMPAN DATA JSON
    # ═══════════════════════════════════════════════════════════

    def _simpan_artikel(self):
        """Menyimpan semua artikel ke file JSON."""
        self._tulis_json(
            Config.ARTIKEL_FILE,
            [a.to_dict() for a in self._artikel]
        )

    def _simpan_kajian(self):
        """Menyimpan semua kajian ke file JSON."""
        self._tulis_json(
            Config.KAJIAN_FILE,
            [k.to_dict() for k in self._kajian]
        )

    def _simpan_pengumuman(self):
        """Menyimpan semua pengumuman ke file JSON."""
        self._tulis_json(
            Config.PENGUMUMAN_FILE,
            [p.to_dict() for p in self._pengumuman]
        )

    def _tulis_json(self, filepath, data):
        """
        Helper: menulis data ke file JSON.
        EXCEPTION HANDLING: tangkap error saat tulis file.
        """
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            raise Exception(f"Gagal menyimpan data: {e}")

    def _baca_json(self, filepath):
        """
        Helper: membaca data dari file JSON.
        EXCEPTION HANDLING: return list kosong jika file tidak ada.
        """
        try:
            if not os.path.exists(filepath):
                return []
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    def muat_semua_data(self):
        """
        Memuat semua data dari file JSON ke dalam object list.
        OBJECT RELATIONSHIP: JSON → dict → Object (Artikel/Kajian/Pengumuman)

        Dipanggil sekali saat aplikasi pertama start.
        """
        # Load artikel
        self._artikel = [
            Artikel.from_dict(d)
            for d in self._baca_json(Config.ARTIKEL_FILE)
        ]
        # Load kajian
        self._kajian = [
            Kajian.from_dict(d)
            for d in self._baca_json(Config.KAJIAN_FILE)
        ]
        # Load pengumuman
        self._pengumuman = [
            Pengumuman.from_dict(d)
            for d in self._baca_json(Config.PENGUMUMAN_FILE)
        ]
        return self

    def get_statistik(self):
        """
        DYNAMIC BEHAVIOR: statistik berubah sesuai data terkini.
        Mengembalikan ringkasan data masjid.
        """
        return {
            "total_artikel"      : len(self._artikel),
            "artikel_published"  : len([a for a in self._artikel
                                        if a.status == "published"]),
            "total_kajian"       : len(self._kajian),
            "total_pengumuman"   : len(self._pengumuman),
            "pengumuman_aktif"   : len([p for p in self._pengumuman
                                        if p.aktif]),
        }

    def to_dict(self):
        """Mengubah info dasar masjid ke dictionary."""
        return {
            "nama"      : self.nama,
            "alamat"    : self.alamat,
            "kota"      : self.kota,
            "telepon"   : self.telepon,
            "email"     : self.email,
            "deskripsi" : self.deskripsi
        }

    def __repr__(self):
        return f"<Masjid '{self.nama}' — {self.kota}>"


# ── SINGLETON INSTANCE ────────────────────────────────────────
# Satu object Masjid dipakai di seluruh aplikasi
# Dibuat sekali di sini, diimpor di mana-mana
masjid = Masjid(
    nama      = "Masjid Al-Ikhlas",
    alamat    = "Jl. Contoh No. 1",
    kota      = "Depok",
    telepon   = "021-1234567",
    email     = "masjid@example.com",
    deskripsi = "Masjid yang makmur dan modern."
)