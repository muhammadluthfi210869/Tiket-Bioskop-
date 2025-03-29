from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                          QPushButton, QFrame, QScrollArea, QLineEdit,
                          QComboBox, QStackedWidget, QSizePolicy, QGraphicsDropShadowEffect)
from PyQt5.QtGui import QFont, QIcon, QColor, QPainter, QPixmap, QBrush, QPen
from PyQt5.QtCore import Qt, pyqtSignal, QSize, QDateTime
import json
import os
from datetime import datetime
import uuid

class TransactionCard(QFrame):
    """Widget untuk menampilkan item riwayat"""
    def __init__(self, transaction_data):
        super().__init__()
        self.transaction_data = transaction_data
        self.init_ui()
        
    def create_stacked_food_icons(self, items, container_size=60):
        """Membuat tampilan bertumpuk untuk item makanan"""
        if not items:
            return None
            
        # Container untuk icon makanan
        container = QFrame()
        container.setFixedSize(container_size, container_size)
        container.setStyleSheet("""
            background: transparent;
        """)
        
        # Maksimal 3 item yang ditampilkan
        max_items = min(len(items), 3)
        item_size = 40  # Ukuran setiap icon
        offset = 10     # Jarak antar icon
        
        # Layout absolute untuk penempatan icon
        container.setLayout(QVBoxLayout())
        container.layout().setContentsMargins(0, 0, 0, 0)
        
        for i in range(max_items):
            item = items[i]
            item_name = ""
            if isinstance(item, dict):
                if "name" in item and isinstance(item["name"], dict):
                    item_name = item["name"].get("name", "").lower()
                else:
                    item_name = item.get("name", "").lower()
            
            # Frame untuk setiap icon
            icon_frame = QLabel(container)
            icon_frame.setFixedSize(item_size, item_size)
            icon_frame.setStyleSheet("""
                background-color: #252525;
                border-radius: 20px;
                padding: 5px;
            """)
            
            # Cari icon yang sesuai
            icon_path = self.find_food_icon(item_name)
            if icon_path and os.path.exists(icon_path):
                pixmap = QPixmap(icon_path)
                icon_frame.setPixmap(pixmap.scaled(item_size-10, item_size-10, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            
            # Posisikan icon dengan offset
            icon_frame.move(i * offset, i * offset)
            icon_frame.raise_()
            
        return container
        
    def find_food_icon(self, food_name):
        """Mencari icon makanan berdasarkan nama"""
        if not food_name:
            return os.path.join('assets', 'icons', 'food', 'food_default.png')
            
        food_name = food_name.lower()
        print(f"Looking for icon for food: '{food_name}'")
        
        icons_folder = os.path.join('assets', 'icons', 'food')
        if not os.path.exists(icons_folder):
            os.makedirs(icons_folder, exist_ok=True)
            
        # Mapping nama makanan ke icon
        food_icons = {
            'popcorn': 'popcorn.png',
            'cheese': 'popcorn.png',  # Popcorn with cheese is still popcorn
            'caramel': 'popcorn.png', # Popcorn with caramel is still popcorn
            's': 'popcorn.png',       # Popcorn (S) small
            'm': 'popcorn.png',       # Popcorn (M) medium
            'l': 'popcorn.png',       # Popcorn (L) large
            'soda': 'soda.png',
            'cola': 'soda.png',
            'air': 'water.png',
            'mineral': 'water.png',
            'nachos': 'nachos.png',
            'hotdog': 'hotdog.png',
            'burger': 'burger.png',
            'french': 'fries.png',
            'fries': 'fries.png',
            'kentang': 'fries.png',
            'ice cream': 'ice_cream.png',
            'es krim': 'ice_cream.png'
        }
        
        # First check for direct matches
        for key, icon_name in food_icons.items():
            if key == food_name:
                icon_path = os.path.join(icons_folder, icon_name)
                print(f"Found exact match: {icon_path}")
                return icon_path
        
        # Then check for partial matches within the food name
        for key, icon_name in food_icons.items():
            if key in food_name:
                icon_path = os.path.join(icons_folder, icon_name)
                print(f"Found partial match ({key}): {icon_path}")
                return icon_path
        
        # Default food icon if no match found
        default_path = os.path.join(icons_folder, 'food_default.png')
        print(f"No match found, using default: {default_path}")
        return default_path

    def init_ui(self):
        """Inisialisasi antarmuka kartu transaksi"""
        # Set style untuk card
        self.setObjectName("transaction_card")
        self.setStyleSheet("""
            #transaction_card {
                background-color: #1A1A1A;
                border-radius: 10px;
                border: 1px solid #2A2A2A;
            }
            #transaction_card:hover {
                border: 1px solid #FFD700;
            }
        """)
        
        # Layout utama
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Icon/Poster container (kiri)
        if self.transaction_data.get("type") == "Tiket":
            # Poster untuk tiket - rectangular container
            poster_container = QFrame()
            poster_container.setFixedSize(60, 90)
            poster_container.setStyleSheet("""
                background-color: #252525;
                border-radius: 5px;
            """)
            
            poster_layout = QVBoxLayout(poster_container)
            poster_layout.setContentsMargins(0, 0, 0, 0)
            
            poster_label = QLabel()
            poster_label.setFixedSize(60, 90)
            poster_label.setScaledContents(True)
            
            movie_title = self.transaction_data.get("movie_title", "")
            if movie_title:
                poster_path = self.find_poster_for_film(movie_title)
                if poster_path and os.path.exists(poster_path):
                    pixmap = QPixmap(poster_path)
                    poster_label.setPixmap(pixmap)
                    poster_label.setStyleSheet("border-radius: 5px;")
            
            poster_layout.addWidget(poster_label)
            main_layout.addWidget(poster_container)
            
        elif self.transaction_data.get("type") == "Makanan":
            # Improved circular food icon
            items = self.transaction_data.get("items", [])
            if items:
                # Get the first food item for the icon
                item = items[0]
                item_name = ""
                
                print(f"Food item: {item}")
                
                if isinstance(item, dict):
                    if "name" in item and isinstance(item["name"], dict):
                        item_name = item["name"].get("name", "")
                        print(f"Found complex item name: {item_name}")
                    else:
                        item_name = item.get("name", "")
                        print(f"Found simple item name: {item_name}")
                elif isinstance(item, str):
                    item_name = item
                    print(f"Found string item name: {item_name}")
                
                # Create circular food icon container
                food_container = QFrame()
                food_container.setFixedSize(60, 60)
                food_container.setStyleSheet("""
                    background-color: #252525;
                    border-radius: 30px;
                    border: 1px solid #333333;
                """)
                
                food_layout = QVBoxLayout(food_container)
                food_layout.setContentsMargins(10, 10, 10, 10)
                food_layout.setAlignment(Qt.AlignCenter)
                
                food_icon = QLabel()
                food_icon.setFixedSize(40, 40)
                food_icon.setAlignment(Qt.AlignCenter)
                food_icon.setStyleSheet("background: transparent; border: none;")
                
                # Find appropriate food icon
                icon_path = self.find_food_icon(item_name)
                print(f"Icon path for {item_name}: {icon_path}")
                
                if icon_path and os.path.exists(icon_path):
                    pixmap = QPixmap(icon_path)
                    food_icon.setPixmap(pixmap.scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                    print(f"Set pixmap from {icon_path}")
                else:
                    print(f"Icon path not found: {icon_path}")
                    # Create a text label as fallback
                    if item_name:
                        first_letter = item_name[0].upper() if item_name else "F"
                        food_icon.setText(first_letter)
                        food_icon.setStyleSheet("""
                            background-color: #FFD700;
                            color: #000000;
                            border-radius: 20px;
                            font-size: 20px;
                            font-weight: bold;
                            text-align: center;
                        """)
                
                food_layout.addWidget(food_icon)
                main_layout.addWidget(food_container)
            else:
                # Fallback if no items
                default_container = QFrame()
                default_container.setFixedSize(60, 60)
                default_container.setStyleSheet("""
                    background-color: #252525;
                    border-radius: 30px;
                """)
                main_layout.addWidget(default_container)
        
        else:  # Top Up - show specific bank icon
            # Get payment method from transaction data
            payment_method = self.transaction_data.get("payment_method", "").lower()
            
            # Create circular bank icon container
            icon_container = QFrame()
            icon_container.setFixedSize(60, 60)
            icon_container.setStyleSheet("""
                background-color: #252525;
                border-radius: 30px;
            """)
            
            icon_layout = QVBoxLayout(icon_container)
            icon_layout.setContentsMargins(10, 10, 10, 10)
            icon_layout.setAlignment(Qt.AlignCenter)
            
            icon_label = QLabel()
            icon_label.setFixedSize(40, 40)
            icon_label.setAlignment(Qt.AlignCenter)
            
            # Choose bank icon based on payment method
            bank_icon_path = None
            if "bca" in payment_method:
                bank_icon_path = os.path.join("assets", "icons", "banks", "bca.png")
            elif "bni" in payment_method:
                bank_icon_path = os.path.join("assets", "icons", "banks", "bni.png")
            elif "mandiri" in payment_method:
                bank_icon_path = os.path.join("assets", "icons", "banks", "mandiri.png")
            elif "bri" in payment_method:
                bank_icon_path = os.path.join("assets", "icons", "banks", "bri.png")
            
            # Fallback to generic bank icon if specific bank not found
            if not bank_icon_path or not os.path.exists(bank_icon_path):
                bank_icon_path = os.path.join("assets", "icons", "bank.png")
            
            if os.path.exists(bank_icon_path):
                icon_pixmap = QPixmap(bank_icon_path)
                icon_label.setPixmap(icon_pixmap.scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            
            icon_layout.addWidget(icon_label)
            main_layout.addWidget(icon_container)
        
        # Content container (tengah)
        content_container = QFrame()
        content_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        
        content_layout = QVBoxLayout(content_container)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(5)
        
        # Header dengan timestamp
        header_layout = QHBoxLayout()
        
        transaction_type_label = QLabel(self.transaction_data.get("type", ""))
        transaction_type_label.setStyleSheet("""
            color: #FFD700;
            font-weight: bold;
            font-size: 16px;
            font-family: 'Poppins';
        """)
        
        timestamp_label = QLabel(self.transaction_data.get("timestamp", ""))
        timestamp_label.setStyleSheet("""
            color: #808080;
            font-size: 12px;
            font-family: 'Poppins';
        """)
        
        header_layout.addWidget(transaction_type_label)
        header_layout.addStretch()
        header_layout.addWidget(timestamp_label)
        
        content_layout.addLayout(header_layout)
        
        # Process different transaction types
        if self.transaction_data.get("type") == "Tiket":
            # Movie title
            movie_title = QLabel(self.transaction_data.get("movie_title", ""))
            movie_title.setStyleSheet("color: #FFFFFF; font-weight: bold; font-size: 14px; font-family: 'Poppins';")
            content_layout.addWidget(movie_title)
            
            # Cinema and seats info
            cinema_info = QLabel(f"{self.transaction_data.get('cinema', '')} - {self.transaction_data.get('studio_type', '')}")
            cinema_info.setStyleSheet("color: #CCCCCC; font-size: 13px; font-family: 'Poppins';")
            content_layout.addWidget(cinema_info)
            
            seats_info = QLabel(f"Kursi: {', '.join(self.transaction_data.get('seats', []))}")
            seats_info.setStyleSheet("color: #CCCCCC; font-size: 13px; font-family: 'Poppins';")
            content_layout.addWidget(seats_info)
            
            # Show date and time
            datetime_info = QLabel(f"Jadwal: {self.transaction_data.get('show_date', '')} {self.transaction_data.get('show_time', '')}")
            datetime_info.setStyleSheet("color: #CCCCCC; font-size: 13px; font-family: 'Poppins';")
            content_layout.addWidget(datetime_info)
            
        elif self.transaction_data.get("type") == "Makanan":
            # Food items with detailed information
            items = self.transaction_data.get("items", [])
            total_price = 0
            
            for item in items:
                item_name = ""
                price = 0
                quantity = 0
                
                if isinstance(item, dict):
                    if "name" in item and isinstance(item["name"], dict):
                        product = item["name"]
                        item_name = product.get("name", "Unknown")
                        price = product.get("price", 0)
                        quantity = item.get("quantity", 1)
                    else:
                        item_name = item.get("name", "Unknown")
                        quantity = item.get("quantity", 1)
                        price = item.get("price", 0)
                
                total_price += price * quantity
                
                # Create item info
                item_info = QLabel(f"{item_name} x{quantity} - Rp {price * quantity:,}".replace(",", "."))
                item_info.setStyleSheet("color: #CCCCCC; font-size: 13px; font-family: 'Poppins';")
                content_layout.addWidget(item_info)
            
            # Update total in transaction data if not set
            if self.transaction_data.get("total", 0) == 0:
                self.transaction_data["total"] = -total_price
            
        else:  # Top Up
            amount = self.transaction_data.get("total", 0)
            amount_text = f"Rp {abs(amount):,}".replace(',', '.')
            amount_label = QLabel(f"Nominal Top Up: {amount_text}")
            amount_label.setStyleSheet("color: #FFFFFF; font-size: 14px; font-family: 'Poppins';")
            content_layout.addWidget(amount_label)
        
        # Status container (kanan)
        status_container = QFrame()
        status_container.setFixedWidth(150)
        
        status_layout = QVBoxLayout(status_container)
        status_layout.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        
        # Total amount
        total = self.transaction_data.get("total", 0)
        if total == 0 and self.transaction_data.get("type") == "Tiket":
            # Jika total 0 untuk tiket, ambil harga dari ticket_price
            total = -self.transaction_data.get("ticket_price", 0)
            self.transaction_data["total"] = total
        
        total_text = f"Rp {abs(total):,}".replace(',', '.')
        if total > 0:
            total_text = f"+{total_text}"
            total_color = "#4CAF50"  # Hijau untuk nilai positif
        else:
            total_text = f"-{total_text}"
            total_color = "#F44336"  # Merah untuk nilai negatif
        
        total_label = QLabel(total_text)
        total_label.setStyleSheet(f"""
            color: {total_color};
            font-weight: bold;
            font-size: 16px;
            font-family: 'Poppins';
        """)
        total_label.setAlignment(Qt.AlignRight)
        
        # Status label
        status_label = QLabel(self.transaction_data.get("status", ""))
        status_label.setStyleSheet("""
            color: #00C853;
            font-size: 12px;
            font-family: 'Poppins';
        """)
        status_label.setAlignment(Qt.AlignRight)
        
        status_layout.addWidget(total_label)
        status_layout.addWidget(status_label)
        
        # Add containers to main layout
        main_layout.addWidget(content_container)
        main_layout.addWidget(status_container)
        
    def find_poster_for_film(self, title):
        """Mencari poster film berdasarkan judul"""
        # Path ke folder assets/posters
        posters_folder = os.path.join('assets', 'posters')
        if not os.path.exists(posters_folder):
            posters_folder = 'assets'
        
        # Normalisasi judul untuk pencarian file
        normalized_title = title.lower().replace(' ', '_').replace(':', '').replace('-', '_')
        
        # Cek semua file di folder posters
        for filename in os.listdir(posters_folder):
            # Jika nama file mengandung judul film
            file_lower = filename.lower()
            if normalized_title in file_lower or title.lower().replace(' ', '') in file_lower:
                return os.path.join(posters_folder, filename)
        
        # Jika tidak menemukan kecocokan persis, coba dengan sebagian judul
        for filename in os.listdir(posters_folder):
            file_lower = filename.lower()
            words = title.lower().split()
            for word in words:
                if len(word) > 3 and word in file_lower:  # Cari kata dengan panjang >3 karakter
                    return os.path.join(posters_folder, filename)
        
        return None

class HistoryPage(QWidget):
    """Halaman untuk menampilkan riwayat transaksi"""
    def __init__(self, user_data):
        super().__init__()
        self.user_data = user_data
        self.transactions = []
        self.init_ui()
        self.ensure_bank_icons_directory()
        self.ensure_food_icons_directory()
        self.load_history()
        
    def init_ui(self):
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(20)
        
        # Header section
        header_container = QWidget()
        header_layout = QHBoxLayout(header_container)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        # Title with icon
        title_container = QHBoxLayout()
        title_icon = QLabel()
        icon_path = os.path.join("assets", "icons", "history.png")
        if os.path.exists(icon_path):
            title_icon.setPixmap(QIcon(icon_path).pixmap(QSize(32, 32)))
        
        title = QLabel("Riwayat Transaksi")
        title.setStyleSheet("""
            QLabel {
                color: #FFFFFF;
                font-size: 28px;
                font-weight: 600;
                font-family: 'Poppins';
            }
        """)
        
        title_container.addWidget(title_icon)
        title_container.addWidget(title)
        title_container.addStretch()
        
        # Filter and search section
        filter_search_container = QWidget()
        filter_search_layout = QHBoxLayout(filter_search_container)
        filter_search_layout.setContentsMargins(0, 0, 0, 0)
        filter_search_layout.setSpacing(20)
        
        # Filter combo
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["Semua", "Tiket", "Makanan", "Top Up"])
        self.filter_combo.setStyleSheet("""
            QComboBox {
                background-color: #1F1F1F;
                color: #FFFFFF;
                border: 1px solid #333333;
                border-radius: 8px;
                padding: 8px 12px;
                min-width: 150px;
                font-family: 'Montserrat';
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: url(assets/icons/dropdown.png);
                width: 12px;
                height: 12px;
            }
            QComboBox QAbstractItemView {
                background-color: #1F1F1F;
                color: #FFFFFF;
                selection-background-color: #333333;
                border: 1px solid #333333;
            }
        """)
        self.filter_combo.currentTextChanged.connect(self.filter_transactions)
        
        # Search input
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Cari transaksi...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                background-color: #1F1F1F;
                color: #FFFFFF;
                border: 1px solid #333333;
                border-radius: 8px;
                padding: 8px 12px;
                font-family: 'Montserrat';
            }
            QLineEdit::placeholder {
                color: #888888;
            }
        """)
        self.search_input.textChanged.connect(self.filter_transactions)
        
        filter_search_layout.addWidget(self.filter_combo)
        filter_search_layout.addWidget(self.search_input)
        filter_search_layout.addStretch()
        
        # Add header components to header layout
        header_layout.addLayout(title_container)
        header_layout.addWidget(filter_search_container)
        
        # Transactions container
        transactions_container = QWidget()
        transactions_container.setStyleSheet("""
            QWidget {
                background-color: #1A1A1A;
                border-radius: 12px;
            }
        """)
        
        # Transactions scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                border: none;
                background-color: #1F1F1F;
                width: 8px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background-color: #333333;
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
        """)
        
        # Transactions content widget
        transactions_widget = QWidget()
        self.transactions_layout = QVBoxLayout(transactions_widget)
        self.transactions_layout.setContentsMargins(20, 20, 20, 20)
        self.transactions_layout.setSpacing(12)
        self.transactions_layout.setAlignment(Qt.AlignTop)
        
        scroll_area.setWidget(transactions_widget)
        
        # Add scroll area to transactions container
        transactions_layout = QVBoxLayout(transactions_container)
        transactions_layout.setContentsMargins(0, 0, 0, 0)
        transactions_layout.addWidget(scroll_area)
        
        # Add all components to main layout
        main_layout.addWidget(header_container)
        main_layout.addWidget(transactions_container)
    
    def add_transaction(self, transaction_data):
        """Menambahkan transaksi baru ke history"""
        # Add timestamp if not present
        if "timestamp" not in transaction_data:
            transaction_data["timestamp"] = QDateTime.currentDateTime().toString("dd/MM/yyyy HH:mm")
        
        # Generate unique transaction ID if not present
        if "transaction_id" not in transaction_data:
            transaction_data["transaction_id"] = str(uuid.uuid4())
        
        # Check for duplicates using more specific criteria
        is_duplicate = False
        for existing_transaction in self.transactions:
            # For tickets, check specific ticket details
            if transaction_data["type"] == "Tiket" and existing_transaction.get("type") == "Tiket":
                if (existing_transaction.get("movie_title") == transaction_data.get("movie_title") and
                    existing_transaction.get("show_date") == transaction_data.get("show_date") and
                    existing_transaction.get("show_time") == transaction_data.get("show_time") and
                    existing_transaction.get("seats") == transaction_data.get("seats") and
                    existing_transaction.get("timestamp") == transaction_data.get("timestamp")):
                    is_duplicate = True
                    break
            # For food orders, check more than just transaction_id
            elif transaction_data["type"] == "Makanan" and existing_transaction.get("type") == "Makanan":
                # Check timestamp - if it's the same timestamp, it's likely a duplicate
                if existing_transaction.get("timestamp") == transaction_data.get("timestamp"):
                    # Also check total to be extra sure
                    if existing_transaction.get("total") == transaction_data.get("total"):
                        is_duplicate = True
                        break
                # Also check transaction_id if it exists
                elif transaction_data.get("transaction_id") and transaction_data["transaction_id"] == existing_transaction.get("transaction_id"):
                    is_duplicate = True
                    break
            # For other transactions, use transaction_id if available
            elif transaction_data.get("transaction_id"):
                if transaction_data["transaction_id"] == existing_transaction.get("transaction_id"):
                    is_duplicate = True
                    break
        
        # Only add if not a duplicate
        if not is_duplicate:
            # Add to transactions list
            self.transactions.insert(0, transaction_data)
            # Save to file
            self.save_history()
            # Refresh display
            self.filter_transactions()
            print(f"Added new transaction of type: {transaction_data.get('type')}")
        else:
            print(f"Skipped duplicate transaction of type: {transaction_data.get('type')}")
    
    def load_history(self):
        """Muat data riwayat dari penyimpanan"""
        if not self.user_data or 'username' not in self.user_data:
            return
            
        # Path file riwayat
        history_file = os.path.join("data", "history", f"{self.user_data['username']}.json")
        
        try:
            if os.path.exists(history_file):
                with open(history_file, 'r') as f:
                    self.transactions = json.load(f)
                    
                    # Process the loaded transactions to ensure they have a consistent format
                    for i, transaction in enumerate(self.transactions):
                        # Fix the old format where items is a list of lists instead of dictionaries
                        if isinstance(transaction, dict) and "items" in transaction:
                            if isinstance(transaction["items"], list):
                                # Check if the items list contains lists instead of dicts
                                for j, item in enumerate(transaction["items"]):
                                    if isinstance(item, list):
                                        # Convert [product_dict, quantity] to the new format
                                        product = item[0]
                                        quantity = item[1]
                                        self.transactions[i]["items"][j] = {
                                            "name": product,
                                            "quantity": quantity,
                                            "price": product.get("price", 0) * quantity 
                                        }
                        
                        # Fix dates in old format
                        if isinstance(transaction, dict) and "date" in transaction and "timestamp" not in transaction:
                            self.transactions[i]["timestamp"] = transaction["date"]
                    
                    self.filter_transactions()
        except Exception as e:
            print(f"Error loading history: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def save_history(self):
        """Simpan data riwayat ke penyimpanan"""
        if not self.user_data or 'username' not in self.user_data:
            return
            
        # Buat direktori jika belum ada
        os.makedirs(os.path.join("data", "history"), exist_ok=True)
        
        # Path file riwayat
        history_file = os.path.join("data", "history", f"{self.user_data['username']}.json")
        
        try:
            with open(history_file, 'w') as f:
                json.dump(self.transactions, f, indent=4)
        except Exception as e:
            print(f"Error saving history: {str(e)}")
    
    def filter_transactions(self):
        """Filter transaksi berdasarkan tipe dan pencarian"""
        print("Filtering transactions...")  # Debug print
        print(f"Current filter: {self.filter_combo.currentText()}")  # Debug print
        print(f"Search text: {self.search_input.text()}")  # Debug print
        
        # Clear current transactions
        while self.transactions_layout.count():
            item = self.transactions_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Get filter criteria
        filter_type = self.filter_combo.currentText()
        search_text = self.search_input.text().lower()
        
        print(f"Total transactions: {len(self.transactions)}")  # Debug print
        
        # Show empty state if no transactions
        if not self.transactions:
            self._show_empty_state("Tidak ada riwayat transaksi")
            return
        
        # Filter and add transactions
        has_visible_transactions = False
        for transaction in self.transactions:
            print(f"Processing transaction: {transaction}")  # Debug print
            
            show_transaction = True
            
            # Check type filter
            if filter_type != "Semua":
                transaction_type = transaction.get("type", "")
                if filter_type == "Tiket" and transaction_type != "Tiket":
                    show_transaction = False
                elif filter_type == "Makanan" and transaction_type != "Makanan":
                    show_transaction = False
                elif filter_type == "Top Up" and transaction_type != "Top Up":
                    show_transaction = False
            
            # Check search text
            if search_text and show_transaction:
                search_found = False
                # Search in relevant fields
                searchable_fields = ["movie_title", "type", "status", "cinema", "studio", "seats", "show_date", "show_time"]
                for field in searchable_fields:
                    if isinstance(transaction, dict):
                        value = str(transaction.get(field, "")).lower()
                        if search_text in value:
                            search_found = True
                            break
                    # If items is a list, handle it differently
                    elif isinstance(transaction, list):
                        # Skip searching in lists for now
                        search_found = True
                        break
                if not search_found:
                    show_transaction = False
            
            if show_transaction:
                print(f"Showing transaction: {transaction}")  # Debug print
                has_visible_transactions = True
                card = TransactionCard(transaction)
                self.transactions_layout.addWidget(card)
        
        # Show empty state if no transactions match filter
        if not has_visible_transactions:
            if filter_type == "Tiket":
                self._show_empty_state("Tidak ada riwayat pembelian tiket")
            elif filter_type == "Makanan":
                self._show_empty_state("Tidak ada riwayat pembelian makanan")
            elif filter_type == "Top Up":
                self._show_empty_state("Tidak ada riwayat pengisian saldo")
            else:
                self._show_empty_state("Tidak ada transaksi yang sesuai dengan filter")
        
        # Add stretch at the end
        self.transactions_layout.addStretch()
    
    def _show_empty_state(self, message):
        """Menampilkan pesan ketika tidak ada transaksi"""
        empty_widget = QWidget()
        empty_layout = QVBoxLayout(empty_widget)
        empty_layout.setAlignment(Qt.AlignCenter)
        
        empty_icon = QLabel()
        icon_path = os.path.join("assets", "icons", "empty.png")
        if os.path.exists(icon_path):
            empty_icon.setPixmap(QIcon(icon_path).pixmap(QSize(64, 64)))
        empty_icon.setAlignment(Qt.AlignCenter)
        
        empty_text = QLabel(message)
        empty_text.setStyleSheet("""
            color: #888888;
            font-size: 16px;
            font-family: 'Montserrat';
        """)
        empty_text.setAlignment(Qt.AlignCenter)
        
        empty_layout.addWidget(empty_icon)
        empty_layout.addWidget(empty_text)
        
        self.transactions_layout.addWidget(empty_widget)
    
    def update_user_data(self, user_data):
        """Update data user dan muat ulang riwayat"""
        self.user_data = user_data
        self.load_history()
    
    def ensure_bank_icons_directory(self):
        """Memastikan direktori untuk ikon bank tersedia"""
        banks_dir = os.path.join("assets", "icons", "banks")
        if not os.path.exists(banks_dir):
            try:
                os.makedirs(banks_dir, exist_ok=True)
                print(f"Created banks directory at: {banks_dir}")
            except Exception as e:
                print(f"Error creating banks directory: {e}")
                
        # Create generic bank icons if they don't exist
        sample_banks = {
            "bca.png": (0, 106, 206),  # Blue
            "bni.png": (255, 91, 0),   # Orange
            "mandiri.png": (0, 120, 160),  # Blue-green
            "bri.png": (0, 149, 218)   # Light blue
        }
        
        for bank_file, color in sample_banks.items():
            bank_path = os.path.join(banks_dir, bank_file)
            if not os.path.exists(bank_path):
                self.create_generic_bank_icon(bank_path, color)

    def create_generic_bank_icon(self, path, color):
        """Membuat ikon bank generik dengan inisial bank"""
        try:
            # Create a 100x100 transparent pixmap
            pixmap = QPixmap(100, 100)
            pixmap.fill(Qt.transparent)
            
            # Create painter
            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.Antialiasing)
            
            # Draw circular background
            painter.setBrush(QBrush(QColor(*color)))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(0, 0, 100, 100)
            
            # Draw bank name
            bank_name = os.path.basename(path).split('.')[0].upper()
            painter.setPen(QPen(QColor(255, 255, 255)))
            font = QFont("Arial", 36, QFont.Bold)
            painter.setFont(font)
            painter.drawText(pixmap.rect(), Qt.AlignCenter, bank_name)
            
            painter.end()
            
            # Save the pixmap
            pixmap.save(path)
            print(f"Created generic bank icon at: {path}")
        except Exception as e:
            print(f"Error creating generic bank icon: {e}")
            import traceback
            traceback.print_exc()

    def ensure_food_icons_directory(self):
        """Memastikan direktori untuk ikon makanan tersedia"""
        food_dir = os.path.join("assets", "icons", "food")
        if not os.path.exists(food_dir):
            try:
                os.makedirs(food_dir, exist_ok=True)
                print(f"Created food icons directory at: {food_dir}")
            except Exception as e:
                print(f"Error creating food icons directory: {e}")
                
        # Create generic food icons if they don't exist
        sample_foods = {
            "popcorn.png": (255, 204, 0),  # Yellow for popcorn
            "soda.png": (180, 0, 0),       # Red for soda/drinks
            "hotdog.png": (180, 90, 0),    # Brown for hotdog
            "nachos.png": (230, 180, 0),   # Orange for nachos
            "burger.png": (130, 70, 0),    # Brown for burger
            "fries.png": (230, 180, 0),    # Golden for fries
            "water.png": (0, 140, 200),    # Blue for water
            "ice_cream.png": (240, 240, 240),  # White for ice cream
            "food_default.png": (100, 180, 100)  # Green for default
        }
        
        for food_file, color in sample_foods.items():
            food_path = os.path.join(food_dir, food_file)
            if not os.path.exists(food_path):
                self.create_generic_food_icon(food_path, color)

    def create_generic_food_icon(self, path, color):
        """Membuat ikon makanan generik"""
        try:
            # Create a 100x100 transparent pixmap
            pixmap = QPixmap(100, 100)
            pixmap.fill(Qt.transparent)
            
            # Create painter
            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.Antialiasing)
            
            # Draw circular background
            painter.setBrush(QBrush(QColor(*color)))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(0, 0, 100, 100)
            
            # Draw food name
            food_name = os.path.basename(path).split('.')[0].upper()
            painter.setPen(QPen(QColor(255, 255, 255)))
            font = QFont("Arial", 14, QFont.Bold)
            painter.setFont(font)
            painter.drawText(pixmap.rect(), Qt.AlignCenter, food_name)
            
            painter.end()
            
            # Save the pixmap
            pixmap.save(path)
            print(f"Created generic food icon at: {path}")
        except Exception as e:
            print(f"Error creating generic food icon: {e}")
            import traceback
            traceback.print_exc() 