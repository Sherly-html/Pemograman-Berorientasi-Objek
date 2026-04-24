# ============================================================
# exceptions/custom_error.py
# Custom Exception Classes untuk SmartShop
#
# OOP — Error Handling:
#   - Semua exception extends built-in Exception
#   - Encapsulation: atribut private + getter
#   - Hierarki exception yang jelas & terstruktur
#
# Hierarki:
#   Exception (built-in)
#   ├── SmartShopError          ← base semua error SmartShop
#   │   ├── ValidationError     ← input tidak valid
#   │   ├── AuthenticationError ← login / akses ditolak
#   │   ├── PaymentError        ← masalah pembayaran
#   │   └── ProductNotFoundError← produk tidak ditemukan
# ============================================================


# ============================================================
# BASE EXCEPTION — induk semua custom error SmartShop
# ============================================================
class SmartShopError(Exception):
    """
    Base exception untuk semua error di SmartShop.
    Semua custom exception wajib extends class ini.
    """
    def __init__(self, message: str):
        self.__message = message
        super().__init__(self.__message)

    @property
    def message(self) -> str:
        return self.__message

    def __str__(self) -> str:
        return f"[SmartShopError] {self.__message}"


# ============================================================
# VALIDATION ERROR
# Untuk input yang tidak memenuhi syarat
# ============================================================
class ValidationError(SmartShopError):
    """
    Dilempar saat data input dari user tidak valid.

    Contoh penggunaan:
        raise ValidationError("Username minimal 3 karakter.", "username")
        raise ValidationError("Harga tidak boleh negatif.", "price")

    Attributes:
        message (str) : pesan error yang ditampilkan ke user
        field   (str) : nama field yang bermasalah (opsional)
    """

    def __init__(self, message: str, field: str = None):
        super().__init__(message)
        self.__field = field

    @property
    def field(self) -> str:
        """Nama field yang menyebabkan error (bisa None)."""
        return self.__field

    def __str__(self) -> str:
        if self.__field:
            return f"[ValidationError] Field '{self.__field}': {self.message}"
        return f"[ValidationError] {self.message}"


# ============================================================
# AUTHENTICATION ERROR
# Untuk masalah login & akses
# ============================================================
class AuthenticationError(SmartShopError):
    """
    Dilempar saat autentikasi gagal.

    Contoh penggunaan:
        raise AuthenticationError("Username tidak ditemukan.")
        raise AuthenticationError("Password salah.")
        raise AuthenticationError("Sesi telah berakhir.")

    Attributes:
        message (str) : pesan error untuk ditampilkan ke user
    """

    def __init__(self, message: str = "Autentikasi gagal."):
        super().__init__(message)

    def __str__(self) -> str:
        return f"[AuthenticationError] {self.message}"


# ============================================================
# PAYMENT ERROR
# Untuk masalah proses pembayaran
# ============================================================
class PaymentError(SmartShopError):
    """
    Dilempar saat proses pembayaran bermasalah.

    Contoh penggunaan:
        raise PaymentError("Bukti pembayaran belum diupload.", "pay-001")
        raise PaymentError("Status pembayaran tidak valid.", None)

    Attributes:
        message    (str) : pesan error
        payment_id (str) : ID pembayaran yang bermasalah (opsional)
    """

    def __init__(self, message: str, payment_id: str = None):
        super().__init__(message)
        self.__payment_id = payment_id

    @property
    def payment_id(self) -> str:
        """ID pembayaran yang menyebabkan error (bisa None)."""
        return self.__payment_id

    def __str__(self) -> str:
        if self.__payment_id:
            return (f"[PaymentError] "
                    f"Payment '{self.__payment_id}': {self.message}")
        return f"[PaymentError] {self.message}"


# ============================================================
# PRODUCT NOT FOUND ERROR
# Untuk produk yang tidak ada di database
# ============================================================
class ProductNotFoundError(SmartShopError):
    """
    Dilempar saat produk tidak ditemukan di database.

    Contoh penggunaan:
        raise ProductNotFoundError("abc-123")
        raise ProductNotFoundError()  # tanpa ID

    Attributes:
        product_id (str) : ID produk yang dicari (opsional)
    """

    def __init__(self, product_id: str = None):
        self.__product_id = product_id
        if product_id:
            msg = f"Produk dengan ID '{product_id}' tidak ditemukan."
        else:
            msg = "Produk tidak ditemukan."
        super().__init__(msg)

    @property
    def product_id(self) -> str:
        """ID produk yang tidak ditemukan (bisa None)."""
        return self.__product_id

    def __str__(self) -> str:
        return f"[ProductNotFoundError] {self.message}"