# ============================================================
# app.py — SmartShop Main Application
# Framework: Flask
# ============================================================

import os
import uuid
from flask import (Flask, render_template, request, redirect,
                   url_for, session, flash)
from werkzeug.utils import secure_filename

# Import Services
from services.auth_service import register_customer, login_user, seed_admin
from services.product_service import (get_all_products, get_product_by_id,
                                       add_product, update_product, delete_product,
                                       seed_products)
from services.transaction_service import (create_transaction, get_transactions_by_user,
                                           get_transaction_by_id, get_all_transactions,
                                           upload_payment_proof, verify_payment)
from services.db import read_db, write_db

# Import Exceptions
from exceptions.custom_error import (ValidationError, AuthenticationError,
                                      PaymentError, ProductNotFoundError)

# ============================================================
# KONFIGURASI FLASK
# ============================================================
app = Flask(__name__)
app.secret_key = "smartshop-secret-key-2024-uas-pbo"

# Folder upload bukti pembayaran
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "images", "proofs")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # Maks 5MB

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# ============================================================
# HELPER: Cart count di session
# ============================================================
def update_cart_count():
    user_id = session.get("user_id")
    if not user_id:
        session["cart_count"] = 0
        return
    db = read_db()
    for c in db.get("carts", []):
        if c["user_id"] == user_id:
            total = sum(item["quantity"] for item in c.get("items", []))
            session["cart_count"] = total
            return
    session["cart_count"] = 0


def get_cart_data(user_id: str) -> dict:
    db = read_db()
    for c in db.get("carts", []):
        if c["user_id"] == user_id:
            return c
    return {"user_id": user_id, "items": []}


def save_cart(user_id: str, cart_data: dict):
    db = read_db()
    for i, c in enumerate(db.get("carts", [])):
        if c["user_id"] == user_id:
            db["carts"][i] = cart_data
            write_db(db)
            return
    db.setdefault("carts", []).append(cart_data)
    write_db(db)


# ============================================================
# DEKORATOR: Proteksi halaman
# ============================================================
def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("user_id"):
            flash("Silakan login terlebih dahulu.", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("user_id"):
            flash("Silakan login terlebih dahulu.", "warning")
            return redirect(url_for("login"))
        if session.get("role") != "admin":
            flash("Akses ditolak. Halaman ini hanya untuk Admin.", "danger")
            return redirect(url_for("home"))
        return f(*args, **kwargs)
    return decorated


def customer_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("user_id"):
            flash("Silakan login terlebih dahulu.", "warning")
            return redirect(url_for("login"))
        if session.get("role") != "customer":
            flash("Halaman ini hanya untuk Customer.", "warning")
            return redirect(url_for("admin_dashboard"))
        return f(*args, **kwargs)
    return decorated


# ============================================================
# ROUTES: AUTH
# ============================================================

@app.route("/")
def index():
    if session.get("user_id"):
        if session.get("role") == "admin":
            return redirect(url_for("admin_dashboard"))
        return redirect(url_for("home"))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("user_id"):
        return redirect(url_for("index"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        try:
            user = login_user(username, password)
            session["user_id"]   = user["user_id"]
            session["username"]  = user["username"]
            session["full_name"] = user["full_name"]
            session["role"]      = user["role"]
            update_cart_count()
            flash(f"Selamat datang, {user['full_name']}!", "success")
            if user["role"] == "admin":
                return redirect(url_for("admin_dashboard"))
            return redirect(url_for("home"))
        except AuthenticationError as e:
            flash(e.message, "danger")
        except Exception:
            flash("Terjadi kesalahan. Coba lagi.", "danger")

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if session.get("user_id"):
        return redirect(url_for("index"))

    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        phone     = request.form.get("phone", "").strip()
        address   = request.form.get("address", "").strip()
        username  = request.form.get("username", "").strip()
        password  = request.form.get("password", "")
        try:
            register_customer(full_name, phone, address, username, password)
            flash("Akun berhasil dibuat! Silakan login.", "success")
            return redirect(url_for("login"))
        except ValidationError as e:
            flash(e.message, "danger")
        except Exception:
            flash("Registrasi gagal. Coba lagi.", "danger")

    return render_template("register.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("Kamu telah logout. Sampai jumpa!", "info")
    return redirect(url_for("login"))


# ============================================================
# ROUTES: CUSTOMER — Produk
# ============================================================

@app.route("/home")
@login_required
def home():
    products = get_all_products()
    update_cart_count()
    return render_template("home.html", products=products)


@app.route("/product/<product_id>")
@login_required
def product_detail(product_id):
    try:
        product = get_product_by_id(product_id)
        return render_template("detail.html", product=product)
    except ProductNotFoundError:
        flash("Produk tidak ditemukan.", "danger")
        return redirect(url_for("home"))


# ============================================================
# ROUTES: CUSTOMER — Cart
# ============================================================

@app.route("/cart/add", methods=["POST"])
@customer_required
def add_to_cart():
    product_id = request.form.get("product_id")
    quantity   = int(request.form.get("quantity", 1))
    try:
        product   = get_product_by_id(product_id)
        if not product.is_available():
            flash("Stok produk habis.", "danger")
            return redirect(request.referrer or url_for("home"))

        user_id   = session["user_id"]
        cart_data = get_cart_data(user_id)

        found = False
        for item in cart_data["items"]:
            if item["product_id"] == product_id:
                new_qty = item["quantity"] + quantity
                if new_qty > product.stock:
                    flash(f"Stok tidak mencukupi. Tersisa {product.stock} unit.", "warning")
                    return redirect(request.referrer or url_for("home"))
                item["quantity"] = new_qty
                found = True
                break

        if not found:
            cart_data["items"].append({
                "product_id": product.product_id,
                "name":       product.name,
                "price":      product.price,
                "quantity":   quantity,
                "image":      product.image,
            })

        save_cart(user_id, cart_data)
        update_cart_count()
        flash(f"{product.name} ditambahkan ke keranjang!", "success")
    except ProductNotFoundError:
        flash("Produk tidak ditemukan.", "danger")
    except Exception:
        flash("Gagal menambahkan ke keranjang.", "danger")

    return redirect(request.referrer or url_for("home"))


@app.route("/cart")
@customer_required
def cart():
    user_id   = session["user_id"]
    cart_data = get_cart_data(user_id)
    total     = sum(i["price"] * i["quantity"] for i in cart_data["items"])
    update_cart_count()
    return render_template("cart.html", cart=cart_data, total=total)


@app.route("/cart/update", methods=["POST"])
@customer_required
def update_cart():
    product_id = request.form.get("product_id")
    action     = request.form.get("action")
    user_id    = session["user_id"]
    cart_data  = get_cart_data(user_id)

    try:
        product = get_product_by_id(product_id)
    except ProductNotFoundError:
        flash("Produk tidak ditemukan.", "danger")
        return redirect(url_for("cart"))

    for i, item in enumerate(cart_data["items"]):
        if item["product_id"] == product_id:

            if action == "increase":
                if item["quantity"] + 1 > product.stock:
                    flash(f"Stok maksimal {product.stock} unit.", "warning")
                    return redirect(url_for("cart"))
                cart_data["items"][i]["quantity"] += 1

            elif action == "decrease":
                cart_data["items"][i]["quantity"] -= 1
                if cart_data["items"][i]["quantity"] <= 0:
                    cart_data["items"].pop(i)

            elif action == "remove":
                cart_data["items"].pop(i)

            break

    save_cart(user_id, cart_data)
    update_cart_count()
    return redirect(url_for("cart"))


@app.route("/cart/clear", methods=["POST"])
@customer_required
def clear_cart():
    user_id = session["user_id"]
    save_cart(user_id, {"user_id": user_id, "items": []})
    update_cart_count()
    flash("Keranjang dikosongkan.", "info")
    return redirect(url_for("cart"))


# ============================================================
# ROUTES: CUSTOMER — Checkout & Pembayaran
# ============================================================

@app.route("/checkout", methods=["GET", "POST"])
@customer_required
def checkout():
    user_id   = session["user_id"]
    cart_data = get_cart_data(user_id)

    if not cart_data["items"]:
        flash("Keranjang kamu kosong!", "warning")
        return redirect(url_for("cart"))

    total    = sum(i["price"] * i["quantity"] for i in cart_data["items"])
    db       = read_db()
    user_row = next((u for u in db["users"] if u["user_id"] == user_id), {})
    address  = user_row.get("address", "")

    if request.method == "POST":
        ship_address   = request.form.get("address", "").strip()
        payment_method = request.form.get("payment_method", "")

        try:
            transaction = create_transaction(
                user_id        = user_id,
                username       = session["username"],
                items          = cart_data["items"],
                total          = total,
                address        = ship_address,
                payment_method = payment_method,
            )
            save_cart(user_id, {"user_id": user_id, "items": []})
            update_cart_count()
            flash("Pesanan berhasil dibuat! Silakan upload bukti pembayaran.", "success")
            return redirect(url_for("upload_proof",
                                    transaction_id=transaction.transaction_id))
        except ValidationError as e:
            flash(e.message, "danger")
        except Exception:
            flash("Checkout gagal. Coba lagi.", "danger")

    return render_template("checkout.html",
                           cart=cart_data, total=total, address=address)


@app.route("/upload-proof/<transaction_id>", methods=["GET", "POST"])
@customer_required
def upload_proof(transaction_id):
    transaction = get_transaction_by_id(transaction_id)

    if not transaction or transaction.user_id != session["user_id"]:
        flash("Transaksi tidak ditemukan.", "danger")
        return redirect(url_for("my_orders"))

    if request.method == "POST":
        if "proof" not in request.files:
            flash("Pilih file bukti pembayaran.", "warning")
            return redirect(request.url)

        file = request.files["proof"]
        if file.filename == "":
            flash("File belum dipilih.", "warning")
            return redirect(request.url)

        if file and allowed_file(file.filename):
            ext      = file.filename.rsplit(".", 1)[1].lower()
            filename = f"proof_{transaction_id[:8]}_{uuid.uuid4().hex[:8]}.{ext}"
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(filepath)

            try:
                upload_payment_proof(transaction_id, session["user_id"], filename)
                flash("Bukti pembayaran berhasil diupload! Menunggu verifikasi admin.", "success")
                return redirect(url_for("order_status",
                                        transaction_id=transaction_id))
            except (PaymentError, ValidationError) as e:
                flash(e.message, "danger")
        else:
            flash("Format file tidak valid. Gunakan PNG, JPG, atau JPEG.", "danger")

    return render_template("upload_proof.html", transaction=transaction)


@app.route("/orders")
@customer_required
def my_orders():
    user_id      = session["user_id"]
    transactions = get_transactions_by_user(user_id)
    return render_template("status.html", transactions=transactions)


@app.route("/orders/<transaction_id>")
@customer_required
def order_status(transaction_id):
    transaction = get_transaction_by_id(transaction_id)
    if not transaction or transaction.user_id != session["user_id"]:
        flash("Pesanan tidak ditemukan.", "danger")
        return redirect(url_for("my_orders"))
    return render_template("order_detail.html", transaction=transaction)


# ============================================================
# ROUTES: ADMIN
# ============================================================

@app.route("/admin/dashboard")
@admin_required
def admin_dashboard():
    transactions = get_all_transactions()
    products     = get_all_products()
    db           = read_db()
    customers    = [u for u in db.get("users", []) if u.get("role") == "customer"]

    stats = {
        "total_products":     len(products),
        "total_customers":    len(customers),
        "total_transactions": len(transactions),
        "pending":  sum(1 for t in transactions if t.status == "pending"),
        "paid":     sum(1 for t in transactions if t.status == "paid"),
        "shipping": sum(1 for t in transactions if t.status == "dikirim"),
        "done":     sum(1 for t in transactions if t.status == "selesai"),
        "rejected": sum(1 for t in transactions if t.status == "ditolak"),
        "revenue":  sum(t.total for t in transactions
                        if t.status in ["dikirim", "selesai"]),
    }
    recent = transactions[:5]
    return render_template("admin_dashboard.html", stats=stats, recent=recent)


@app.route("/admin/products")
@admin_required
def admin_products():
    products = get_all_products()
    return render_template("admin_products.html", products=products)


@app.route("/admin/products/add", methods=["GET", "POST"])
@admin_required
def admin_add_product():
    if request.method == "POST":
        name        = request.form.get("name", "").strip()
        description = request.form.get("description", "").strip()
        price       = request.form.get("price", 0)
        stock       = request.form.get("stock", 0)
        category    = request.form.get("category", "Umum").strip()
        image       = "default.jpg"

        if "image" in request.files:
            file = request.files["image"]
            if file and file.filename and allowed_file(file.filename):
                ext      = file.filename.rsplit(".", 1)[1].lower()
                filename = f"product_{uuid.uuid4().hex[:10]}.{ext}"
                img_path = os.path.join("static", "images", filename)
                os.makedirs(os.path.dirname(img_path), exist_ok=True)
                file.save(img_path)
                image = filename

        try:
            add_product(name, description, float(price), int(stock), image, category)
            flash(f"Produk '{name}' berhasil ditambahkan!", "success")
            return redirect(url_for("admin_products"))
        except ValidationError as e:
            flash(e.message, "danger")
        except ValueError:
            flash("Harga dan stok harus berupa angka.", "danger")

    return render_template("admin_product_form.html", product=None, action="Tambah")


@app.route("/admin/products/edit/<product_id>", methods=["GET", "POST"])
@admin_required
def admin_edit_product(product_id):
    try:
        product = get_product_by_id(product_id)
    except ProductNotFoundError:
        flash("Produk tidak ditemukan.", "danger")
        return redirect(url_for("admin_products"))

    if request.method == "POST":
        name        = request.form.get("name", "").strip()
        description = request.form.get("description", "").strip()
        price       = request.form.get("price", 0)
        stock       = request.form.get("stock", 0)
        category    = request.form.get("category", "Umum").strip()
        image       = None

        if "image" in request.files:
            file = request.files["image"]
            if file and file.filename and allowed_file(file.filename):
                ext      = file.filename.rsplit(".", 1)[1].lower()
                filename = f"product_{uuid.uuid4().hex[:10]}.{ext}"
                img_path = os.path.join("static", "images", filename)
                os.makedirs(os.path.dirname(img_path), exist_ok=True)
                file.save(img_path)
                image = filename

        try:
            update_product(product_id, name, description,
                           float(price), int(stock), category, image)
            flash(f"Produk '{name}' berhasil diupdate!", "success")
            return redirect(url_for("admin_products"))
        except (ValidationError, ProductNotFoundError) as e:
            flash(str(e), "danger")
        except ValueError:
            flash("Harga dan stok harus berupa angka.", "danger")

    return render_template("admin_product_form.html", product=product, action="Edit")


@app.route("/admin/products/delete/<product_id>", methods=["POST"])
@admin_required
def admin_delete_product(product_id):
    try:
        delete_product(product_id)
        flash("Produk berhasil dihapus.", "success")
    except ProductNotFoundError:
        flash("Produk tidak ditemukan.", "danger")
    return redirect(url_for("admin_products"))


@app.route("/admin/transactions")
@admin_required
def admin_transactions():
    status_filter = request.args.get("status", "")
    transactions  = get_all_transactions()
    if status_filter:
        transactions = [t for t in transactions if t.status == status_filter]
    return render_template("admin_transactions.html",
                           transactions=transactions,
                           status_filter=status_filter)


@app.route("/admin/verify/<transaction_id>", methods=["GET", "POST"])
@admin_required
def admin_verify(transaction_id):
    transaction = get_transaction_by_id(transaction_id)
    if not transaction:
        flash("Transaksi tidak ditemukan.", "danger")
        return redirect(url_for("admin_transactions"))

    if request.method == "POST":
        action = request.form.get("action")
        note   = request.form.get("note", "").strip()
        try:
            verify_payment(transaction_id, action, note)
            if action == "approve":
                flash("Pembayaran diverifikasi! Status diubah ke Dikirim.", "success")
            else:
                flash("Pembayaran ditolak.", "warning")
            return redirect(url_for("admin_transactions"))
        except (ValidationError, PaymentError) as e:
            flash(str(e), "danger")

    return render_template("verification.html", transaction=transaction)


# ============================================================
# JALANKAN SERVER
# ============================================================
if __name__ == "__main__":
    seed_admin()
    seed_products()

    print("=" * 50)
    print("  SmartShop Server Berjalan!")
    print("=" * 50)
    print("  Local  : http://127.0.0.1:5000")
    print("  HP/Tab : http://<IP-LAPTOP>:5000")
    print("  Admin  : username=admin | password=admin123")
    print("=" * 50)

    app.run(host="0.0.0.0", port=5000, debug=True)