# app.py
# ============================================================
# FILE UTAMA FLASK — Entry Point Aplikasi
# ============================================================
# KONSEP OOP:
#   - Object       : app, login_manager adalah object
#   - Encapsulation: semua konfigurasi dikumpulkan lewat Config
#   - Object Relationship: app "menggunakan" masjid object
# ============================================================

from flask import Flask
from flask_login import LoginManager, UserMixin, login_user

from config import Config
from models.masjid import masjid


# ── FLASK-LOGIN: Class User ───────────────────────────────────
# KONSEP OOP: Class + Inheritance (UserMixin dari Flask-Login)
# UserMixin memberi method: is_authenticated, is_active, dll

class AdminUser(UserMixin):
    """
    CLASS   : AdminUser
    PARENT  : UserMixin (Inheritance dari Flask-Login)
    FUNGSI  : Merepresentasikan user admin yang sedang login.

    INHERITANCE:
    AdminUser mewarisi method dari UserMixin:
      - is_authenticated → True jika sudah login
      - is_active        → True jika akun aktif
      - get_id()         → mengembalikan ID user
    """
    def __init__(self, id, username):
        # PUBLIC ATTRIBUTE
        self.id       = id
        self.username = username

    def __repr__(self):
        return f"<AdminUser {self.username}>"


# ── BUAT FLASK APP ────────────────────────────────────────────
def create_app():
    """
    FACTORY FUNCTION: create_app()
    --------------------------------
    Membuat dan mengkonfigurasi Flask application.
    Mengembalikan object Flask yang sudah siap dipakai.
    """

    # Buat object Flask — ini adalah OBJECT utama aplikasi
    app = Flask(__name__)

    # Terapkan konfigurasi dari class Config (Encapsulation)
    app.config["SECRET_KEY"]  = Config.SECRET_KEY
    app.config["DEBUG"]       = Config.DEBUG

    # ── SETUP FLASK-LOGIN ─────────────────────────────────────
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view       = "admin.login"
    login_manager.login_message    = "Silakan login terlebih dahulu."
    login_manager.login_message_category = "warning"

    # Satu-satunya admin user (simple, tanpa database user)
    admin_user = AdminUser(id="1", username=Config.ADMIN_USERNAME)

    @login_manager.user_loader
    def load_user(user_id):
        """
        Callback Flask-Login: dipanggil setiap request.
        Mengembalikan object AdminUser jika user_id valid.
        """
        if user_id == "1":
            return admin_user
        return None

    # ── MUAT DATA MASJID ──────────────────────────────────────
    # OBJECT RELATIONSHIP: app menggunakan object masjid
    # Muat semua data JSON ke dalam memory saat startup
    masjid.muat_semua_data()

    # ── REGISTER BLUEPRINTS ───────────────────────────────────
    # Blueprint = cara Flask memisahkan route ke beberapa file
    # Import di dalam fungsi → cegah circular import
    from routes.public import public_bp
    from routes.admin  import admin_bp

    app.register_blueprint(public_bp)           # Route: /
    app.register_blueprint(admin_bp, url_prefix="/admin")  # Route: /admin

    # ── CONTEXT PROCESSOR ────────────────────────────────────
    # Membuat variabel 'masjid_info' tersedia di SEMUA template HTML
    @app.context_processor
    def inject_masjid():
        return {"masjid_info": masjid.to_dict()}

    return app


# ── JALANKAN APLIKASI ─────────────────────────────────────────
if __name__ == "__main__":
    app = create_app()
    print("=" * 50)
    print(f"  {Config.APP_NAME} v{Config.APP_VERSION}")
    print(f"  Running at: http://localhost:5000")
    print(f"  Admin panel: http://localhost:5000/admin")
    print("=" * 50)
    app.run(debug=Config.DEBUG, host="0.0.0.0", port=5000)