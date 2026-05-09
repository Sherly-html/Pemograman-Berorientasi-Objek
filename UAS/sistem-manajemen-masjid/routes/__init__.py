# routes/__init__.py
# ============================================================
# Package Initializer untuk folder routes/
# ============================================================

from routes.public import public_bp
from routes.admin import admin_bp

__all__ = ["public_bp", "admin_bp"]