# models/__init__.py
# ============================================================
# Package Initializer untuk folder models/
# ============================================================
# File ini wajib ada agar Python mengenali folder 'models'
# sebagai sebuah package yang bisa di-import.
#
# Tanpa file ini:
#   from models.artikel import Artikel  → ERROR!
# Dengan file ini:
#   from models.artikel import Artikel  → OK!
# ============================================================

from models.base_model import BaseModel
from models.artikel import Artikel
from models.kajian import Kajian
from models.pengumuman import Pengumuman
from models.masjid import Masjid, masjid

# Daftar semua yang bisa di-import dari package ini
__all__ = [
    "BaseModel",
    "Artikel",
    "Kajian",
    "Pengumuman",
    "Masjid",
    "masjid"
]