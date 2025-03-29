from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                          QPushButton, QFrame, QScrollArea, QSpacerItem, QSizePolicy, 
                          QGridLayout, QMessageBox, QSpinBox)
from PyQt5.QtGui import QFont, QPixmap, QIcon, QColor, QPainter, QLinearGradient
from PyQt5.QtCore import Qt, pyqtSignal, QSize
import os
import json
from datetime import datetime
from models import UserModel

# Data menu makanan dan minuman
FOOD_MENU = [
    {"id": "F1", "name": "Popcorn (S)", "price": 25000, "category": "Makanan", "image": "popcorn_mini.jpg"},
    {"id": "F2", "name": "Popcorn (M)", "price": 35000, "category": "Makanan", "image": "popcorn_medium.jpg"},
    {"id": "F4", "name": "Popcorn Caramel", "price": 40000, "category": "Makanan", "image": "popcorn_caramel.jpg"},
    {"id": "F5", "name": "Popcorn Cheese", "price": 40000, "category": "Makanan", "image": "Popcorn_cheese.jpg"},
    {"id": "F7", "name": "Hotdog", "price": 30000, "category": "Makanan", "image": "hotdog.jpeg"},
    {"id": "F8", "name": "Nasi Padang", "price": 35000, "category": "Makanan", "image": "nasi_padang.jpeg"}
]

DRINK_MENU = [
    {"id": "D1", "name": "Coca Cola (S)", "price": 15000, "category": "Minuman", "image": "cocacola_mini.webp"},
    {"id": "D2", "name": "Coca Cola (M)", "price": 20000, "category": "Minuman", "image": "coca_cola_medium.png"},
    {"id": "D4", "name": "Sprite (S)", "price": 15000, "category": "Minuman", "image": "sprite_mini.jpeg"},
    {"id": "D5", "name": "Sprite (M)", "price": 20000, "category": "Minuman", "image": "sprite_medium.jpg"}
]

class FoodItem(QFrame):
    """Widget untuk menampilkan item makanan/minuman"""
    item_added = pyqtSignal(dict, int)  # Signal ketika item ditambahkan ke keranjang (item, jumlah)
    
    def __init__(self, item_data):
        super().__init__()
        self.item_data = item_data
        self.init_ui()
        
    def init_ui(self):
        # Set style untuk frame
        self.setFrameShape(QFrame.StyledPanel)
        self.setObjectName("food_item")
        self.setStyleSheet("""
            #food_item {
                background-color: #1E1E1E;
                border-radius: 15px;
                border: 1px solid #2A2A2A;
                padding: 15px;
            }
            #food_item:hover {
                background-color: #252525;
                border: 1px solid #FFD700;
                transform: translateY(-2px);
                transition: all 0.3s ease;
            }
        """)
        
        # Layout utama
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 15)
        layout.setSpacing(10)
        
        # Gambar makanan/minuman dengan container
        image_container = QFrame()
        image_container.setObjectName("image_container")
        image_container.setFixedSize(160, 160)
        image_container.setStyleSheet("""
            #image_container {
                background-color: #252525;
                border-radius: 12px;
                border: 1px solid #2A2A2A;
            }
        """)
        
        image_layout = QVBoxLayout(image_container)
        image_layout.setContentsMargins(0, 0, 0, 0)
        
        image_label = QLabel()
        image_label.setAlignment(Qt.AlignCenter)
        image_label.setFixedSize(140, 140)
        
        # Coba muat gambar
        image_path = os.path.join("assets", "food", self.item_data['image'])
        if os.path.exists(image_path):
            pixmap = QPixmap(image_path)
            pixmap = pixmap.scaled(140, 140, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            image_label.setPixmap(pixmap)
        else:
            # Jika gambar tidak ditemukan, tampilkan placeholder
            image_label.setText("No Image")
            image_label.setStyleSheet("color: #666; font-family: 'Poppins';")
        
        image_layout.addWidget(image_label, 0, Qt.AlignCenter)
        layout.addWidget(image_container, 0, Qt.AlignCenter)
        
        # Nama item
        name_label = QLabel(self.item_data['name'])
        name_label.setAlignment(Qt.AlignCenter)
        name_label.setFont(QFont("Poppins", 12, QFont.DemiBold))
        name_label.setStyleSheet("color: #FFFFFF; margin-top: 8px;")
        layout.addWidget(name_label)
        
        # Harga
        price_label = QLabel(f"Rp {self.item_data['price']:,}".replace(',', '.'))
        price_label.setAlignment(Qt.AlignCenter)
        price_label.setStyleSheet("color: #FFD700; font-weight: bold; font-family: 'Poppins'; font-size: 13px; margin-top: 2px;")
        layout.addWidget(price_label)
        
        # Layout untuk input jumlah dan tombol tambah
        add_layout = QHBoxLayout()
        add_layout.setContentsMargins(5, 10, 5, 0)
        
        # Input jumlah
        self.quantity_input = QSpinBox()
        self.quantity_input.setMinimum(1)
        self.quantity_input.setMaximum(10)
        self.quantity_input.setValue(1)
        self.quantity_input.setFixedWidth(50)
        self.quantity_input.setAlignment(Qt.AlignCenter)
        self.quantity_input.setStyleSheet("""
            QSpinBox {
                background-color: #252525;
                color: #FFFFFF;
                border: 1px solid #2A2A2A;
                border-radius: 5px;
                padding: 5px;
                font-family: 'Poppins';
            }
            QSpinBox::up-button, QSpinBox::down-button {
                width: 18px;
                border-radius: 3px;
                background-color: #2A2A2A;
            }
            QSpinBox::up-button:hover, QSpinBox::down-button:hover {
                background-color: #333333;
            }
        """)
        add_layout.addWidget(self.quantity_input)
        
        # Tombol tambah ke keranjang
        add_button = QPushButton("+ Tambah")
        add_button.setStyleSheet("""
            QPushButton {
                background-color: #FFD700;
                color: #000000;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                font-weight: bold;
                font-family: 'Poppins';
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #F5CB0C;
            }
            QPushButton:pressed {
                background-color: #E6C000;
            }
        """)
        add_button.clicked.connect(self.add_to_cart)
        add_layout.addWidget(add_button)
        
        layout.addLayout(add_layout)
    
    def add_to_cart(self):
        """Tambahkan item ke keranjang"""
        quantity = self.quantity_input.value()
        self.item_added.emit(self.item_data, quantity)
        
        # Reset jumlah ke 1 setelah ditambahkan
        self.quantity_input.setValue(1)

class CartItem(QFrame):
    """Widget untuk menampilkan item dalam keranjang"""
    quantity_changed = pyqtSignal(str, int)  # Signal ketika jumlah item diubah (item_id, jumlah)
    item_removed = pyqtSignal(str)  # Signal ketika item dihapus dari keranjang (item_id)
    
    def __init__(self, item_data, quantity=1):
        super().__init__()
        self.item_data = item_data
        self.quantity = quantity
        self.init_ui()
        
    def init_ui(self):
        # Set style untuk frame
        self.setFrameShape(QFrame.StyledPanel)
        self.setObjectName("cart_item")
        self.setStyleSheet("""
            #cart_item {
                background-color: #1A1A1A;
                border-radius: 8px;
                border: 1px solid #2A2A2A;
                margin-bottom: 8px;
            }
        """)
        
        # Layout utama
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(10)
        
        # Informasi item
        info_layout = QVBoxLayout()
        info_layout.setSpacing(3)
        
        # Nama item
        name_label = QLabel(self.item_data['name'])
        name_label.setFont(QFont("Montserrat", 10, QFont.Bold))
        name_label.setStyleSheet("color: #FFFFFF;")
        info_layout.addWidget(name_label)
        
        # Harga satuan
        price_label = QLabel(f"Rp {self.item_data['price']:,}".replace(',', '.'))
        price_label.setStyleSheet("color: #B3B3B3; font-size: 9pt; font-family: 'Montserrat';")
        info_layout.addWidget(price_label)
        
        layout.addLayout(info_layout)
        
        # Control jumlah
        quantity_layout = QHBoxLayout()
        quantity_layout.setSpacing(6)
        
        # Label jumlah
        self.quantity_label = QLabel(str(self.quantity))
        self.quantity_label.setAlignment(Qt.AlignCenter)
        self.quantity_label.setFixedWidth(20)
        self.quantity_label.setStyleSheet("color: #FFFFFF; font-weight: bold; font-family: 'Montserrat';")
        
        # Tombol kurangi
        decrease_button = QPushButton("-")
        decrease_button.setFixedSize(22, 22)
        decrease_button.setStyleSheet("""
            QPushButton {
                background-color: #2A2A2A;
                color: #FFFFFF;
                border: none;
                border-radius: 11px;
                font-weight: bold;
                padding: 0;
                font-family: 'Montserrat';
            }
            QPushButton:hover {
                background-color: #444444;
            }
        """)
        decrease_button.clicked.connect(self.decrease_quantity)
        
        # Tombol tambah
        increase_button = QPushButton("+")
        increase_button.setFixedSize(22, 22)
        increase_button.setStyleSheet("""
            QPushButton {
                background-color: #2A2A2A;
                color: #FFFFFF;
                border: none;
                border-radius: 11px;
                font-weight: bold;
                padding: 0;
                font-family: 'Montserrat';
            }
            QPushButton:hover {
                background-color: #444444;
            }
        """)
        increase_button.clicked.connect(self.increase_quantity)
        
        quantity_layout.addWidget(decrease_button)
        quantity_layout.addWidget(self.quantity_label)
        quantity_layout.addWidget(increase_button)
        
        layout.addLayout(quantity_layout)
        
        # Sub total
        self.subtotal_label = QLabel(f"Rp {self.item_data['price'] * self.quantity:,}".replace(',', '.'))
        self.subtotal_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.subtotal_label.setStyleSheet("color: #FFD700; font-weight: bold; min-width: 80px; font-family: 'Montserrat'; font-size: 10pt;")
        layout.addWidget(self.subtotal_label)
        
        # Tombol hapus
        remove_button = QPushButton("×")
        remove_button.setFixedSize(22, 22)
        remove_button.setStyleSheet("""
            QPushButton {
                background-color: #B71C1C;
                color: white;
                border: none;
                border-radius: 11px;
                font-weight: bold;
                padding: 0;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #D32F2F;
            }
        """)
        remove_button.clicked.connect(self.remove_item)
        layout.addWidget(remove_button)
    
    def update_quantity(self, quantity):
        """Update jumlah item dalam keranjang"""
        self.quantity = quantity
        self.quantity_label.setText(str(quantity))
        self.subtotal_label.setText(f"Rp {self.item_data['price'] * quantity:,}".replace(',', '.'))
    
    def increase_quantity(self):
        """Tambah jumlah item"""
        if self.quantity < 10:  # Batasi hingga 10 item
            self.quantity += 1
            self.update_quantity(self.quantity)
            self.quantity_changed.emit(self.item_data['id'], self.quantity)
    
    def decrease_quantity(self):
        """Kurangi jumlah item"""
        if self.quantity > 1:
            self.quantity -= 1
            self.update_quantity(self.quantity)
            self.quantity_changed.emit(self.item_data['id'], self.quantity)
        else:
            # Jika jumlah 1 dan dikurangi, hapus item
            self.remove_item()
    
    def remove_item(self):
        """Hapus item dari keranjang"""
        self.item_removed.emit(self.item_data['id'])
        self.deleteLater()

class FoodPage(QWidget):
    """Halaman untuk pemesanan makanan dan minuman"""
    order_completed = pyqtSignal(dict)  # Signal ketika order selesai
    
    def __init__(self, user_data=None):
        super().__init__()
        self.user_data = user_data
        self.cart_items = {}  # Dictionary untuk menyimpan item di keranjang {item_id: (item_data, quantity)}
        self.init_ui()
        
    def init_ui(self):
        """Inisialisasi antarmuka pengguna"""
        # Layout utama
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Panel kiri untuk daftar menu (2/3 lebar)
        left_panel = QWidget()
        left_panel.setObjectName("left_panel")
        left_panel.setStyleSheet("""
            #left_panel {
                background-color: #121212;
            }
        """)
        # Set panel kiri ke 2/3 lebar
        left_panel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        left_panel.setMinimumWidth(600)
        
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(40, 40, 40, 40)
        
        # Header Container
        header_container = QWidget()
        header_container.setObjectName("header_container")
        header_container.setStyleSheet("""
            #header_container {
                background-color: #1A1A1A;
                border-radius: 15px;
                padding: 25px;
                margin-bottom: 30px;
            }
        """)
        header_layout = QVBoxLayout(header_container)
        header_layout.setContentsMargins(20, 20, 20, 20)
        
        # Judul halaman
        title_label = QLabel("Menu Makanan & Minuman")
        title_label.setFont(QFont("Poppins", 24, QFont.Bold))
        title_label.setStyleSheet("color: #FFD700; margin-bottom: 10px;")
        header_layout.addWidget(title_label)
        
        # Informasi
        info_label = QLabel("Pilih makanan dan minuman favorit Anda. Tambahkan ke keranjang dan bayar untuk menikmati selama menonton film.")
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #B3B3B3; font-family: 'Poppins'; font-size: 14px; line-height: 1.6;")
        header_layout.addWidget(info_label)
        
        left_layout.addWidget(header_container)
        
        # Scroll area untuk menu
        menu_scroll = QScrollArea()
        menu_scroll.setWidgetResizable(True)
        menu_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        menu_scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                background-color: #1A1A1A;
                width: 10px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background-color: #333333;
                min-height: 30px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #444444;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        menu_widget = QWidget()
        menu_widget.setStyleSheet("background-color: transparent;")
        menu_layout = QVBoxLayout(menu_widget)
        menu_layout.setContentsMargins(0, 0, 15, 0)
        menu_layout.setSpacing(40)
        
        # Section Makanan
        food_section = QFrame()
        food_section.setObjectName("food_section")
        food_section.setStyleSheet("""
            #food_section {
                background-color: #1A1A1A;
                border-radius: 15px;
                padding: 25px;
            }
        """)
        food_layout = QVBoxLayout(food_section)
        food_layout.setContentsMargins(20, 20, 20, 20)
        food_layout.setSpacing(25)
        
        food_title = QLabel("Makanan")
        food_title.setFont(QFont("Poppins", 18, QFont.Bold))
        food_title.setStyleSheet("color: #FFFFFF; margin-bottom: 5px;")
        food_layout.addWidget(food_title)
        
        # Grid untuk item makanan
        food_grid = QGridLayout()
        food_grid.setHorizontalSpacing(25)
        food_grid.setVerticalSpacing(25)
        
        # Tambahkan item makanan ke grid
        row, col = 0, 0
        for food in FOOD_MENU:
            food_item = FoodItem(food)
            food_item.item_added.connect(self.add_to_cart)
            food_grid.addWidget(food_item, row, col)
            
            col += 1
            if col > 2:  # 3 kolom per baris
                col = 0
                row += 1
        
        food_layout.addLayout(food_grid)
        menu_layout.addWidget(food_section)
        
        # Section Minuman
        drink_section = QFrame()
        drink_section.setObjectName("drink_section")
        drink_section.setStyleSheet("""
            #drink_section {
                background-color: #1A1A1A;
                border-radius: 15px;
                padding: 25px;
            }
        """)
        drink_layout = QVBoxLayout(drink_section)
        drink_layout.setContentsMargins(20, 20, 20, 20)
        drink_layout.setSpacing(25)
        
        drink_title = QLabel("Minuman")
        drink_title.setFont(QFont("Poppins", 18, QFont.Bold))
        drink_title.setStyleSheet("color: #FFFFFF; margin-bottom: 5px;")
        drink_layout.addWidget(drink_title)
        
        # Grid untuk item minuman
        drink_grid = QGridLayout()
        drink_grid.setHorizontalSpacing(25)
        drink_grid.setVerticalSpacing(25)
        
        # Tambahkan item minuman ke grid
        row, col = 0, 0
        for drink in DRINK_MENU:
            drink_item = FoodItem(drink)
            drink_item.item_added.connect(self.add_to_cart)
            drink_grid.addWidget(drink_item, row, col)
            
            col += 1
            if col > 2:  # 3 kolom per baris
                col = 0
                row += 1
        
        drink_layout.addLayout(drink_grid)
        menu_layout.addWidget(drink_section)
        
        # Tambahkan spacer di bagian bawah
        menu_layout.addStretch()
        
        menu_scroll.setWidget(menu_widget)
        left_layout.addWidget(menu_scroll)
        
        # Panel kanan untuk keranjang (1/3 lebar)
        right_panel = QWidget()
        right_panel.setObjectName("right_panel")
        right_panel.setStyleSheet("""
            #right_panel {
                background-color: #1A1A1A;
                border-left: 1px solid #2A2A2A;
            }
        """)
        # Set panel kanan ke 1/3 lebar layar
        right_panel.setFixedWidth(350)
        
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(30, 40, 30, 40)
        
        # Judul keranjang dengan icon
        cart_header = QHBoxLayout()
        cart_icon = QLabel()
        cart_icon_path = os.path.join("assets", "icons", "cart.png")
        if os.path.exists(cart_icon_path):
            cart_pixmap = QPixmap(cart_icon_path)
            cart_icon.setPixmap(cart_pixmap.scaled(24, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        cart_title = QLabel("Keranjang Belanja")
        cart_title.setFont(QFont("Poppins", 20, QFont.Bold))
        cart_title.setStyleSheet("color: #FFD700;")
        cart_header.addWidget(cart_icon)
        cart_header.addWidget(cart_title)
        cart_header.addStretch()
        right_layout.addLayout(cart_header)
        
        # Divider
        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        divider.setStyleSheet("background-color: #2A2A2A; margin: 20px 0;")
        right_layout.addWidget(divider)
        
        # Scroll area untuk item keranjang
        cart_scroll = QScrollArea()
        cart_scroll.setWidgetResizable(True)
        cart_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        cart_scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                background-color: #252525;
                width: 8px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background-color: #444444;
                min-height: 30px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #555555;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        self.cart_widget = QWidget()
        self.cart_widget.setStyleSheet("background-color: transparent;")
        self.cart_layout = QVBoxLayout(self.cart_widget)
        self.cart_layout.setContentsMargins(0, 0, 0, 0)
        self.cart_layout.setSpacing(12)
        
        # Label keranjang kosong
        self.empty_cart_label = QLabel("Keranjang belanja Anda kosong.")
        self.empty_cart_label.setAlignment(Qt.AlignCenter)
        self.empty_cart_label.setStyleSheet("color: #808080; margin: 40px 0; font-family: 'Poppins'; font-size: 14px;")
        self.cart_layout.addWidget(self.empty_cart_label)
        
        # Spacer untuk item keranjang
        self.cart_layout.addStretch()
        
        cart_scroll.setWidget(self.cart_widget)
        right_layout.addWidget(cart_scroll)
        
        # Ringkasan keranjang
        summary_frame = QFrame()
        summary_frame.setFrameShape(QFrame.StyledPanel)
        summary_frame.setObjectName("summary_frame")
        summary_frame.setStyleSheet("""
            #summary_frame {
                background-color: #1A1A1A;
                border-radius: 12px;
                border: 1px solid #2A2A2A;
                padding: 20px;
                margin-top: 20px;
            }
        """)
        
        summary_layout = QVBoxLayout(summary_frame)
        summary_layout.setSpacing(15)
        
        # Judul ringkasan
        summary_title = QLabel("Ringkasan Belanja")
        summary_title.setFont(QFont("Poppins", 14, QFont.Bold))
        summary_title.setStyleSheet("color: #FFFFFF; margin-bottom: 5px;")
        summary_layout.addWidget(summary_title)
        
        # Total item
        total_item_layout = QHBoxLayout()
        total_item_label = QLabel("Total Item")
        total_item_label.setStyleSheet("color: #B3B3B3; font-family: 'Poppins'; font-size: 14px;")
        self.total_item_value = QLabel("0")
        self.total_item_value.setStyleSheet("color: #FFFFFF; font-family: 'Poppins'; font-size: 14px; font-weight: bold;")
        total_item_layout.addWidget(total_item_label)
        total_item_layout.addStretch()
        total_item_layout.addWidget(self.total_item_value)
        summary_layout.addLayout(total_item_layout)
        
        # Divider
        summary_divider = QFrame()
        summary_divider.setFrameShape(QFrame.HLine)
        summary_divider.setStyleSheet("background-color: #2A2A2A; margin: 5px 0;")
        summary_layout.addWidget(summary_divider)
        
        # Total harga
        total_price_layout = QHBoxLayout()
        total_price_label = QLabel("Total Harga")
        total_price_label.setStyleSheet("color: #B3B3B3; font-family: 'Poppins'; font-size: 14px;")
        self.total_price_value = QLabel("Rp 0")
        self.total_price_value.setFont(QFont("Poppins", 20, QFont.Bold))
        self.total_price_value.setStyleSheet("color: #FFD700; margin-right: 5px;")
        self.total_price_value.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.total_price_value.setMinimumWidth(120)  # Ensure enough space for the price
        total_price_layout.addWidget(total_price_label)
        total_price_layout.addStretch()
        total_price_layout.addWidget(self.total_price_value)
        summary_layout.addLayout(total_price_layout)
        
        right_layout.addWidget(summary_frame)
        
        # Tombol checkout
        self.checkout_button = QPushButton("Bayar Sekarang")
        self.checkout_button.setStyleSheet("""
            QPushButton {
                background-color: #FFD700;
                color: #000000;
                border: none;
                border-radius: 8px;
                padding: 15px;
                font-size: 15px;
                font-weight: bold;
                margin-top: 25px;
                font-family: 'Poppins';
            }
            QPushButton:hover {
                background-color: #F5CB0C;
            }
            QPushButton:pressed {
                background-color: #E6C000;
            }
            QPushButton:disabled {
                background-color: #333333;
                color: #666666;
            }
        """)
        self.checkout_button.setEnabled(False)  # Disabled sampai ada item di keranjang
        self.checkout_button.clicked.connect(self.checkout)
        right_layout.addWidget(self.checkout_button)
        
        # Tambahkan panel ke layout utama
        main_layout.addWidget(left_panel, 2)
        main_layout.addWidget(right_panel, 1)
        
        # Update tampilan
        self.update_cart_summary()
    
    def add_to_cart(self, item_data, quantity):
        """Tambahkan item ke keranjang belanja"""
        item_id = item_data['id']
        
        if item_id in self.cart_items:
            # Jika item sudah ada di keranjang, update jumlahnya
            existing_item, existing_quantity = self.cart_items[item_id]
            new_quantity = min(existing_quantity + quantity, 10)  # Batasi hingga 10 item
            
            # Update data di cart_items
            self.cart_items[item_id] = (existing_item, new_quantity)
            
            # Cari widget item di keranjang dan update
            for i in range(self.cart_layout.count()):
                widget = self.cart_layout.itemAt(i).widget()
                if isinstance(widget, CartItem) and widget.item_data['id'] == item_id:
                    widget.update_quantity(new_quantity)
                    break
        else:
            # Jika item belum ada di keranjang, tambahkan item baru
            self.cart_items[item_id] = (item_data, quantity)
            
            # Tambahkan widget item ke keranjang
            cart_item = CartItem(item_data, quantity)
            cart_item.quantity_changed.connect(self.update_cart_item_quantity)
            cart_item.item_removed.connect(self.remove_from_cart)
            
            # Sembunyikan label keranjang kosong jika ini item pertama
            if len(self.cart_items) == 1:
                self.empty_cart_label.setVisible(False)
            
            # Tambahkan item sebelum spacer
            self.cart_layout.insertWidget(self.cart_layout.count() - 1, cart_item)
        
        # Update ringkasan keranjang
        self.update_cart_summary()
    
    def update_cart_item_quantity(self, item_id, quantity):
        """Update jumlah item di keranjang"""
        if item_id in self.cart_items:
            item_data, _ = self.cart_items[item_id]
            self.cart_items[item_id] = (item_data, quantity)
            self.update_cart_summary()
    
    def remove_from_cart(self, item_id):
        """Hapus item dari keranjang"""
        if item_id in self.cart_items:
            del self.cart_items[item_id]
            self.update_cart_summary()
            
            # Tampilkan label keranjang kosong jika tidak ada item
            if not self.cart_items:
                self.empty_cart_label.setVisible(True)
    
    def update_cart_summary(self):
        """Update ringkasan keranjang belanja"""
        total_items = sum(quantity for _, quantity in self.cart_items.values())
        total_price = sum(item['price'] * quantity for (item, quantity) in self.cart_items.values())
        
        # Update the total item count
        self.total_item_value.setText(str(total_items))
        
        # Format the price with thousand separators and ensure visibility
        formatted_price = f"Rp {total_price:,}".replace(',', '.')
        self.total_price_value.setText(formatted_price)
        
        # Add debug print to verify the price is correctly formatted
        print(f"Updated cart total: {formatted_price}")
        
        # Aktifkan/nonaktifkan tombol checkout
        self.checkout_button.setEnabled(bool(self.cart_items))
    
    def checkout(self):
        """Proses checkout pemesanan"""
        if not self.cart_items:
            QMessageBox.warning(self, "Keranjang Kosong", "Tambahkan item ke keranjang terlebih dahulu.")
            return
        
        # Hitung total harga
        total_price = sum(item['price'] * quantity for (item, quantity) in self.cart_items.values())
        
        # Cek saldo pengguna
        if self.user_data and 'username' in self.user_data:
            current_saldo = UserModel.get_saldo(self.user_data['username'])
            
            if current_saldo < total_price:
                QMessageBox.warning(
                    self, 
                    "Saldo Tidak Mencukupi", 
                    f"Saldo anda (Rp {current_saldo:,}) tidak mencukupi untuk pembelian ini (Rp {total_price:,}).\n\nSilakan top-up saldo Anda terlebih dahulu.".replace(',', '.')
                )
                return
        else:
            QMessageBox.warning(
                self,
                "Login Diperlukan",
                "Silakan login terlebih dahulu untuk melakukan pembelian."
            )
            return
        
        # Buat daftar item untuk konfirmasi
        item_list = ""
        item_descriptions = []
        for (item, quantity) in self.cart_items.values():
            subtotal = item['price'] * quantity
            item_str = f"{quantity}x {item['name']} (Rp {subtotal:,})".replace(',', '.')
            item_list += f"- {item_str}\n"
            item_descriptions.append(item_str)
        
        # Konfirmasi pemesanan
        confirm = QMessageBox.question(
            self,
            "Konfirmasi Pemesanan",
            f"Anda akan memesan item berikut:\n\n{item_list}\nTotal: Rp {total_price:,}\n\nLanjutkan pembayaran?".replace(',', '.'),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if confirm == QMessageBox.Yes:
            # Proses pembayaran
            try:
                success, message, new_saldo = UserModel.update_saldo(
                    self.user_data['username'], 
                    -total_price  # Kurangi saldo
                )
                
                if success:
                    # Siapkan data order
                    order_data = {
                        'items': [(item, quantity) for (item, quantity) in self.cart_items.values()],
                        'total_price': total_price,
                        'order_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    
                    # Update user data dengan saldo baru
                    if isinstance(new_saldo, (int, float)):
                        self.user_data['saldo'] = new_saldo
                    
                    # Tampilkan pesan sukses
                    QMessageBox.information(
                        self,
                        "Pemesanan Berhasil",
                        f"Pesanan Anda telah berhasil. Pembayaran sebesar Rp {total_price:,} telah diproses.\nSaldo Anda sekarang: Rp {new_saldo:,}".replace(',', '.')
                    )
                    
                    # Reset keranjang
                    self.clear_cart()
                    
                    # Emit signal bahwa order selesai
                    self.order_completed.emit(order_data)
                else:
                    # Jika gagal update saldo
                    QMessageBox.critical(self, "Pembayaran Gagal", message)
            except Exception as e:
                # Tangani kesalahan apa pun yang mungkin terjadi
                error_message = f"Error saat memproses pembayaran: {str(e)}"
                print(error_message)
                QMessageBox.critical(self, "Error Pembayaran", error_message)
    
    def clear_cart(self):
        """Kosongkan keranjang belanja"""
        self.cart_items = {}
        
        # Hapus semua item dari layout
        for i in reversed(range(self.cart_layout.count())):
            widget = self.cart_layout.itemAt(i).widget()
            if isinstance(widget, CartItem):
                widget.setParent(None)
        
        # Reset ringkasan
        self.update_cart_summary()
        
        # Tampilkan label keranjang kosong
        self.empty_cart_label.setVisible(True)
    
    def update_user_data(self, user_data):
        """Update data user"""
        self.user_data = user_data 