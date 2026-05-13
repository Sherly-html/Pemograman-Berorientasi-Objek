# config.py
# ============================================================
# FILE KONFIGURASI PROJECT
# Berisi pengaturan global untuk seluruh aplikasi Flask
# ============================================================
# KONSEP OOP: Class, Class Attribute, Encapsulation
# ============================================================

import os


class Config:
    """
    CLASS: Config
    -------------
    Menyimpan semua konfigurasi aplikasi sebagai class attribute.
    
    KONSEP OOP:
    - Class         : Config adalah sebuah class
    - Encapsulation : Semua konfigurasi dikumpulkan dalam 1 class
    - Class Attribute: Atribut langsung di class (bukan di __init__)
    """

    # ── PUBLIC ATTRIBUTE ───────────────────────────────────────
    # Bisa diakses dari mana saja
    APP_NAME = "Sistem Manajemen Masjid"
    APP_VERSION = "1.0.0"
    DEBUG = True

    # Secret key untuk keamanan session Flask
    # os.urandom(24) menghasilkan string acak 24 byte
    SECRET_KEY = os.environ.get("SECRET_KEY") or "masjid-secret-key-2026"

    # ── PATH KONFIGURASI ──────────────────────────────────────
    # Lokasi folder data JSON
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = os.path.join(BASE_DIR, "data")

    # Path lengkap setiap file JSON
    ARTIKEL_FILE    = os.path.join(DATA_DIR, "artikel.json")
    KAJIAN_FILE     = os.path.join(DATA_DIR, "kajian.json")
    PENGUMUMAN_FILE = os.path.join(DATA_DIR, "pengumuman.json")
    MASJID_FILE     = os.path.join(DATA_DIR, "masjid.json")

    # ── ADMIN CREDENTIAL ─────────────────────────────────────
    # Username & password admin (sederhana, tanpa database user)
    ADMIN_USERNAME = "admin"
    ADMIN_PASSWORD = "masjid2026"

    # ── PAGINATION ────────────────────────────────────────────
    ITEMS_PER_PAGE = 6