# ============================================================
# models/transaction.py
# Model Transaksi SmartShop
# OOP: Encapsulation (atribut private + getter/setter)
# Relasi: User → Cart → Transaction → Payment
# ============================================================

from datetime import datetime
from exceptions.custom_error import ValidationError


class Transaction:
    """
    Menyimpan data satu transaksi pembelian.

    Alur status:
    pending → paid → verified → dikirim → selesai
                  ↘ ditolak (jika pembayaran tidak valid)

    Relasi: User → Cart → Transaction → Payment
    """

    # ---- Konstanta status ----
    STATUS_PENDING  = "pending"    # baru checkout, belum bayar
    STATUS_PAID     = "paid"       # sudah upload bukti
    STATUS_VERIFIED = "verified"   # admin verifikasi (internal)
    STATUS_SHIPPING = "dikirim"    # barang sedang dikirim
    STATUS_DONE     = "selesai"    # transaksi selesai
    STATUS_REJECTED = "ditolak"    # pembayaran ditolak admin

    VALID_STATUSES = [
        STATUS_PENDING, STATUS_PAID, STATUS_VERIFIED,
        STATUS_SHIPPING, STATUS_DONE, STATUS_REJECTED,
    ]

    def __init__(self, transaction_id: str, user_id: str, username: str,
                 items: list, total: float, address: str,
                 payment_method: str = None, created_at: str = None):

        # ---- Atribut Private (Encapsulation) ----
        self.__transaction_id = transaction_id
        self.__user_id        = user_id
        self.__username       = username
        self.__items          = items        # list of dict (snapshot cart)
        self.__total          = total
        self.__address        = address
        self.__payment_method = payment_method
        self.__status         = self.STATUS_PENDING
        self.__payment_proof  = None         # filename bukti pembayaran
        self.__payment_id     = None
        self.__note           = ""           # catatan dari admin
        self.__created_at     = created_at or datetime.now().strftime("%d-%m-%Y %H:%M")

    # ==================================================
    # GETTER
    # ==================================================

    @property
    def transaction_id(self) -> str:
        return self.__transaction_id

    @property
    def user_id(self) -> str:
        return self.__user_id

    @property
    def username(self) -> str:
        return self.__username

    @property
    def items(self) -> list:
        return self.__items

    @property
    def total(self) -> float:
        return self.__total

    @property
    def address(self) -> str:
        return self.__address

    @property
    def payment_method(self) -> str:
        return self.__payment_method

    @property
    def status(self) -> str:
        return self.__status

    @property
    def payment_proof(self) -> str:
        return self.__payment_proof

    @property
    def payment_id(self) -> str:
        return self.__payment_id

    @property
    def note(self) -> str:
        return self.__note

    @property
    def created_at(self) -> str:
        return self.__created_at

    # ==================================================
    # SETTER (dengan validasi)
    # ==================================================

    @payment_method.setter
    def payment_method(self, value: str):
        if not value or not value.strip():
            raise ValidationError("Metode pembayaran tidak boleh kosong.", "payment_method")
        self.__payment_method = value.strip()

    @status.setter
    def status(self, value: str):
        if value not in self.VALID_STATUSES:
            raise ValidationError(
                f"Status tidak valid. Pilihan: {self.VALID_STATUSES}", "status"
            )
        self.__status = value

    @payment_proof.setter
    def payment_proof(self, filename: str):
        self.__payment_proof = filename

    @payment_id.setter
    def payment_id(self, value: str):
        self.__payment_id = value

    @note.setter
    def note(self, value: str):
        self.__note = value.strip() if value else ""

    # ==================================================
    # METHOD — Label & Warna Status
    # ==================================================

    def get_status_label(self) -> str:
        """
        Label status dalam Bahasa Indonesia
        untuk ditampilkan di UI.
        """
        labels = {
            self.STATUS_PENDING  : "Menunggu Pembayaran",
            self.STATUS_PAID     : "Bukti Dikirim",
            self.STATUS_VERIFIED : "Pembayaran Terverifikasi",
            self.STATUS_SHIPPING : "Barang Sedang Dikirim",
            self.STATUS_DONE     : "Selesai",
            self.STATUS_REJECTED : "Pembayaran Ditolak",
        }
        return labels.get(self.__status, self.__status)

    def get_status_badge(self) -> str:
        """
        Nama CSS class badge untuk warna status
        (disesuaikan dengan style.css).
        """
        badges = {
            self.STATUS_PENDING  : "badge-warning",
            self.STATUS_PAID     : "badge-info",
            self.STATUS_VERIFIED : "badge-success",
            self.STATUS_SHIPPING : "badge-primary",
            self.STATUS_DONE     : "badge-success",
            self.STATUS_REJECTED : "badge-danger",
        }
        return badges.get(self.__status, "badge-secondary")

    def get_status_icon(self) -> str:
        """Ikon emoji untuk masing-masing status."""
        icons = {
            self.STATUS_PENDING  : "⏳",
            self.STATUS_PAID     : "💳",
            self.STATUS_VERIFIED : "✅",
            self.STATUS_SHIPPING : "🚚",
            self.STATUS_DONE     : "🎉",
            self.STATUS_REJECTED : "❌",
        }
        return icons.get(self.__status, "📦")

    def format_total(self) -> str:
        """Format total ke Rupiah."""
        return "Rp {:,.0f}".format(self.__total).replace(",", ".")

    def can_upload_proof(self) -> bool:
        """Cek apakah user masih bisa upload bukti pembayaran."""
        return self.__status in [self.STATUS_PENDING, self.STATUS_REJECTED]

    def needs_verification(self) -> bool:
        """Cek apakah transaksi ini perlu diverifikasi admin."""
        return self.__status == self.STATUS_PAID

    # ==================================================
    # SERIALISASI
    # ==================================================

    def to_dict(self) -> dict:
        """Konversi objek Transaction ke dict untuk disimpan ke JSON."""
        return {
            "transaction_id" : self.__transaction_id,
            "user_id"        : self.__user_id,
            "username"       : self.__username,
            "items"          : self.__items,
            "total"          : self.__total,
            "address"        : self.__address,
            "payment_method" : self.__payment_method,
            "status"         : self.__status,
            "payment_proof"  : self.__payment_proof,
            "payment_id"     : self.__payment_id,
            "note"           : self.__note,
            "created_at"     : self.__created_at,
        }

    @staticmethod
    def from_dict(data: dict) -> "Transaction":
        """Buat objek Transaction dari dictionary (data JSON)."""
        t = Transaction(
            transaction_id = data["transaction_id"],
            user_id        = data["user_id"],
            username       = data.get("username", ""),
            items          = data.get("items", []),
            total          = data["total"],
            address        = data["address"],
            payment_method = data.get("payment_method"),
            created_at     = data.get("created_at"),
        )
        # Restore state via setter (melewati validasi)
        t.status        = data.get("status", Transaction.STATUS_PENDING)
        t.payment_proof = data.get("payment_proof")
        t.payment_id    = data.get("payment_id")
        t.note          = data.get("note", "")
        return t

    def __str__(self) -> str:
        return (f"[Transaksi {self.__transaction_id[:8]}...] "
                f"User: {self.__username} | "
                f"Total: {self.format_total()} | "
                f"Status: {self.get_status_label()}")