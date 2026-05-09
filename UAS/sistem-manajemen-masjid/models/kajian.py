# models/kajian.py
# ============================================================
# CLASS KAJIAN — Mewarisi BaseModel
# ============================================================
# KONSEP OOP:
#   - Inheritance        : class Kajian(BaseModel)
#   - Polymorphism       : Override to_dict(), from_dict(), validate()
#   - Constructor        : __init__ dengan super().__init__()
#   - Encapsulation      : semua atribut terkumpul dalam class
#   - Exception Handling : validate() raise ValueError
#   - Public Attribute   : judul, pemateri, lokasi, tanggal, waktu
#   - Protected Attribute: _kuota
# ============================================================

from models.base_model import BaseModel


class Kajian(BaseModel):
    """
    CLASS   : Kajian
    PARENT  : BaseModel (Inheritance)
    FUNGSI  : Merepresentasikan satu jadwal kajian masjid.

    POLYMORPHISM:
    Kajian dan Artikel sama-sama punya to_dict(), from_dict(), validate()
    Tapi isinya BERBEDA sesuai kebutuhan masing-masing class.
    Inilah POLYMORPHISM — satu interface, banyak bentuk.
    """

    # ── CLASS ATTRIBUTE ───────────────────────────────────────
    HARI_VALID = ["Senin", "Selasa", "Rabu", "Kamis",
                  "Jumat", "Sabtu", "Ahad"]

    def __init__(self, judul, pemateri, lokasi, hari,
                 waktu, deskripsi="", kuota=100,
                 id=None, created_at=None):
        """
        CONSTRUCTOR Kajian
        ------------------
        Memanggil super().__init__(id) untuk inisialisasi BaseModel.

        Parameter:
          judul     → PUBLIC
          pemateri  → PUBLIC
          lokasi    → PUBLIC
          hari      → PUBLIC
          waktu     → PUBLIC
          deskripsi → PUBLIC
          _kuota    → PROTECTED (dibatasi aksesnya lewat property)
        """

        # Panggil constructor parent
        super().__init__(id)

        if created_at:
            self._created_at = created_at

        # ── PUBLIC ATTRIBUTE ──────────────────────────────────
        self.judul     = judul
        self.pemateri  = pemateri
        self.lokasi    = lokasi
        self.hari      = hari
        self.waktu     = waktu
        self.deskripsi = deskripsi

        # ── PROTECTED ATTRIBUTE ───────────────────────────────
        # _kuota: kapasitas peserta kajian
        # Protected karena perlu validasi saat diubah
        self._kuota = kuota

    # ── PROPERTY untuk _kuota ─────────────────────────────────
    @property
    def kuota(self):
        """Getter untuk protected attribute _kuota"""
        return self._kuota

    @kuota.setter
    def kuota(self, value):
        """
        Setter _kuota dengan validasi.
        EXCEPTION HANDLING: kuota harus angka positif
        """
        try:
            value = int(value)
            if value <= 0:
                raise ValueError("Kuota harus berupa angka positif!")
            self._kuota = value
        except (TypeError, ValueError):
            raise ValueError("Kuota harus berupa angka positif!")

    # ── POLYMORPHISM: Override Abstract Methods ───────────────

    def to_dict(self):
        """
        POLYMORPHISM: Override to_dict() dari BaseModel
        ------------------------------------------------
        Versi Kajian — field berbeda dari Artikel.
        Ini membuktikan Polymorphism: method sama, isi berbeda.
        """
        return {
            "id"        : self.id,
            "judul"     : self.judul,
            "pemateri"  : self.pemateri,
            "lokasi"    : self.lokasi,
            "hari"      : self.hari,
            "waktu"     : self.waktu,
            "deskripsi" : self.deskripsi,
            "kuota"     : self._kuota,
            "created_at": self._created_at
        }

    @classmethod
    def from_dict(cls, data: dict):
        """
        POLYMORPHISM: Override from_dict() dari BaseModel
        --------------------------------------------------
        Membuat object Kajian dari dictionary (saat baca JSON).
        """
        return cls(
            id         = data.get("id"),
            judul      = data.get("judul", ""),
            pemateri   = data.get("pemateri", ""),
            lokasi     = data.get("lokasi", "Masjid"),
            hari       = data.get("hari", "Ahad"),
            waktu      = data.get("waktu", "08:00"),
            deskripsi  = data.get("deskripsi", ""),
            kuota      = data.get("kuota", 100),
            created_at = data.get("created_at")
        )

    def validate(self):
        """
        POLYMORPHISM: Override validate() dari BaseModel
        -------------------------------------------------
        Validasi data Kajian.

        EXCEPTION HANDLING + ValueError:
        Raise ValueError jika data tidak valid.
        """
        if not self.judul or not self.judul.strip():
            raise ValueError("Judul kajian tidak boleh kosong!")

        if len(self.judul.strip()) < 5:
            raise ValueError("Judul kajian minimal 5 karakter!")

        if not self.pemateri or not self.pemateri.strip():
            raise ValueError("Nama pemateri tidak boleh kosong!")

        if not self.lokasi or not self.lokasi.strip():
            raise ValueError("Lokasi kajian tidak boleh kosong!")

        if self.hari not in self.HARI_VALID:
            raise ValueError(
                f"Hari '{self.hari}' tidak valid! "
                f"Pilih dari: {', '.join(self.HARI_VALID)}"
            )

        if not self.waktu:
            raise ValueError("Waktu kajian tidak boleh kosong!")

        if self._kuota <= 0:
            raise ValueError("Kuota peserta harus lebih dari 0!")

        return True

    # ── PUBLIC METHOD ─────────────────────────────────────────
    def get_jadwal_lengkap(self):
        """
        METHOD: get_jadwal_lengkap()
        -----------------------------
        Mengembalikan string jadwal lengkap kajian.
        Contoh: "Ahad, 08:00 WIB — Masjid Al-Ikhlas"
        """
        return f"{self.hari}, {self.waktu} WIB — {self.lokasi}"

    def tambah_kuota(self, jumlah):
        """
        METHOD: tambah_kuota()
        -----------------------
        DYNAMIC BEHAVIOR: object bisa mengubah state-nya sendiri.
        Menambah kuota peserta kajian.
        """
        try:
            jumlah = int(jumlah)
            if jumlah <= 0:
                raise ValueError("Jumlah tambahan harus positif!")
            self._kuota += jumlah
            return f"Kuota berhasil ditambah! Total: {self._kuota} orang"
        except ValueError as e:
            raise ValueError(f"Gagal menambah kuota: {e}")