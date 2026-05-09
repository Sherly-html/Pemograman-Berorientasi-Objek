# models/artikel.py
# ============================================================
# CLASS ARTIKEL — Mewarisi BaseModel
# ============================================================
# KONSEP OOP:
#   - Inheritance        : class Artikel(BaseModel)
#   - Polymorphism       : Override to_dict(), from_dict(), validate()
#   - Constructor        : __init__ memanggil super().__init__()
#   - Encapsulation      : atribut dikumpulkan dalam class
#   - Exception Handling : validate() raise ValueError
#   - Public Attribute   : judul, konten, penulis, kategori
#   - Protected Attribute: _status (inherited style)
# ============================================================

from models.base_model import BaseModel
from datetime import datetime


class Artikel(BaseModel):
    """
    CLASS   : Artikel
    PARENT  : BaseModel (Inheritance)
    FUNGSI  : Merepresentasikan satu artikel islami.

    INHERITANCE:
    Artikel mewarisi semua atribut & method dari BaseModel:
      - id          (dari BaseModel)
      - created_at  (dari BaseModel)
      - get_info()  (dari BaseModel)
      - __repr__()  (dari BaseModel)
    """

    # ── CLASS ATTRIBUTE ───────────────────────────────────────
    # Milik class Artikel, bukan per-object
    # Dipakai untuk membatasi pilihan kategori
    KATEGORI_VALID = ["Fiqih", "Akidah", "Akhlak", "Kisah", "Umum"]

    def __init__(self, judul, konten, penulis, kategori="Umum",
                 status="draft", id=None, created_at=None):
        """
        CONSTRUCTOR Artikel
        -------------------
        super().__init__(id) → memanggil constructor BaseModel
        Ini adalah cara INHERITANCE bekerja di constructor.

        Parameter:
          judul    → PUBLIC  (bebas diakses)
          konten   → PUBLIC
          penulis  → PUBLIC
          kategori → PUBLIC
          _status  → PROTECTED (konvensi: pakai _ prefix)
          id       → diteruskan ke BaseModel
        """

        # Panggil constructor parent (BaseModel)
        # WAJIB dipanggil agar __id dan _created_at ter-inisialisasi
        super().__init__(id)

        # Jika created_at diberikan (saat load dari JSON), override nilai
        if created_at:
            self._created_at = created_at

        # ── PUBLIC ATTRIBUTE ──────────────────────────────────
        # Bisa diakses & diubah bebas dari luar class
        self.judul    = judul
        self.konten   = konten
        self.penulis  = penulis
        self.kategori = kategori

        # ── PROTECTED ATTRIBUTE ───────────────────────────────
        # Konvensi: satu underscore = "jangan diakses sembarangan"
        # Tapi masih bisa diakses jika perlu (tidak di-enforce Python)
        self._status = status   # "draft" atau "published"

    # ── PROPERTY untuk _status ────────────────────────────────
    @property
    def status(self):
        """Getter untuk protected attribute _status"""
        return self._status

    @status.setter
    def status(self, value):
        """
        Setter _status dengan validasi.
        EXCEPTION HANDLING: hanya terima "draft" atau "published"
        """
        if value not in ["draft", "published"]:
            raise ValueError(f"Status '{value}' tidak valid! Gunakan 'draft' atau 'published'.")
        self._status = value

    # ── POLYMORPHISM: Override Abstract Methods ───────────────
    # Tiga method berikut adalah IMPLEMENTASI dari abstract method BaseModel
    # Inilah yang disebut POLYMORPHISM — method sama, implementasi berbeda

    def to_dict(self):
        """
        POLYMORPHISM: Override to_dict() dari BaseModel
        ------------------------------------------------
        Mengubah object Artikel menjadi dictionary.
        Dipakai saat menyimpan data ke file JSON.
        """
        return {
            "id"        : self.id,
            "judul"     : self.judul,
            "konten"    : self.konten,
            "penulis"   : self.penulis,
            "kategori"  : self.kategori,
            "status"    : self._status,
            "created_at": self._created_at
        }

    @classmethod
    def from_dict(cls, data: dict):
        """
        POLYMORPHISM: Override from_dict() dari BaseModel
        --------------------------------------------------
        Membuat object Artikel dari dictionary.
        Dipakai saat membaca data dari file JSON.

        cls → merujuk ke class Artikel itu sendiri
        """
        return cls(
            id         = data.get("id"),
            judul      = data.get("judul", ""),
            konten     = data.get("konten", ""),
            penulis    = data.get("penulis", "Admin"),
            kategori   = data.get("kategori", "Umum"),
            status     = data.get("status", "draft"),
            created_at = data.get("created_at")
        )

    def validate(self):
        """
        POLYMORPHISM: Override validate() dari BaseModel
        -------------------------------------------------
        Memvalidasi data Artikel sebelum disimpan.

        EXCEPTION HANDLING + ValueError:
        Raise ValueError jika ada data yang tidak valid.
        """
        # Cek judul tidak kosong
        if not self.judul or not self.judul.strip():
            raise ValueError("Judul artikel tidak boleh kosong!")

        # Cek judul tidak terlalu pendek
        if len(self.judul.strip()) < 5:
            raise ValueError("Judul artikel minimal 5 karakter!")

        # Cek konten tidak kosong
        if not self.konten or not self.konten.strip():
            raise ValueError("Konten artikel tidak boleh kosong!")

        # Cek konten tidak terlalu pendek
        if len(self.konten.strip()) < 20:
            raise ValueError("Konten artikel minimal 20 karakter!")

        # Cek kategori valid
        if self.kategori not in self.KATEGORI_VALID:
            raise ValueError(
                f"Kategori '{self.kategori}' tidak valid! "
                f"Pilih dari: {', '.join(self.KATEGORI_VALID)}"
            )

        # Jika semua valid, return True
        return True

    # ── PUBLIC METHOD ─────────────────────────────────────────
    def publish(self):
        """
        METHOD: publish()
        -----------------
        Mengubah status artikel dari 'draft' ke 'published'.
        Contoh DYNAMIC BEHAVIOR — object bisa mengubah state-nya sendiri.
        """
        self._status = "published"
        return f"Artikel '{self.judul}' telah dipublish!"

    def unpublish(self):
        """Mengubah status artikel kembali ke 'draft'."""
        self._status = "draft"
        return f"Artikel '{self.judul}' dikembalikan ke draft."

    def get_preview(self, panjang=100):
        """
        METHOD: get_preview()
        ----------------------
        Mengembalikan potongan konten untuk preview.
        Contoh method dengan parameter default.
        """
        if len(self.konten) <= panjang:
            return self.konten
        return self.konten[:panjang] + "..."