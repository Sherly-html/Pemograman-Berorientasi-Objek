# models/base_model.py
# ============================================================
# ABSTRACT BASE CLASS — Fondasi semua Model OOP
# ============================================================
# KONSEP OOP:
#   - Abstraction        : ABC & @abstractmethod
#   - Inheritance        : Semua model lain extends class ini
#   - Constructor        : __init__ dengan validasi
#   - Encapsulation      : Private & Protected attribute
#   - Exception Handling : try/except + ValueError
#   - Private Attribute  : __id (nama mulai __)
#   - Protected Attribute: _created_at (nama mulai _)
# ============================================================

from abc import ABC, abstractmethod
from datetime import datetime
import uuid


class BaseModel(ABC):
    """
    CLASS   : BaseModel
    TYPE    : Abstract Base Class (tidak bisa di-instansiasi langsung)
    FUNGSI  : Menjadi "template wajib" untuk semua model turunan.

    Setiap class yang extends BaseModel WAJIB mengimplementasi:
      - to_dict()   → konversi object ke dictionary
      - from_dict() → buat object dari dictionary
      - validate()  → validasi data sebelum disimpan
    """

    def __init__(self, id=None):
        """
        CONSTRUCTOR (__init__)
        ----------------------
        Dipanggil otomatis saat object dibuat.
        Menerima parameter 'id' opsional.
        Jika id tidak diberikan, dibuat otomatis (UUID).

        KONSEP:
        - __id      → PRIVATE attribute (hanya bisa diakses dalam class ini)
        - _created_at → PROTECTED attribute (bisa diakses class turunan)
        """

        # PRIVATE ATTRIBUTE: __id
        # Dua underscore (__) = private, tidak bisa diakses langsung dari luar
        # Contoh: obj.__id → ERROR!
        # Harus lewat getter: obj.id → OK
        self.__id = id if id else str(uuid.uuid4())[:8]

        # PROTECTED ATTRIBUTE: _created_at
        # Satu underscore (_) = protected
        # Bisa diakses class turunan, tapi "tidak disarankan" dari luar
        self._created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # ── PROPERTY (Getter) ─────────────────────────────────────
    # @property memungkinkan akses atribut private seperti atribut biasa
    # obj.id → memanggil method ini secara otomatis

    @property
    def id(self):
        """Getter untuk private attribute __id"""
        return self.__id

    @property
    def created_at(self):
        """Getter untuk protected attribute _created_at"""
        return self._created_at

    # ── SETTER ───────────────────────────────────────────────
    @id.setter
    def id(self, value):
        """
        SETTER untuk __id dengan validasi.

        KONSEP EXCEPTION HANDLING + ValueError:
        Jika value kosong atau bukan string → raise ValueError
        """
        # EXCEPTION HANDLING: try/except
        try:
            if not value or not isinstance(value, str):
                # ValueError: jenis exception untuk nilai tidak valid
                raise ValueError("ID harus berupa string dan tidak boleh kosong!")
            self.__id = value
        except ValueError as e:
            # Tangkap error dan print pesan yang jelas
            print(f"[ERROR] Setter ID gagal: {e}")
            raise  # Re-raise agar caller tahu ada error

    # ── ABSTRACT METHODS ─────────────────────────────────────
    # @abstractmethod = method yang WAJIB diimplementasi oleh class turunan
    # Jika tidak diimplementasi → Python otomatis error saat instansiasi

    @abstractmethod
    def to_dict(self):
        """
        ABSTRACT METHOD: to_dict()
        --------------------------
        Wajib diimplementasi di setiap class turunan.
        Fungsi: Mengubah object menjadi dictionary (untuk disimpan ke JSON).

        KONSEP POLYMORPHISM:
        Setiap class turunan mengimplementasi to_dict() dengan cara berbeda,
        tapi dipanggil dengan cara yang sama.
        """
        pass

    @classmethod
    @abstractmethod
    def from_dict(cls, data: dict):
        """
        ABSTRACT CLASS METHOD: from_dict()
        -----------------------------------
        Wajib diimplementasi di class turunan.
        Fungsi: Membuat object dari dictionary (saat membaca JSON).
        """
        pass

    @abstractmethod
    def validate(self):
        """
        ABSTRACT METHOD: validate()
        ----------------------------
        Wajib diimplementasi di class turunan.
        Fungsi: Validasi data sebelum disimpan.
        Harus raise ValueError jika data tidak valid.
        """
        pass

    # ── CONCRETE METHOD ──────────────────────────────────────
    # Method biasa (bukan abstract) — langsung bisa dipakai semua turunan

    def get_info(self):
        """
        CONCRETE METHOD: get_info()
        ----------------------------
        Bisa langsung dipakai semua class turunan tanpa override.
        Mengembalikan info dasar object.
        """
        return {
            "id": self.id,
            "created_at": self.created_at,
            "type": self.__class__.__name__  # Nama class saat ini (Dynamic Behavior)
        }

    def __repr__(self):
        """
        __repr__: Representasi string object (untuk debugging).
        Contoh output: <Artikel id=abc123>
        """
        return f"<{self.__class__.__name__} id={self.id}>"

    def __eq__(self, other):
        """
        __eq__: Perbandingan dua object berdasarkan ID.
        Contoh: artikel1 == artikel2 → True jika id sama
        """
        if not isinstance(other, BaseModel):
            return False
        return self.id == other.id