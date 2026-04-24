# ============================================================
# models/user.py
# OOP Concepts:
#   - Abstract Class : User
#   - Inheritance    : Customer, Admin extends User
#   - Encapsulation  : atribut private (__nama)
#   - Getter & Setter: via @property
# ============================================================

from abc import ABC, abstractmethod
from exceptions.custom_error import ValidationError


class User(ABC):
    """
    Abstract Class: User
    Tidak bisa diinstansiasi langsung.
    Semua role (Admin & Customer) wajib extends class ini.
    """

    def __init__(self, user_id: str, username: str, password: str,
                 full_name: str, phone: str, role: str):

        # ---- Atribut Private (Encapsulation) ----
        self.__user_id   = user_id
        self.__username  = username
        self.__password  = password
        self.__full_name = full_name
        self.__phone     = phone
        self.__role      = role

    # ==================================================
    # GETTER (baca atribut private dari luar class)
    # ==================================================

    @property
    def user_id(self) -> str:
        return self.__user_id

    @property
    def username(self) -> str:
        return self.__username

    @property
    def full_name(self) -> str:
        return self.__full_name

    @property
    def phone(self) -> str:
        return self.__phone

    @property
    def role(self) -> str:
        return self.__role

    @property
    def password(self) -> str:
        return self.__password

    # ==================================================
    # SETTER (ubah atribut private dengan validasi)
    # ==================================================

    @full_name.setter
    def full_name(self, value: str):
        if not value or len(value.strip()) < 2:
            raise ValidationError("Nama lengkap minimal 2 karakter.", "full_name")
        self.__full_name = value.strip()

    @phone.setter
    def phone(self, value: str):
        cleaned = value.strip().replace("-", "").replace(" ", "")
        if not cleaned.isdigit():
            raise ValidationError("Nomor telepon hanya boleh angka.", "phone")
        if len(cleaned) < 10 or len(cleaned) > 15:
            raise ValidationError("Nomor telepon tidak valid (10-15 digit).", "phone")
        self.__phone = cleaned

    @password.setter
    def password(self, hashed_value: str):
        """Setter password — menerima hash, bukan plain text."""
        self.__password = hashed_value

    # ==================================================
    # ABSTRACT METHOD (wajib diimplementasi subclass)
    # ==================================================

    @abstractmethod
    def get_dashboard_url(self) -> str:
        """
        Setiap role punya halaman dashboard berbeda.
        - Customer → /home
        - Admin    → /admin/dashboard
        """
        pass

    @abstractmethod
    def get_info(self) -> dict:
        """
        Mengembalikan informasi user dalam bentuk dict.
        Tiap subclass bisa punya field berbeda.
        """
        pass

    # ==================================================
    # METHOD UMUM (bisa dipakai semua subclass)
    # ==================================================

    def to_dict(self) -> dict:
        """Konversi objek User ke dict untuk disimpan ke JSON."""
        return {
            "user_id"   : self.__user_id,
            "username"  : self.__username,
            "password"  : self.__password,
            "full_name" : self.__full_name,
            "phone"     : self.__phone,
            "role"      : self.__role,
        }

    def __str__(self) -> str:
        return f"[{self.__role.upper()}] {self.__full_name} (@{self.__username})"


# ============================================================
# INHERITANCE: Customer extends User
# ============================================================
class Customer(User):
    """
    Customer adalah user biasa yang bisa:
    - Melihat produk
    - Menambah ke keranjang
    - Checkout & membayar
    - Melihat status pesanan

    Menambahkan atribut: address (alamat pengiriman)
    """

    def __init__(self, user_id: str, username: str, password: str,
                 full_name: str, phone: str, address: str):

        # Panggil constructor parent (User)
        super().__init__(user_id, username, password,
                         full_name, phone, role="customer")

        # Atribut tambahan khusus Customer
        self.__address = address

    # ---- Getter & Setter address ----

    @property
    def address(self) -> str:
        return self.__address

    @address.setter
    def address(self, value: str):
        if not value or len(value.strip()) < 5:
            raise ValidationError("Alamat minimal 5 karakter.", "address")
        self.__address = value.strip()

    # ---- Implementasi Abstract Method ----

    def get_dashboard_url(self) -> str:
        """Customer diarahkan ke halaman produk."""
        return "/home"

    def get_info(self) -> dict:
        """Info lengkap Customer termasuk alamat."""
        return {
            "user_id"   : self.user_id,
            "username"  : self.username,
            "full_name" : self.full_name,
            "phone"     : self.phone,
            "address"   : self.__address,
            "role"      : self.role,
        }

    # ---- Override to_dict ----

    def to_dict(self) -> dict:
        """Tambahkan field address ke dict parent."""
        data = super().to_dict()
        data["address"] = self.__address
        return data

    # ---- Static Factory Method ----

    @staticmethod
    def from_dict(data: dict) -> "Customer":
        """Buat objek Customer dari dictionary (data JSON)."""
        return Customer(
            user_id   = data["user_id"],
            username  = data["username"],
            password  = data["password"],
            full_name = data["full_name"],
            phone     = data["phone"],
            address   = data.get("address", "-"),
        )


# ============================================================
# INHERITANCE: Admin extends User
# ============================================================
class Admin(User):
    """
    Admin adalah user dengan hak akses penuh:
    - CRUD Produk
    - Verifikasi pembayaran
    - Melihat semua transaksi

    Admin dikenali otomatis dari username 'admin'.
    Tidak perlu halaman registrasi khusus admin.
    """

    def __init__(self, user_id: str, username: str, password: str,
                 full_name: str, phone: str):

        # Panggil constructor parent dengan role="admin"
        super().__init__(user_id, username, password,
                         full_name, phone, role="admin")

    # ---- Implementasi Abstract Method ----

    def get_dashboard_url(self) -> str:
        """Admin diarahkan ke halaman dashboard admin."""
        return "/admin/dashboard"

    def get_info(self) -> dict:
        """Info Admin (tanpa alamat)."""
        return {
            "user_id"   : self.user_id,
            "username"  : self.username,
            "full_name" : self.full_name,
            "phone"     : self.phone,
            "role"      : self.role,
        }

    # ---- Static Factory Method ----

    @staticmethod
    def from_dict(data: dict) -> "Admin":
        """Buat objek Admin dari dictionary (data JSON)."""
        return Admin(
            user_id   = data["user_id"],
            username  = data["username"],
            password  = data["password"],
            full_name = data["full_name"],
            phone     = data["phone"],
        )