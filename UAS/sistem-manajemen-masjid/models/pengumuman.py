# models/pengumuman.py
# ============================================================
# CLASS PENGUMUMAN — Mewarisi BaseModel
# ============================================================
# KONSEP OOP:
#   - Inheritance        : class Pengumuman(BaseModel)
#   - Polymorphism       : Override to_dict(), from_dict(), validate()
#   - Constructor        : __init__ dengan super().__init__()
#   - Private Attribute  : __prioritas (dua underscore)
#   - Protected Attribute: _aktif
#   - Exception Handling : validate() + setter raise ValueError
# ============================================================

from models.base_model import BaseModel


class Pengumuman(BaseModel):
    """
    CLASS   : Pengumuman
    PARENT  : BaseModel (Inheritance)
    FUNGSI  : Merepresentasikan satu pengumuman masjid.

    Perbedaan dengan Artikel & Kajian:
    - Punya PRIVATE attribute __prioritas (bukan hanya protected)
    - Lebih simpel, fokus pada judul, isi, dan tanggal berlaku
    """

    # ── CLASS ATTRIBUTE ───────────────────────────────────────
    PRIORITAS_VALID = ["rendah", "normal", "tinggi"]
    TIPE_VALID      = ["Umum", "Kegiatan", "Keuangan", "Darurat"]

    def __init__(self, judul, isi, tipe="Umum",
                 tanggal_berlaku="", prioritas="normal",
                 aktif=True, id=None, created_at=None):
        """
        CONSTRUCTOR Pengumuman
        ----------------------
        Parameter:
          judul           → PUBLIC
          isi             → PUBLIC
          tipe            → PUBLIC
          tanggal_berlaku → PUBLIC
          __prioritas     → PRIVATE  (dua underscore)
          _aktif          → PROTECTED (satu underscore)
        """

        super().__init__(id)

        if created_at:
            self._created_at = created_at

        # ── PUBLIC ATTRIBUTE ──────────────────────────────────
        self.judul           = judul
        self.isi             = isi
        self.tipe            = tipe
        self.tanggal_berlaku = tanggal_berlaku

        # ── PRIVATE ATTRIBUTE: __prioritas ───────────────────
        # DUA underscore = PRIVATE
        # Tidak bisa diakses dari luar class sama sekali!
        # obj.__prioritas  → ERROR (AttributeError)
        # Harus lewat property: obj.prioritas → OK
        self.__prioritas = prioritas

        # ── PROTECTED ATTRIBUTE: _aktif ───────────────────────
        # Satu underscore = PROTECTED
        self._aktif = aktif

    # ── PROPERTY untuk __prioritas (PRIVATE) ─────────────────
    @property
    def prioritas(self):
        """
        Getter untuk PRIVATE attribute __prioritas.
        Satu-satunya cara mengakses __prioritas dari luar class.
        """
        return self.__prioritas

    @prioritas.setter
    def prioritas(self, value):
        """
        Setter dengan validasi untuk __prioritas.
        EXCEPTION HANDLING: hanya terima nilai dari PRIORITAS_VALID
        """
        if value not in self.PRIORITAS_VALID:
            raise ValueError(
                f"Prioritas '{value}' tidak valid! "
                f"Pilih: {', '.join(self.PRIORITAS_VALID)}"
            )
        self.__prioritas = value

    # ── PROPERTY untuk _aktif (PROTECTED) ────────────────────
    @property
    def aktif(self):
        """Getter untuk protected attribute _aktif"""
        return self._aktif

    @aktif.setter
    def aktif(self, value):
        """Setter _aktif — hanya terima boolean"""
        if not isinstance(value, bool):
            raise ValueError("Nilai aktif harus True atau False!")
        self._aktif = value

    # ── POLYMORPHISM: Override Abstract Methods ───────────────

    def to_dict(self):
        """
        POLYMORPHISM: Override to_dict() dari BaseModel
        ------------------------------------------------
        Versi Pengumuman — berbeda dari Artikel & Kajian.
        """
        return {
            "id"             : self.id,
            "judul"          : self.judul,
            "isi"            : self.isi,
            "tipe"           : self.tipe,
            "tanggal_berlaku": self.tanggal_berlaku,
            "prioritas"      : self.__prioritas,
            "aktif"          : self._aktif,
            "created_at"     : self._created_at
        }

    @classmethod
    def from_dict(cls, data: dict):
        """
        POLYMORPHISM: Override from_dict() dari BaseModel
        --------------------------------------------------
        Membuat object Pengumuman dari dictionary.
        """
        return cls(
            id              = data.get("id"),
            judul           = data.get("judul", ""),
            isi             = data.get("isi", ""),
            tipe            = data.get("tipe", "Umum"),
            tanggal_berlaku = data.get("tanggal_berlaku", ""),
            prioritas       = data.get("prioritas", "normal"),
            aktif           = data.get("aktif", True),
            created_at      = data.get("created_at")
        )

    def validate(self):
        """
        POLYMORPHISM: Override validate() dari BaseModel
        -------------------------------------------------
        Validasi data Pengumuman.
        """
        if not self.judul or not self.judul.strip():
            raise ValueError("Judul pengumuman tidak boleh kosong!")

        if len(self.judul.strip()) < 5:
            raise ValueError("Judul pengumuman minimal 5 karakter!")

        if not self.isi or not self.isi.strip():
            raise ValueError("Isi pengumuman tidak boleh kosong!")

        if len(self.isi.strip()) < 10:
            raise ValueError("Isi pengumuman minimal 10 karakter!")

        if self.tipe not in self.TIPE_VALID:
            raise ValueError(
                f"Tipe '{self.tipe}' tidak valid! "
                f"Pilih: {', '.join(self.TIPE_VALID)}"
            )

        if self.__prioritas not in self.PRIORITAS_VALID:
            raise ValueError("Prioritas tidak valid!")

        return True

    # ── PUBLIC METHOD ─────────────────────────────────────────
    def aktifkan(self):
        """
        DYNAMIC BEHAVIOR: Mengaktifkan pengumuman.
        Object mengubah state-nya sendiri.
        """
        self._aktif = True
        return f"Pengumuman '{self.judul}' telah diaktifkan!"

    def nonaktifkan(self):
        """DYNAMIC BEHAVIOR: Menonaktifkan pengumuman."""
        self._aktif = False
        return f"Pengumuman '{self.judul}' telah dinonaktifkan!"

    def get_badge(self):
        """
        METHOD: get_badge()
        --------------------
        Mengembalikan label badge berdasarkan prioritas.
        Contoh DYNAMIC BEHAVIOR berbasis state object.
        """
        badge = {
            "rendah": "secondary",
            "normal": "primary",
            "tinggi": "danger"
        }
        return badge.get(self.__prioritas, "primary")