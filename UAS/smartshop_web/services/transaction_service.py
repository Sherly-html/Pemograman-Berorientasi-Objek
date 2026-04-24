# ============================================================
# services/transaction_service.py
# Layanan Transaksi & Pembayaran SmartShop
#
# Fungsi:
#   - create_transaction()       : buat transaksi baru dari checkout
#   - get_transactions_by_user() : ambil transaksi milik 1 user
#   - get_transaction_by_id()    : ambil 1 transaksi by ID
#   - get_all_transactions()     : ambil semua transaksi (Admin)
#   - upload_payment_proof()     : user upload bukti bayar
#   - verify_payment()           : admin approve/reject pembayaran
# ============================================================

import uuid

from models.transaction import Transaction
from models.payment import EWallet, BankTransfer
from services.db import read_db, write_db
from exceptions.custom_error import ValidationError, PaymentError


def create_transaction(user_id: str, username: str, items: list,
                       total: float, address: str,
                       payment_method: str) -> Transaction:
    """
    Buat transaksi baru saat user melakukan checkout.

    Args:
        user_id        : ID user yang checkout
        username       : username user
        items          : list item dari keranjang (snapshot)
        total          : total harga
        address        : alamat pengiriman
        payment_method : metode pembayaran yang dipilih

    Returns:
        Transaction: objek transaksi yang baru dibuat

    Raises:
        ValidationError: jika keranjang kosong / data tidak valid
    """
    # ---- Validasi ----
    if not items or len(items) == 0:
        raise ValidationError("Keranjang belanja kosong.", "items")

    try:
        total = float(total)
    except (TypeError, ValueError):
        raise ValidationError("Total harga tidak valid.", "total")

    if total <= 0:
        raise ValidationError("Total harga harus lebih dari 0.", "total")

    if not address or len(address.strip()) < 5:
        raise ValidationError("Alamat pengiriman minimal 5 karakter.", "address")

    if not payment_method or not payment_method.strip():
        raise ValidationError("Pilih metode pembayaran.", "payment_method")

    # ---- Buat objek Transaction (OOP) ----
    transaction = Transaction(
        transaction_id = str(uuid.uuid4()),
        user_id        = user_id,
        username       = username,
        items          = items,
        total          = total,
        address        = address.strip(),
        payment_method = payment_method.strip(),
    )

    # ---- Simpan ke database ----
    db = read_db()
    db["transactions"].append(transaction.to_dict())
    write_db(db)

    return transaction


def get_transactions_by_user(user_id: str) -> list:
    """
    Ambil semua transaksi milik user tertentu,
    diurutkan dari yang terbaru.

    Args:
        user_id : ID user

    Returns:
        list[Transaction]: daftar transaksi user (terbaru di atas)
    """
    db     = read_db()
    result = []

    for t in db.get("transactions", []):
        if t["user_id"] == user_id:
            result.append(Transaction.from_dict(t))

    # Urutkan terbaru di atas (by created_at descending)
    result.sort(key=lambda x: x.created_at, reverse=True)
    return result


def get_transaction_by_id(transaction_id: str) -> Transaction:
    """
    Ambil satu transaksi berdasarkan transaction_id.

    Args:
        transaction_id : ID unik transaksi

    Returns:
        Transaction | None: objek transaksi, atau None jika tidak ditemukan
    """
    db = read_db()
    for t in db.get("transactions", []):
        if t["transaction_id"] == transaction_id:
            return Transaction.from_dict(t)
    return None


def get_all_transactions() -> list:
    """
    Ambil semua transaksi dari semua user (Admin only),
    diurutkan dari yang terbaru.

    Returns:
        list[Transaction]: semua transaksi (terbaru di atas)
    """
    db     = read_db()
    result = [Transaction.from_dict(t) for t in db.get("transactions", [])]
    result.sort(key=lambda x: x.created_at, reverse=True)
    return result


def upload_payment_proof(transaction_id: str, user_id: str,
                         filename: str) -> bool:
    """
    User mengupload bukti pembayaran.
    Status transaksi berubah dari 'pending'/'ditolak' → 'paid'.

    Args:
        transaction_id : ID transaksi
        user_id        : ID user (untuk validasi kepemilikan)
        filename       : nama file bukti yang diupload

    Returns:
        bool: True jika berhasil

    Raises:
        ValidationError : jika transaksi tidak ditemukan
        PaymentError    : jika status tidak bisa diupload lagi
    """
    if not filename or not filename.strip():
        raise ValidationError("Nama file tidak valid.", "filename")

    db = read_db()

    for i, t in enumerate(db["transactions"]):
        if t["transaction_id"] == transaction_id and t["user_id"] == user_id:

            # Cek apakah status masih boleh upload
            if t["status"] not in [Transaction.STATUS_PENDING,
                                    Transaction.STATUS_REJECTED]:
                raise PaymentError(
                    "Transaksi ini sudah diproses dan tidak bisa diupload ulang.",
                    transaction_id
                )

            # Update transaksi
            db["transactions"][i]["payment_proof"] = filename.strip()
            db["transactions"][i]["status"]        = Transaction.STATUS_PAID

            # Buat record payment berdasarkan metode yang dipilih
            method = t.get("payment_method", "")
            pid    = str(uuid.uuid4())

            if "E-Wallet" in method:
                wallet_name = method.replace("E-Wallet (", "").replace(")", "")
                payment     = EWallet(pid, t["total"], wallet_name, filename)
            else:
                bank_name = method.replace("Bank Transfer (", "").replace(")", "")
                payment   = BankTransfer(pid, t["total"], bank_name, filename)

            db["transactions"][i]["payment_id"] = pid
            write_db(db)
            return True

    raise ValidationError("Transaksi tidak ditemukan.", "transaction_id")


def verify_payment(transaction_id: str, action: str,
                   note: str = "") -> Transaction:
    """
    Admin memverifikasi atau menolak pembayaran.

    Args:
        transaction_id : ID transaksi yang diverifikasi
        action         : 'approve' → status jadi 'dikirim'
                         'reject'  → status jadi 'ditolak'
        note           : catatan dari admin (opsional)

    Returns:
        Transaction: objek transaksi setelah diupdate

    Raises:
        ValidationError : jika action tidak valid / transaksi tidak ada
        PaymentError    : jika transaksi belum ada bukti pembayaran
    """
    # Validasi action
    if action not in ["approve", "reject"]:
        raise ValidationError(
            "Action tidak valid. Gunakan 'approve' atau 'reject'.", "action"
        )

    db = read_db()

    for i, t in enumerate(db["transactions"]):
        if t["transaction_id"] == transaction_id:

            # Harus sudah ada bukti bayar sebelum bisa diverifikasi
            if not t.get("payment_proof"):
                raise PaymentError(
                    "Belum ada bukti pembayaran yang diupload.",
                    transaction_id
                )

            # Terapkan action
            if action == "approve":
                db["transactions"][i]["status"] = Transaction.STATUS_SHIPPING
            else:
                db["transactions"][i]["status"] = Transaction.STATUS_REJECTED

            # Simpan catatan admin
            db["transactions"][i]["note"] = note.strip() if note else ""

            write_db(db)
            return Transaction.from_dict(db["transactions"][i])

    raise ValidationError("Transaksi tidak ditemukan.", "transaction_id")


# Import Transaction untuk konstanta STATUS
from models.transaction import Transaction