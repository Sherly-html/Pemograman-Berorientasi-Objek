# ============================================================
# services/db.py
# Database Helper — baca & tulis file JSON
#
# SmartShop menggunakan JSON sebagai database sederhana.
# Semua data disimpan dalam satu file: data/database.json
#
# Struktur database.json:
# {
#   "users"        : [ {...}, {...} ],
#   "products"     : [ {...}, {...} ],
#   "transactions" : [ {...}, {...} ],
#   "carts"        : [ {...}, {...} ]
# }
# ============================================================

import json
import os

# ---- Path absolut ke file database.json ----
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH  = os.path.join(BASE_DIR, "data", "database.json")

# ---- Struktur default jika file belum ada ----
DEFAULT_DB = {
    "users"        : [],
    "products"     : [],
    "transactions" : [],
    "carts"        : [],
}


def read_db() -> dict:
    """
    Baca seluruh isi database dari file JSON.

    Returns:
        dict: isi database (users, products, transactions, carts)

    Jika file belum ada, otomatis dibuat dengan struktur default.
    """
    if not os.path.exists(DB_PATH):
        write_db(DEFAULT_DB)
        return DEFAULT_DB.copy()

    try:
        with open(DB_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Pastikan semua key ada (jaga-jaga file rusak / tidak lengkap)
        for key in DEFAULT_DB:
            if key not in data:
                data[key] = []

        return data

    except json.JSONDecodeError:
        # File JSON rusak → reset ke default
        print(f"[DB] WARNING: {DB_PATH} rusak. Reset ke default.")
        write_db(DEFAULT_DB)
        return DEFAULT_DB.copy()


def write_db(data: dict) -> None:
    """
    Tulis data ke file database JSON.

    Args:
        data (dict): seluruh isi database yang akan disimpan

    File disimpan dengan indent=2 agar mudah dibaca manusia.
    """
    # Buat folder data/ jika belum ada
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def reset_db() -> None:
    """
    Reset database ke kondisi kosong (default).
    HATI-HATI: semua data akan terhapus!
    Gunakan hanya untuk testing / development.
    """
    write_db(DEFAULT_DB)
    print(f"[DB] Database direset ke default: {DB_PATH}")


def get_db_path() -> str:
    """Kembalikan path absolut ke file database.json."""
    return DB_PATH