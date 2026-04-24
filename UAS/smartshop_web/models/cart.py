# ============================================================
# models/cart.py
# Model Keranjang Belanja SmartShop
# OOP: Encapsulation pada CartItem dan Cart
# Relasi: User → Cart → Transaction
# ============================================================

from exceptions.custom_error import ValidationError


class CartItem:
    """
    Satu baris item di dalam keranjang belanja.

    Menyimpan snapshot produk saat ditambahkan ke cart
    (nama, harga, qty) agar tidak berubah jika admin
    mengubah harga produk di tengah jalan.
    """

    def __init__(self, product_id: str, name: str,
                 price: float, quantity: int,
                 image: str = "default.jpg"):

        # ---- Atribut Private ----
        self.__product_id = product_id
        self.__name       = name
        self.__price      = price
        self.__quantity   = quantity
        self.__image      = image

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
    def price(self) -> float:
        return self.__price

    @property
    def quantity(self) -> int:
        return self.__quantity

    @property
    def image(self) -> str:
        return self.__image

    # ==================================================
    # SETTER
    # ==================================================

    @quantity.setter
    def quantity(self, value: int):
        try:
            value = int(value)
        except (TypeError, ValueError):
            raise ValidationError("Jumlah harus berupa angka.", "quantity")
        if value < 1:
            raise ValidationError("Jumlah item minimal 1.", "quantity")
        self.__quantity = value

    # ==================================================
    # METHOD
    # ==================================================

    def subtotal(self) -> float:
        """Harga total satu baris item (price × quantity)."""
        return self.__price * self.__quantity

    def format_subtotal(self) -> str:
        """Format subtotal ke Rupiah."""
        return "Rp {:,.0f}".format(self.subtotal()).replace(",", ".")

    def format_price(self) -> str:
        """Format harga satuan ke Rupiah."""
        return "Rp {:,.0f}".format(self.__price).replace(",", ".")

    def to_dict(self) -> dict:
        return {
            "product_id" : self.__product_id,
            "name"       : self.__name,
            "price"      : self.__price,
            "quantity"   : self.__quantity,
            "image"      : self.__image,
        }

    @staticmethod
    def from_dict(data: dict) -> "CartItem":
        return CartItem(
            product_id = data["product_id"],
            name       = data["name"],
            price      = data["price"],
            quantity   = data["quantity"],
            image      = data.get("image", "default.jpg"),
        )

    def __str__(self) -> str:
        return (f"{self.__name} x{self.__quantity} "
                f"@ {self.format_price()} = {self.format_subtotal()}")


# ============================================================
# CLASS CART
# ============================================================
class Cart:
    """
    Keranjang belanja milik satu user.
    Berisi daftar CartItem dan menyediakan
    method untuk tambah, hapus, update, dan hitung total.

    Relasi: User → Cart → Transaction
    """

    def __init__(self, user_id: str):
        self.__user_id = user_id
        self.__items   = []   # list of CartItem

    # ==================================================
    # GETTER
    # ==================================================

    @property
    def user_id(self) -> str:
        return self.__user_id

    @property
    def items(self) -> list:
        """Kembalikan salinan list item (bukan referensi langsung)."""
        return list(self.__items)

    # ==================================================
    # METHOD — Kelola Item
    # ==================================================

    def add_item(self, product_id: str, name: str, price: float,
                 quantity: int = 1, image: str = "default.jpg"):
        """
        Tambah produk ke cart.
        Jika produk sudah ada → tambah quantity-nya.
        Jika belum ada       → buat CartItem baru.
        """
        if quantity < 1:
            raise ValidationError("Jumlah minimal 1.", "quantity")

        for item in self.__items:
            if item.product_id == product_id:
                item.quantity = item.quantity + quantity
                return

        self.__items.append(
            CartItem(product_id, name, price, quantity, image)
        )

    def remove_item(self, product_id: str):
        """Hapus item dari cart berdasarkan product_id."""
        before = len(self.__items)
        self.__items = [i for i in self.__items
                        if i.product_id != product_id]
        if len(self.__items) == before:
            raise ValidationError(
                f"Produk '{product_id}' tidak ada di keranjang.", "product_id"
            )

    def update_quantity(self, product_id: str, quantity: int):
        """
        Update jumlah item tertentu.
        Jika quantity <= 0 → item dihapus otomatis.
        """
        for item in self.__items:
            if item.product_id == product_id:
                if quantity <= 0:
                    self.remove_item(product_id)
                else:
                    item.quantity = quantity
                return
        raise ValidationError(
            f"Produk '{product_id}' tidak ada di keranjang.", "product_id"
        )

    def clear(self):
        """Kosongkan seluruh isi keranjang."""
        self.__items = []

    # ==================================================
    # METHOD — Kalkulasi
    # ==================================================

    def total(self) -> float:
        """Total harga semua item di keranjang."""
        return sum(item.subtotal() for item in self.__items)

    def format_total(self) -> str:
        """Format total ke Rupiah."""
        return "Rp {:,.0f}".format(self.total()).replace(",", ".")

    def item_count(self) -> int:
        """Jumlah total unit produk di keranjang (bukan jumlah baris)."""
        return sum(item.quantity for item in self.__items)

    def row_count(self) -> int:
        """Jumlah baris item (jenis produk berbeda) di keranjang."""
        return len(self.__items)

    def is_empty(self) -> bool:
        """Cek apakah keranjang kosong."""
        return len(self.__items) == 0

    def has_product(self, product_id: str) -> bool:
        """Cek apakah produk tertentu sudah ada di keranjang."""
        return any(i.product_id == product_id for i in self.__items)

    # ==================================================
    # SERIALISASI
    # ==================================================

    def to_dict(self) -> dict:
        """Konversi Cart ke dict untuk disimpan ke JSON."""
        return {
            "user_id" : self.__user_id,
            "items"   : [item.to_dict() for item in self.__items],
        }

    @staticmethod
    def from_dict(data: dict) -> "Cart":
        """Buat objek Cart dari dictionary (data JSON)."""
        cart = Cart(user_id=data["user_id"])
        for item_data in data.get("items", []):
            # Langsung append ke __items via metode internal
            # agar tidak double-count qty (add_item menambah jika sudah ada)
            cart._Cart__items.append(CartItem.from_dict(item_data))
        return cart

    def __str__(self) -> str:
        if self.is_empty():
            return f"Cart user {self.__user_id} — kosong"
        lines = [f"Cart user {self.__user_id}:"]
        for item in self.__items:
            lines.append(f"  - {item}")
        lines.append(f"  TOTAL: {self.format_total()}")
        return "\n".join(lines)