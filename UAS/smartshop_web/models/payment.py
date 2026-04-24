# ============================================================
# models/payment.py
# OOP: Polymorphism pada metode pembayaran
#
# Hierarki class:
#   Payment (Abstract)
#   ├── EWallet      → GoPay, OVO, DANA, ShopeePay
#   └── BankTransfer → BCA, Mandiri, BRI, BNI
#
# Relasi: Transaction → Payment
# ============================================================

from abc import ABC, abstractmethod
from exceptions.custom_error import PaymentError, ValidationError


class Payment(ABC):
    """
    Abstract Class: Payment
    -------------------------
    Dasar untuk semua metode pembayaran.

    Polymorphism diterapkan pada method:
    - process()         → tiap subclass punya instruksi berbeda
    - get_method_name() → tiap subclass punya nama berbeda
    - get_icon()        → tiap subclass punya ikon berbeda
    """

    # ---- Konstanta status pembayaran ----
    STATUS_PENDING  = "pending"
    STATUS_VERIFIED = "verified"
    STATUS_REJECTED = "rejected"

    VALID_STATUSES = [STATUS_PENDING, STATUS_VERIFIED, STATUS_REJECTED]

    def __init__(self, payment_id: str, amount: float,
                 proof_image: str = None):

        # ---- Atribut Private (Encapsulation) ----
        self.__payment_id  = payment_id
        self.__amount      = amount
        self.__proof_image = proof_image
        self.__status      = self.STATUS_PENDING

    # ==================================================
    # GETTER
    # ==================================================

    @property
    def payment_id(self) -> str:
        return self.__payment_id

    @property
    def amount(self) -> float:
        return self.__amount

    @property
    def proof_image(self) -> str:
        return self.__proof_image

    @property
    def status(self) -> str:
        return self.__status

    # ==================================================
    # SETTER
    # ==================================================

    @proof_image.setter
    def proof_image(self, filename: str):
        if not filename or not filename.strip():
            raise ValidationError(
                "Nama file bukti pembayaran tidak valid.", "proof_image"
            )
        self.__proof_image = filename.strip()

    @status.setter
    def status(self, value: str):
        if value not in self.VALID_STATUSES:
            raise PaymentError(
                f"Status tidak valid. Pilihan: {self.VALID_STATUSES}",
                self.__payment_id,
            )
        self.__status = value

    # ==================================================
    # ABSTRACT METHOD — inti dari POLYMORPHISM
    # ==================================================

    @abstractmethod
    def process(self) -> dict:
        """
        POLYMORPHISM:
        Tiap metode bayar punya instruksi berbeda.
        - EWallet      → instruksi transfer via e-wallet
        - BankTransfer → instruksi transfer via bank
        Mengembalikan dict berisi instruksi pembayaran.
        """
        pass

    @abstractmethod
    def get_method_name(self) -> str:
        """
        POLYMORPHISM:
        Nama tampilan metode pembayaran.
        - EWallet      → 'E-Wallet (GoPay)'
        - BankTransfer → 'Bank Transfer (BCA)'
        """
        pass

    @abstractmethod
    def get_icon(self) -> str:
        """
        POLYMORPHISM:
        Ikon emoji untuk metode pembayaran.
        """
        pass

    # ==================================================
    # METHOD UMUM (dipakai semua subclass)
    # ==================================================

    def format_amount(self) -> str:
        """Format nominal ke Rupiah."""
        return "Rp {:,.0f}".format(self.__amount).replace(",", ".")

    def verify(self):
        """
        Admin memverifikasi pembayaran.
        Bukti harus sudah diupload sebelum bisa diverifikasi.
        """
        if not self.__proof_image:
            raise PaymentError(
                "Bukti pembayaran belum diupload.", self.__payment_id
            )
        self.__status = self.STATUS_VERIFIED

    def reject(self):
        """Admin menolak pembayaran."""
        self.__status = self.STATUS_REJECTED

    def is_verified(self) -> bool:
        return self.__status == self.STATUS_VERIFIED

    def is_rejected(self) -> bool:
        return self.__status == self.STATUS_REJECTED

    def to_dict(self) -> dict:
        """Konversi ke dict. Subclass override untuk tambahkan field."""
        return {
            "payment_id"  : self.__payment_id,
            "amount"      : self.__amount,
            "proof_image" : self.__proof_image,
            "status"      : self.__status,
            "method"      : self.get_method_name(),
        }

    def __str__(self) -> str:
        return (f"[{self.get_icon()} {self.get_method_name()}] "
                f"{self.format_amount()} — {self.__status}")


# ============================================================
# POLYMORPHISM: EWallet extends Payment
# ============================================================
class EWallet(Payment):
    """
    Pembayaran via E-Wallet (GoPay, OVO, DANA, ShopeePay).
    Implements process() dengan instruksi spesifik e-wallet.
    """

    # Nomor e-wallet SmartShop
    WALLET_NUMBERS = {
        "GoPay"     : "0812-3456-7890",
        "OVO"       : "0812-3456-7890",
        "DANA"      : "0812-3456-7890",
        "ShopeePay" : "0812-3456-7890",
    }

    def __init__(self, payment_id: str, amount: float,
                 wallet_name: str = "GoPay", proof_image: str = None):
        super().__init__(payment_id, amount, proof_image)
        self.__wallet_name = wallet_name

    @property
    def wallet_name(self) -> str:
        return self.__wallet_name

    # ---- Implementasi Abstract Method (Polymorphism) ----

    def process(self) -> dict:
        """POLYMORPHISM — instruksi pembayaran via e-wallet."""
        nomor = self.WALLET_NUMBERS.get(self.__wallet_name, "0812-3456-7890")
        return {
            "method"       : "E-Wallet",
            "wallet"       : self.__wallet_name,
            "nomor"        : nomor,
            "nominal"      : self.format_amount(),
            "instructions" : [
                f"Buka aplikasi {self.__wallet_name} di HP kamu",
                "Pilih menu 'Transfer' atau 'Kirim Uang'",
                f"Masukkan nomor: {nomor}",
                "Nama penerima: SmartShop Official",
                f"Masukkan nominal: {self.format_amount()}",
                "Tambahkan catatan: 'Pembayaran SmartShop'",
                "Konfirmasi dan selesaikan transfer",
                "Screenshot bukti transfer, lalu upload di bawah",
            ],
        }

    def get_method_name(self) -> str:
        """POLYMORPHISM — nama metode EWallet."""
        return f"E-Wallet ({self.__wallet_name})"

    def get_icon(self) -> str:
        """POLYMORPHISM — ikon EWallet."""
        icons = {
            "GoPay"     : "💚",
            "OVO"       : "💜",
            "DANA"      : "💙",
            "ShopeePay" : "🧡",
        }
        return icons.get(self.__wallet_name, "📱")

    def to_dict(self) -> dict:
        d = super().to_dict()
        d["wallet_name"] = self.__wallet_name
        return d

    @staticmethod
    def from_dict(data: dict) -> "EWallet":
        p = EWallet(
            payment_id  = data["payment_id"],
            amount      = data["amount"],
            wallet_name = data.get("wallet_name", "GoPay"),
            proof_image = data.get("proof_image"),
        )
        if data.get("status"):
            p.status = data["status"]
        return p


# ============================================================
# POLYMORPHISM: BankTransfer extends Payment
# ============================================================
class BankTransfer(Payment):
    """
    Pembayaran via Transfer Bank (BCA, Mandiri, BRI, BNI).
    Implements process() dengan instruksi spesifik bank.
    """

    # Nomor rekening SmartShop per bank
    BANK_ACCOUNTS = {
        "BCA"     : {"no_rek": "1234-5678-90",   "atas_nama": "SmartShop Indonesia"},
        "Mandiri" : {"no_rek": "9876-5432-10",   "atas_nama": "SmartShop Indonesia"},
        "BRI"     : {"no_rek": "1111-2222-3333", "atas_nama": "SmartShop Indonesia"},
        "BNI"     : {"no_rek": "4444-5555-6666", "atas_nama": "SmartShop Indonesia"},
    }

    def __init__(self, payment_id: str, amount: float,
                 bank_name: str = "BCA", proof_image: str = None):
        super().__init__(payment_id, amount, proof_image)
        self.__bank_name = bank_name

    @property
    def bank_name(self) -> str:
        return self.__bank_name

    # ---- Implementasi Abstract Method (Polymorphism) ----

    def process(self) -> dict:
        """POLYMORPHISM — instruksi pembayaran via bank transfer."""
        info   = self.BANK_ACCOUNTS.get(
            self.__bank_name,
            {"no_rek": "0000-0000-00", "atas_nama": "SmartShop Indonesia"}
        )
        no_rek = info["no_rek"]
        an     = info["atas_nama"]
        return {
            "method"       : "Bank Transfer",
            "bank"         : self.__bank_name,
            "no_rekening"  : no_rek,
            "atas_nama"    : an,
            "nominal"      : self.format_amount(),
            "instructions" : [
                f"Buka aplikasi mobile banking atau ATM {self.__bank_name}",
                "Pilih menu 'Transfer Antar Bank' atau 'Transfer'",
                f"Masukkan no. rekening: {no_rek}",
                f"Atas nama: {an}",
                f"Masukkan nominal: {self.format_amount()}",
                "Pastikan nominal TEPAT agar mudah diverifikasi",
                "Selesaikan transaksi dan simpan bukti transfer",
                "Upload foto/screenshot bukti transfer di bawah",
            ],
        }

    def get_method_name(self) -> str:
        """POLYMORPHISM — nama metode BankTransfer."""
        return f"Bank Transfer ({self.__bank_name})"

    def get_icon(self) -> str:
        """POLYMORPHISM — ikon BankTransfer."""
        icons = {
            "BCA"     : "🔵",
            "Mandiri" : "🟡",
            "BRI"     : "🔵",
            "BNI"     : "🟠",
        }
        return icons.get(self.__bank_name, "🏦")

    def to_dict(self) -> dict:
        d = super().to_dict()
        d["bank_name"] = self.__bank_name
        return d

    @staticmethod
    def from_dict(data: dict) -> "BankTransfer":
        p = BankTransfer(
            payment_id  = data["payment_id"],
            amount      = data["amount"],
            bank_name   = data.get("bank_name", "BCA"),
            proof_image = data.get("proof_image"),
        )
        if data.get("status"):
            p.status = data["status"]
        return p


# ============================================================
# FACTORY FUNCTION
# ============================================================
def payment_from_dict(data: dict) -> Payment:
    """
    Factory function — buat objek Payment yang tepat dari dict
    berdasarkan field 'method'. Dipakai saat baca dari JSON.
    """
    method = data.get("method", "")
    if "E-Wallet" in method:
        return EWallet.from_dict(data)
    return BankTransfer.from_dict(data)