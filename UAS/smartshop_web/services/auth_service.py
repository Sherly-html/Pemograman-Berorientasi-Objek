# ============================================================
# services/auth_service.py
# Layanan Autentikasi SmartShop
#
# Fungsi:
#   - register_customer() : daftar akun baru
#   - login_user()        : login & validasi kredensial
#   - get_user_by_id()    : ambil data user dari DB
#   - seed_admin()        : buat akun admin default
# ============================================================

import uuid
from werkzeug.security import generate_password_hash, check_password_hash

from models.user import Customer, Admin
from services.db import read_db, write_db
from exceptions.custom_error import ValidationError, AuthenticationError


def register_customer(full_name: str, phone: str, address: str,
                      username: str, password: str) -> Customer:
    """
    Daftarkan customer baru ke database.

    Args:
        full_name : nama lengkap
        phone     : nomor telepon (hanya angka)
        address   : alamat lengkap
        username  : username unik (minimal 3 karakter)
        password  : password (minimal 6 karakter)

    Returns:
        Customer: objek customer yang baru dibuat

    Raises:
        ValidationError: jika ada input yang tidak valid
                         atau username sudah dipakai
    """
    # ---- Validasi semua field ----
    if not full_name or len(full_name.strip()) < 2:
        raise ValidationError("Nama lengkap minimal 2 karakter.", "full_name")

    phone_clean = phone.strip().replace("-", "").replace(" ", "") if phone else ""
    if not phone_clean.isdigit():
        raise ValidationError("Nomor telepon hanya boleh berisi angka.", "phone")
    if len(phone_clean) < 10 or len(phone_clean) > 15:
        raise ValidationError("Nomor telepon tidak valid (10–15 digit).", "phone")

    if not address or len(address.strip()) < 5:
        raise ValidationError("Alamat minimal 5 karakter.", "address")

    if not username or len(username.strip()) < 3:
        raise ValidationError("Username minimal 3 karakter.", "username")

    # Username tidak boleh mengandung spasi
    if " " in username.strip():
        raise ValidationError("Username tidak boleh mengandung spasi.", "username")

    # Username 'admin' direservasi
    if username.strip().lower() == "admin":
        raise ValidationError("Username 'admin' tidak tersedia.", "username")

    if not password or len(password) < 6:
        raise ValidationError("Password minimal 6 karakter.", "password")

    # ---- Cek username sudah digunakan ----
    db = read_db()
    for u in db["users"]:
        if u["username"].lower() == username.strip().lower():
            raise ValidationError(
                f"Username '{username}' sudah digunakan. Pilih yang lain.", "username"
            )

    # ---- Buat objek Customer (OOP) ----
    customer = Customer(
        user_id   = str(uuid.uuid4()),
        username  = username.strip(),
        password  = generate_password_hash(password),   # hash password
        full_name = full_name.strip(),
        phone     = phone_clean,
        address   = address.strip(),
    )

    # ---- Simpan ke database ----
    db["users"].append(customer.to_dict())
    write_db(db)

    return customer


def login_user(username: str, password: str) -> dict:
    """
    Validasi kredensial login dan kembalikan info user.

    Args:
        username : username yang diinput
        password : password plain text untuk diverifikasi

    Returns:
        dict: info user (user_id, username, full_name, role, address)

    Raises:
        AuthenticationError: jika username tidak ditemukan
                             atau password salah
    """
    # ---- Validasi input tidak kosong ----
    if not username or not username.strip():
        raise AuthenticationError("Username tidak boleh kosong.")
    if not password:
        raise AuthenticationError("Password tidak boleh kosong.")

    db = read_db()

    # ---- Cari user di database ----
    for u in db["users"]:
        if u["username"].lower() == username.strip().lower():

            # ---- Verifikasi password (check hash) ----
            if not check_password_hash(u["password"], password):
                raise AuthenticationError("Password salah. Coba lagi.")

            # ---- Login berhasil → kembalikan info user ----
            return {
                "user_id"   : u["user_id"],
                "username"  : u["username"],
                "full_name" : u["full_name"],
                "role"      : u["role"],
                "address"   : u.get("address", ""),
            }

    # Username tidak ditemukan
    raise AuthenticationError(
        f"Username '{username}' tidak ditemukan. Silakan daftar terlebih dahulu."
    )


def get_user_by_id(user_id: str) -> dict:
    """
    Ambil data user berdasarkan user_id.

    Args:
        user_id : ID unik user

    Returns:
        dict | None: data user, atau None jika tidak ditemukan
    """
    db = read_db()
    for u in db["users"]:
        if u["user_id"] == user_id:
            return u
    return None


def get_all_customers() -> list:
    """
    Ambil semua user dengan role 'customer'.

    Returns:
        list[dict]: daftar semua customer
    """
    db = read_db()
    return [u for u in db["users"] if u.get("role") == "customer"]


def seed_admin() -> None:
    """
    Buat akun admin default jika belum ada di database.

    Admin default:
        username : admin
        password : admin123

    Dipanggil otomatis saat server pertama kali dijalankan
    dari app.py (__main__).
    """
    db = read_db()

    # Cek apakah admin sudah ada
    for u in db["users"]:
        if u.get("username") == "admin":
            return   # sudah ada, tidak perlu buat lagi

    # ---- Buat objek Admin (OOP) ----
    admin = Admin(
        user_id   = "admin-001",
        username  = "admin",
        password  = generate_password_hash("admin123"),
        full_name = "Administrator",
        phone     = "08000000000",
    )

    db["users"].append(admin.to_dict())
    write_db(db)
    print("[SmartShop] Admin default dibuat → username: admin | password: admin123")