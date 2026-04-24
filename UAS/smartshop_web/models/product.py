# ============================================================
# models/product.py
# Model Produk SmartShop
# OOP: Encapsulation (atribut private + getter/setter)
# ============================================================

from exceptions.custom_error import ValidationError


class Product:
    """
    Class Product — menyimpan data satu produk.

    Menerapkan Encapsulation:
    - Semua atribut dibuat private (__nama)
    - Akses dari luar hanya via getter (@property)
    - Perubahan data hanya via setter (dengan validasi)
    """

    def __init__(self, product_id: str, name: str, description: str,
                 price: float, stock: int,
                 image: str = "default.jpg", category: str = "Umum"):

        # ---- Atribut Private (Encapsulation) ----
        self.__product_id  = product_id
        self.__name        = name
        self.__description = description
        self.__price       = price
        self.__stock       = stock
        self.__image       = image
        self.__category    = category

    # ==================================================
    # GETTER
    # ==================================================

    @property
    def product_id(self) -> str:
        return self.__product_id

    @property
    def name(self) -> str:
        return self.__name

    @property
    def description(self) -> str:
        return self.__description

    @property
    def price(self) -> float:
        return self.__price

    @property
    def stock(self) -> int:
        return self.__stock

    @property
    def image(self) -> str:
        return self.__image

    @property
    def category(self) -> str:
        return self.__category

    # ==================================================
    # SETTER (dengan validasi)
    # ==================================================

    @name.setter
    def name(self, value: str):
        if not value or len(value.strip()) < 2:
            raise ValidationError("Nama produk minimal 2 karakter.", "name")
        self.__name = value.strip()

    @description.setter
    def description(self, value: str):
        if not value:
            raise ValidationError("Deskripsi tidak boleh kosong.", "description")
        self.__description = value.strip()

    @price.setter
    def price(self, value: float):
        try:
            value = float(value)
        except (TypeError, ValueError):
            raise ValidationError("Harga harus berupa angka.", "price")
        if value < 0:
            raise ValidationError("Harga tidak boleh negatif.", "price")
        self.__price = value

    @stock.setter
    def stock(self, value: int):
        try:
            value = int(value)
        except (TypeError, ValueError):
            raise ValidationError("Stok harus berupa angka.", "stock")
        if value < 0:
            raise ValidationError("Stok tidak boleh negatif.", "stock")
        self.__stock = value

    @image.setter
    def image(self, value: str):
        if value and value.strip():
            self.__image = value.strip()

    @category.setter
    def category(self, value: str):
        if not value or len(value.strip()) < 2:
            raise ValidationError("Kategori tidak boleh kosong.", "category")
        self.__category = value.strip()

    # ==================================================
    # METHOD
    # ==================================================

    def is_available(self) -> bool:
        """Cek apakah produk masih tersedia (stok > 0)."""
        return self.__stock > 0

    def reduce_stock(self, qty: int):
        """
        Kurangi stok setelah produk dibeli.
        Raise ValidationError jika stok tidak mencukupi.
        """
        try:
            qty = int(qty)
        except (TypeError, ValueError):
            raise ValidationError("Jumlah harus berupa angka.", "qty")
        if qty <= 0:
            raise ValidationError("Jumlah pembelian minimal 1.", "qty")
        if qty > self.__stock:
            raise ValidationError(
                f"Stok tidak mencukupi. Tersisa: {self.__stock} unit.", "stock"
            )
        self.__stock -= qty

    def format_price(self) -> str:
        """
        Format harga ke format Rupiah.
        Contoh: 15999000 → 'Rp 15.999.000'
        """
        return "Rp {:,.0f}".format(self.__price).replace(",", ".")

    def to_dict(self) -> dict:
        """Konversi objek Product ke dict untuk disimpan ke JSON."""
        return {
            "product_id"  : self.__product_id,
            "name"        : self.__name,
            "description" : self.__description,
            "price"       : self.__price,
            "stock"       : self.__stock,
            "image"       : self.__image,
            "category"    : self.__category,
        }

    @staticmethod
    def from_dict(data: dict) -> "Product":
        """Buat objek Product dari dictionary (data JSON)."""
        return Product(
            product_id  = data["product_id"],
            name        = data["name"],
            description = data["description"],
            price       = data["price"],
            stock       = data["stock"],
            image       = data.get("image", "default.jpg"),
            category    = data.get("category", "Umum"),
        )

    def __str__(self) -> str:
        return (f"[Produk] {self.__name} | "
                f"{self.format_price()} | "
                f"Stok: {self.__stock} | "
                f"Kategori: {self.__category}")