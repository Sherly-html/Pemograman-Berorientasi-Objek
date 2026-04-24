# ============================================================
# services/product_service.py
# Layanan Manajemen Produk SmartShop
#
# Fungsi:
#   - get_all_products()   : ambil semua produk
#   - get_product_by_id()  : ambil satu produk by ID
#   - add_product()        : tambah produk baru (Admin)
#   - update_product()     : edit produk (Admin)
#   - delete_product()     : hapus produk (Admin)
#   - search_products()    : cari produk by nama/kategori
#   - seed_products()      : isi produk contoh pertama kali
# ============================================================

import uuid

from models.product import Product
from services.db import read_db, write_db
from exceptions.custom_error import ValidationError, ProductNotFoundError


def get_all_products() -> list:
    """
    Ambil semua produk dari database.

    Returns:
        list[Product]: daftar semua produk sebagai objek Product
    """
    db = read_db()
    return [Product.from_dict(p) for p in db.get("products", [])]


def get_product_by_id(product_id: str) -> Product:
    """
    Ambil satu produk berdasarkan product_id.

    Args:
        product_id : ID unik produk

    Returns:
        Product: objek produk yang ditemukan

    Raises:
        ProductNotFoundError: jika produk tidak ditemukan
    """
    db = read_db()
    for p in db["products"]:
        if p["product_id"] == product_id:
            return Product.from_dict(p)
    raise ProductNotFoundError(product_id)


def add_product(name: str, description: str, price: float,
                stock: int, image: str = "default.jpg",
                category: str = "Umum") -> Product:
    """
    Tambah produk baru ke database (Admin only).

    Args:
        name        : nama produk (minimal 2 karakter)
        description : deskripsi produk
        price       : harga (tidak boleh negatif)
        stock       : stok (tidak boleh negatif)
        image       : nama file gambar (default: default.jpg)
        category    : kategori produk (default: Umum)

    Returns:
        Product: objek produk yang baru ditambahkan

    Raises:
        ValidationError: jika input tidak valid
    """
    # ---- Validasi input ----
    if not name or len(name.strip()) < 2:
        raise ValidationError("Nama produk minimal 2 karakter.", "name")

    if not description or len(description.strip()) < 5:
        raise ValidationError("Deskripsi produk minimal 5 karakter.", "description")

    try:
        price = float(price)
    except (TypeError, ValueError):
        raise ValidationError("Harga harus berupa angka.", "price")

    if price < 0:
        raise ValidationError("Harga tidak boleh negatif.", "price")

    try:
        stock = int(stock)
    except (TypeError, ValueError):
        raise ValidationError("Stok harus berupa angka bulat.", "stock")

    if stock < 0:
        raise ValidationError("Stok tidak boleh negatif.", "stock")

    if not category or len(category.strip()) < 2:
        raise ValidationError("Kategori minimal 2 karakter.", "category")

    # ---- Buat objek Product (OOP) ----
    product = Product(
        product_id  = str(uuid.uuid4()),
        name        = name.strip(),
        description = description.strip(),
        price       = price,
        stock       = stock,
        image       = image.strip() if image else "default.jpg",
        category    = category.strip(),
    )

    # ---- Simpan ke database ----
    db = read_db()
    db["products"].append(product.to_dict())
    write_db(db)

    return product


def update_product(product_id: str, name: str, description: str,
                   price: float, stock: int, category: str,
                   image: str = None) -> Product:
    """
    Update data produk yang sudah ada (Admin only).

    Args:
        product_id  : ID produk yang akan diupdate
        name        : nama baru
        description : deskripsi baru
        price       : harga baru
        stock       : stok baru
        category    : kategori baru
        image       : nama file gambar baru (None = tidak diubah)

    Returns:
        Product: objek produk setelah diupdate

    Raises:
        ProductNotFoundError : jika produk tidak ditemukan
        ValidationError      : jika input tidak valid
    """
    # ---- Validasi input ----
    if not name or len(name.strip()) < 2:
        raise ValidationError("Nama produk minimal 2 karakter.", "name")

    if not description or len(description.strip()) < 5:
        raise ValidationError("Deskripsi produk minimal 5 karakter.", "description")

    try:
        price = float(price)
    except (TypeError, ValueError):
        raise ValidationError("Harga harus berupa angka.", "price")

    if price < 0:
        raise ValidationError("Harga tidak boleh negatif.", "price")

    try:
        stock = int(stock)
    except (TypeError, ValueError):
        raise ValidationError("Stok harus berupa angka bulat.", "stock")

    if stock < 0:
        raise ValidationError("Stok tidak boleh negatif.", "stock")

    # ---- Cari & update di database ----
    db = read_db()
    for i, p in enumerate(db["products"]):
        if p["product_id"] == product_id:
            db["products"][i]["name"]        = name.strip()
            db["products"][i]["description"] = description.strip()
            db["products"][i]["price"]       = price
            db["products"][i]["stock"]       = stock
            db["products"][i]["category"]    = category.strip()
            # Gambar hanya diupdate jika ada file baru
            if image and image.strip():
                db["products"][i]["image"]   = image.strip()
            write_db(db)
            return Product.from_dict(db["products"][i])

    raise ProductNotFoundError(product_id)


def delete_product(product_id: str) -> None:
    """
    Hapus produk dari database (Admin only).

    Args:
        product_id : ID produk yang akan dihapus

    Raises:
        ProductNotFoundError: jika produk tidak ditemukan
    """
    db = read_db()
    original_count = len(db["products"])
    db["products"]  = [p for p in db["products"]
                       if p["product_id"] != product_id]

    if len(db["products"]) == original_count:
        raise ProductNotFoundError(product_id)

    write_db(db)


def search_products(keyword: str = "", category: str = "") -> list:
    """
    Cari produk berdasarkan keyword nama dan/atau kategori.

    Args:
        keyword  : kata kunci pencarian nama produk
        category : filter kategori (kosong = semua kategori)

    Returns:
        list[Product]: daftar produk yang cocok
    """
    all_products = get_all_products()
    result       = []

    for p in all_products:
        match_keyword  = keyword.lower() in p.name.lower() if keyword else True
        match_category = p.category.lower() == category.lower() if category else True
        if match_keyword and match_category:
            result.append(p)

    return result


def seed_products() -> None:
    """
    Isi produk contoh ke database jika masih kosong.
    Dipanggil otomatis saat server pertama kali dijalankan.
    """
    db = read_db()
    if db.get("products"):
        return   # sudah ada produk, tidak perlu seed

    samples = [
        {
            "name"        : "Laptop Gaming ASUS ROG Strix",
            "description" : "Laptop gaming performa tinggi dengan prosesor Intel Core i7 Gen 13, RAM 16GB DDR5, SSD 512GB NVMe, GPU RTX 3060 6GB. Ideal untuk gaming dan desain.",
            "price"       : 15999000,
            "stock"       : 10,
            "image"       : "default.jpg",
            "category"    : "Elektronik",
        },
        {
            "name"        : "Smartphone Samsung Galaxy S23",
            "description" : "Smartphone flagship terbaru dengan kamera 200MP, layar Dynamic AMOLED 6.1 inch, baterai 3900mAh, prosesor Snapdragon 8 Gen 2.",
            "price"       : 9499000,
            "stock"       : 25,
            "image"       : "default.jpg",
            "category"    : "Elektronik",
        },
        {
            "name"        : "Sepatu Nike Air Max 270",
            "description" : "Sepatu olahraga premium dengan teknologi Air Max unit terbesar untuk kenyamanan sepanjang hari. Tersedia ukuran 39-45.",
            "price"       : 1350000,
            "stock"       : 50,
            "image"       : "default.jpg",
            "category"    : "Fashion",
        },
        {
            "name"        : "Tas Ransel Eiger Adventure",
            "description" : "Tas ransel outdoor premium material cordura, waterproof, kapasitas 30L, kompartemen laptop, cocok untuk hiking dan traveling.",
            "price"       : 450000,
            "stock"       : 30,
            "image"       : "default.jpg",
            "category"    : "Fashion",
        },
        {
            "name"        : "Headphone Sony WH-1000XM5",
            "description" : "Headphone wireless over-ear dengan noise cancelling terbaik di kelasnya. Battery 30 jam, koneksi multipoint, kualitas suara Hi-Res Audio.",
            "price"       : 4200000,
            "stock"       : 15,
            "image"       : "default.jpg",
            "category"    : "Elektronik",
        },
        {
            "name"        : "Kamera Mirrorless Sony Alpha A6400",
            "description" : "Kamera mirrorless APS-C dengan autofocus real-time tracking, video 4K, layar flip, cocok untuk konten kreator dan fotografer.",
            "price"       : 8750000,
            "stock"       : 8,
            "image"       : "default.jpg",
            "category"    : "Elektronik",
        },
        {
            "name"        : "Kemeja Batik Tulis Premium",
            "description" : "Kemeja batik tulis motif parang asli Solo, bahan katun prima halus, nyaman dipakai untuk acara formal maupun kasual.",
            "price"       : 285000,
            "stock"       : 100,
            "image"       : "default.jpg",
            "category"    : "Fashion",
        },
        {
            "name"        : "Meja Belajar Minimalis Kayu Jati",
            "description" : "Meja belajar minimalis dari kayu jati solid, finishing natural, ukuran 120x60cm, dilengkapi laci dan rak buku samping.",
            "price"       : 1250000,
            "stock"       : 12,
            "image"       : "default.jpg",
            "category"    : "Furniture",
        },
        {
            "name"        : "Jam Tangan Casio G-Shock GA-2100",
            "description" : "Jam tangan digital-analog G-Shock dengan desain tipis Octagon, tahan benturan, water resistant 200M, baterai 3 tahun.",
            "price"       : 1650000,
            "stock"       : 20,
            "image"       : "default.jpg",
            "category"    : "Aksesori",
        },
        {
            "name"        : "Rice Cooker Miyako 1.8L",
            "description" : "Rice cooker kapasitas 1.8 liter dengan teknologi keep warm otomatis, anti lengket, hemat listrik, cocok untuk keluarga.",
            "price"       : 195000,
            "stock"       : 40,
            "image"       : "default.jpg",
            "category"    : "Rumah Tangga",
        },
    ]

    for s in samples:
        add_product(**s)

    print(f"[SmartShop] {len(samples)} produk contoh berhasil ditambahkan.")