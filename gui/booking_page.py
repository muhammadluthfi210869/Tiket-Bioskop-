from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                          QPushButton, QFrame, QGridLayout, QLineEdit, QComboBox,
                          QButtonGroup, QRadioButton, QScrollArea, QMessageBox, QSpacerItem,
                          QSizePolicy, QGroupBox)
from PyQt5.QtGui import QFont, QPixmap, QIcon, QColor, QPalette
from PyQt5.QtCore import Qt, pyqtSignal, QSize, QDateTime, QDate
import os
import json
from models import UserModel
from utils.helper import find_poster_for_film
from utils.dialog_styles import setup_message_box

# Data bioskop per kota
CINEMA_DATA = {
    "Jakarta": [
        "CGV Grand Indonesia",
        "XXI Plaza Indonesia",
        "XXI Kota Kasablanka",
        "CGV Central Park",
        "Cinema 21 Mall Taman Anggrek"
    ],
    "Bandung": [
        "CGV Paris Van Java",
        "XXI Cihampelas Walk",
        "CGV BEC Mall",
        "XXI Trans Studio Mall",
        "Cinema 21 Bandung Trade Center"
    ],
    "Surabaya": [
        "CGV Tunjungan Plaza",
        "XXI Pakuwon Mall",
        "Cinema 21 Grand City",
        "XXI Royal Plaza",
        "CGV Marvell City"
    ],
    "Yogyakarta": [
        "CGV Hartono Mall",
        "XXI Ambarrukmo Plaza",
        "CGV J-Walk",
        "XXI Sleman City Hall",
        "Cinema 21 Jogja City Mall"
    ],
    "Bali": [
        "XXI Beachwalk",
        "CGV Plaza Renon",
        "XXI Park 23",
        "XXI Level 21",
        "Cinema 21 Galeria Bali"
    ]
}

# Daftar teater
THEATER_NUMBERS = ["Teater 1", "Teater 2", "Teater 3", "Teater 4", "Teater 5"]

class SeatButton(QPushButton):
    """Custom button untuk pemilihan kursi"""
    def __init__(self, row, col):
        super().__init__()
        self.row = row
        self.col = col
        self.is_selected = False
        self.is_booked = False  # Untuk kursi yang sudah dipesan
        
        # Set tampilan awal
        self.setFixedSize(40, 40)
        self.setText(f"{chr(65+row)}{col+1}")  # Contoh: A1, B2, dst
        self.setCursor(Qt.PointingHandCursor)
        self.setFont(QFont("Montserrat", 10, QFont.Bold))
        self.update_style()
        
    def update_style(self):
        """Update tampilan button berdasarkan status"""
        base_style = """
            QPushButton {
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                font-family: 'Montserrat';
                font-size: 10pt;
                text-align: center;
                padding: 2px;
                margin: 2px;
            }
            QPushButton:hover {
                font-size: 11pt;
                margin: 0px;
            }
        """
        
        if self.is_booked:
            # Kursi sudah dipesan
            self.setStyleSheet(base_style + """
                QPushButton {
                    background-color: #666666;
                    color: white;
                }
                QPushButton:hover {
                    background-color: #666666;
                }
            """)
            self.setEnabled(False)
        elif self.is_selected:
            # Kursi dipilih
            self.setStyleSheet(base_style + """
                QPushButton {
                    background-color: #FFD700;
                    color: black;
                }
                QPushButton:hover {
                    background-color: #F5CB0C;
                }
            """)
        else:
            # Kursi tersedia
            self.setStyleSheet(base_style + """
                QPushButton {
                    background-color: #28a745;
                    color: white;
                }
                QPushButton:hover {
                    background-color: #218838;
                }
            """)
    
    def toggle_selection(self):
        """Toggle status pemilihan kursi"""
        if not self.is_booked:
            self.is_selected = not self.is_selected
            self.update_style()

class BookingPage(QWidget):
    """Halaman untuk pemesanan tiket bioskop"""
    
    back_to_detail = pyqtSignal()
    booking_confirmed = pyqtSignal(dict)
    payment_processed = pyqtSignal(dict)  # Signal baru untuk menandakan pembayaran berhasil
    
    def __init__(self, user_data=None):
        super().__init__()
        self.user_data = user_data
        self.movie_data = None
        self.selected_seats = []
        self.total_price = 0
        self.init_ui()
        
    def init_ui(self):
        # Layout utama
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(30)
        
        # Header dengan tombol kembali
        header_layout = QHBoxLayout()
        
        # Tombol kembali
        self.back_button = QPushButton("← Kembali ke Detail Film")
        self.back_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #FFFFFF;
                border: none;
                font-weight: bold;
                font-family: 'Montserrat';
                font-size: 14px;
                text-align: left;
                padding: 8px 0;
            }
            QPushButton:hover {
                color: #FFD700;
            }
        """)
        self.back_button.setCursor(Qt.PointingHandCursor)
        self.back_button.clicked.connect(self.on_back_clicked)
        
        # Judul halaman
        title_label = QLabel("Pemesanan Tiket")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                color: #FFFFFF;
                font-size: 24px;
                font-weight: bold;
                font-family: 'Montserrat';
            }
        """)
        
        header_layout.addWidget(self.back_button)
        header_layout.addStretch()
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        main_layout.addLayout(header_layout)
        
        # Scroll Area untuk konten
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: transparent;
                border: none;
            }
            QScrollBar:vertical {
                background-color: #2D2D2D;
                width: 12px;
            }
            QScrollBar::handle:vertical {
                background-color: #404040;
                border-radius: 6px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        # Container untuk konten
        content_container = QWidget()
        content_container.setObjectName("content_container")
        content_container.setStyleSheet("""
            #content_container {
                background-color: #2D2D2D;
                border-radius: 10px;
            }
            QLabel {
                color: #FFFFFF;
                font-family: 'Montserrat';
            }
            QComboBox {
                background-color: #404040;
                color: #FFFFFF;
                border: 1px solid #505050;
                border-radius: 5px;
                padding: 8px;
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
                background-color: #404040;
                color: #FFFFFF;
                selection-background-color: #505050;
                selection-color: #FFFFFF;
            }
        """)
        
        content_layout = QVBoxLayout(content_container)
        content_layout.setContentsMargins(30, 30, 30, 30)
        content_layout.setSpacing(20)
        
        # Film info
        movie_info = QHBoxLayout()
        
        self.poster_label = QLabel()
        self.poster_label.setFixedSize(200, 300)
        self.poster_label.setStyleSheet("background-color: #1E1E1E; border-radius: 5px;")
        movie_info.addWidget(self.poster_label)
        
        movie_details = QVBoxLayout()
        movie_details.setSpacing(10)
        
        self.title_label = QLabel()
        self.title_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        
        self.info_label = QLabel()
        self.info_label.setStyleSheet("color: #CCCCCC;")
        
        movie_details.addWidget(self.title_label)
        movie_details.addWidget(self.info_label)
        movie_details.addStretch()
        
        movie_info.addLayout(movie_details)
        content_layout.addLayout(movie_info)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet("background-color: #404040;")
        content_layout.addWidget(separator)
        
        # Booking form
        form_layout = QGridLayout()
        form_layout.setVerticalSpacing(15)
        form_layout.setHorizontalSpacing(30)
        
        # Kota
        city_label = QLabel("Kota:")
        self.city_combo = QComboBox()
        self.city_combo.addItems(list(CINEMA_DATA.keys()))
        self.city_combo.currentTextChanged.connect(self.on_city_changed)
        form_layout.addWidget(city_label, 0, 0)
        form_layout.addWidget(self.city_combo, 0, 1)
        
        # Bioskop
        cinema_label = QLabel("Bioskop:")
        self.cinema_combo = QComboBox()
        self.cinema_combo.currentTextChanged.connect(self.on_cinema_changed)
        form_layout.addWidget(cinema_label, 1, 0)
        form_layout.addWidget(self.cinema_combo, 1, 1)
        
        # Theater
        theater_label = QLabel("Theater:")
        self.theater_combo = QComboBox()
        self.theater_combo.addItems(THEATER_NUMBERS)
        form_layout.addWidget(theater_label, 2, 0)
        form_layout.addWidget(self.theater_combo, 2, 1)
        
        # Jadwal
        schedule_label = QLabel("Jadwal:")
        self.schedule_combo = QComboBox()
        form_layout.addWidget(schedule_label, 3, 0)
        form_layout.addWidget(self.schedule_combo, 3, 1)
        
        # Waktu
        time_label = QLabel("Waktu:")
        self.time_combo = QComboBox()
        self.time_combo.addItems(["10:00", "13:00", "16:00", "19:00", "21:00"])
        form_layout.addWidget(time_label, 4, 0)
        form_layout.addWidget(self.time_combo, 4, 1)
        
        # Tipe Studio
        studio_label = QLabel("Tipe Studio:")
        self.studio_combo = QComboBox()
        self.studio_combo.addItems(["Regular", "VIP"])
        self.studio_combo.currentTextChanged.connect(self.on_studio_changed)
        form_layout.addWidget(studio_label, 5, 0)
        form_layout.addWidget(self.studio_combo, 5, 1)
        
        content_layout.addLayout(form_layout)
        
        # Separator
        separator2 = QFrame()
        separator2.setFrameShape(QFrame.HLine)
        separator2.setStyleSheet("background-color: #404040;")
        content_layout.addWidget(separator2)
        
        # Seat Selection Section
        seat_section = QVBoxLayout()
        
        # Screen
        screen_label = QLabel("LAYAR")
        screen_label.setAlignment(Qt.AlignCenter)
        screen_label.setStyleSheet("""
            QLabel {
                background-color: #404040;
                color: #FFFFFF;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
        """)
        seat_section.addWidget(screen_label)
        seat_section.addSpacing(30)
        
        # Seat Grid
        self.seat_grid = QGridLayout()
        self.seat_grid.setSpacing(5)
        
        # Create 10x10 seat grid
        self.seat_buttons = []
        for row in range(10):
            row_buttons = []
            for col in range(10):
                seat = SeatButton(row, col)
                seat.clicked.connect(self.on_seat_clicked)
                self.seat_grid.addWidget(seat, row, col)
                row_buttons.append(seat)
            self.seat_buttons.append(row_buttons)
        
        seat_section.addLayout(self.seat_grid)
        seat_section.addSpacing(20)
        
        # Legend
        legend_layout = QHBoxLayout()
        legend_layout.setSpacing(20)
        
        # Available
        available_layout = QHBoxLayout()
        available_box = QLabel("A1")
        available_box.setFixedSize(30, 30)
        available_box.setAlignment(Qt.AlignCenter)
        available_box.setStyleSheet("""
            QLabel {
                background-color: #28a745;
                color: white;
                border-radius: 3px;
                font-family: 'Montserrat';
                font-weight: bold;
                font-size: 10pt;
            }
        """)
        available_text = QLabel("Tersedia")
        available_text.setStyleSheet("color: #FFFFFF; font-family: 'Montserrat';")
        available_layout.addWidget(available_box)
        available_layout.addWidget(available_text)
        
        # Selected
        selected_layout = QHBoxLayout()
        selected_box = QLabel("B2")
        selected_box.setFixedSize(30, 30)
        selected_box.setAlignment(Qt.AlignCenter)
        selected_box.setStyleSheet("""
            QLabel {
                background-color: #FFD700;
                color: black;
                border-radius: 3px;
                font-family: 'Montserrat';
                font-weight: bold;
                font-size: 10pt;
            }
        """)
        selected_text = QLabel("Dipilih")
        selected_text.setStyleSheet("color: #FFFFFF; font-family: 'Montserrat';")
        selected_layout.addWidget(selected_box)
        selected_layout.addWidget(selected_text)
        
        # Booked
        booked_layout = QHBoxLayout()
        booked_box = QLabel("C3")
        booked_box.setFixedSize(30, 30)
        booked_box.setAlignment(Qt.AlignCenter)
        booked_box.setStyleSheet("""
            QLabel {
                background-color: #666666;
                color: white;
                border-radius: 3px;
                font-family: 'Montserrat';
                font-weight: bold;
                font-size: 10pt;
            }
        """)
        booked_text = QLabel("Terpesan")
        booked_text.setStyleSheet("color: #FFFFFF; font-family: 'Montserrat';")
        booked_layout.addWidget(booked_box)
        booked_layout.addWidget(booked_text)
        
        legend_layout.addLayout(available_layout)
        legend_layout.addLayout(selected_layout)
        legend_layout.addLayout(booked_layout)
        legend_layout.addStretch()
        
        seat_section.addLayout(legend_layout)
        content_layout.addLayout(seat_section)
        
        # Separator
        separator3 = QFrame()
        separator3.setFrameShape(QFrame.HLine)
        separator3.setStyleSheet("background-color: #404040;")
        content_layout.addWidget(separator3)
        
        # Booking Summary
        summary_layout = QVBoxLayout()
        
        summary_title = QLabel("Ringkasan Pemesanan")
        summary_title.setStyleSheet("""
            QLabel {
                color: #FFFFFF;
                font-size: 18px;
                font-weight: bold;
                margin-bottom: 10px;
            }
        """)
        summary_layout.addWidget(summary_title)
        
        # Selected Seats
        seats_layout = QHBoxLayout()
        seats_label = QLabel("Kursi Dipilih:")
        self.selected_seats_label = QLabel("Belum ada kursi dipilih")
        self.selected_seats_label.setStyleSheet("color: #CCCCCC;")
        seats_layout.addWidget(seats_label)
        seats_layout.addWidget(self.selected_seats_label)
        seats_layout.addStretch()
        summary_layout.addLayout(seats_layout)
        
        # Number of Tickets
        tickets_layout = QHBoxLayout()
        tickets_label = QLabel("Jumlah Tiket:")
        self.tickets_count_label = QLabel("0")
        self.tickets_count_label.setStyleSheet("color: #CCCCCC;")
        tickets_layout.addWidget(tickets_label)
        tickets_layout.addWidget(self.tickets_count_label)
        tickets_layout.addStretch()
        summary_layout.addLayout(tickets_layout)
        
        # Total Price
        price_layout = QHBoxLayout()
        price_label = QLabel("Total Harga:")
        self.total_price_label = QLabel("Rp 0")
        self.total_price_label.setStyleSheet("""
            QLabel {
                color: #FFD700;
                font-weight: bold;
                font-size: 18px;
            }
        """)
        price_layout.addWidget(price_label)
        price_layout.addWidget(self.total_price_label)
        price_layout.addStretch()
        summary_layout.addLayout(price_layout)
        
        content_layout.addLayout(summary_layout)
        
        # Tombol konfirmasi
        self.confirm_button = QPushButton("Konfirmasi Pesanan")
        self.confirm_button.setCursor(Qt.PointingHandCursor)
        self.confirm_button.setEnabled(False)
        self.confirm_button.setStyleSheet("""
            QPushButton {
                background-color: #FFD700;
                color: #000000;
                border: none;
                border-radius: 5px;
                padding: 12px;
                font-weight: bold;
                font-family: 'Montserrat';
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #F5CB0C;
            }
            QPushButton:pressed {
                background-color: #E6C000;
            }
            QPushButton:disabled {
                background-color: #666666;
                color: #CCCCCC;
            }
        """)
        self.confirm_button.clicked.connect(self.on_confirm_clicked)
        
        content_layout.addWidget(self.confirm_button)
        
        # Set scroll area content
        scroll_area.setWidget(content_container)
        main_layout.addWidget(scroll_area)
        
        # Set window background
        self.setStyleSheet("background-color: #1E1E1E;")
        
    def setup_for_movie(self, movie_data):
        """Setup halaman booking untuk film tertentu"""
        self.movie_data = movie_data
        
        # Set poster
        poster_path = movie_data.get("poster_path")
        if poster_path and os.path.exists(poster_path):
            pixmap = QPixmap(poster_path)
            self.poster_label.setPixmap(pixmap.scaled(
                self.poster_label.width(),
                self.poster_label.height(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            ))
        
        # Set informasi film
        self.title_label.setText(movie_data["title"])
        self.info_label.setText(f"{movie_data['genre']} • {movie_data['duration']} menit")
        
        # Set jadwal
        self.schedule_combo.clear()
        if isinstance(movie_data.get("schedule"), list):
            self.schedule_combo.addItems(movie_data["schedule"])
        
        # Update cinema list based on selected city
        self.on_city_changed(self.city_combo.currentText())
        
    def on_city_changed(self, city):
        """Handler when city is changed"""
        self.cinema_combo.clear()
        cinemas = {
            "Jakarta": ["CGV Grand Indonesia", "XXI Plaza Indonesia", "CGV Pacific Place"],
            "Bandung": ["CGV Paris Van Java", "XXI Cihampelas Walk", "CGV BEC Mall"],
            "Surabaya": ["CGV Tunjungan Plaza", "XXI Galaxy Mall", "CGV Grand City"],
            "Medan": ["CGV Center Point", "XXI Sun Plaza", "CGV Ring Road"],
            "Makassar": ["CGV Trans Studio", "XXI Mall Ratu Indah", "CGV Nipah Mall"]
        }
        self.cinema_combo.addItems(cinemas.get(city, []))
        
    def on_cinema_changed(self, cinema):
        """Handler when cinema is changed"""
        self.theater_combo.clear()
        theaters = [f"Theater {i}" for i in range(1, 6)]
        self.theater_combo.addItems(theaters)
        
    def on_seat_clicked(self):
        """Handler when a seat is clicked"""
        button = self.sender()
        button.toggle_selection()
        self.update_booking_summary()
        
    def update_booking_summary(self):
        """Update booking summary information"""
        self.selected_seats = []  # Reset selected seats
        for row in range(10):
            for col in range(10):
                button = self.seat_buttons[row][col]
                if button.is_selected:
                    self.selected_seats.append(f"{chr(65+row)}{col+1}")
        
        # Update selected seats label
        if self.selected_seats:
            self.selected_seats_label.setText(", ".join(sorted(self.selected_seats)))
            self.tickets_count_label.setText(str(len(self.selected_seats)))
            
            # Calculate total price
            base_price = self.movie_data.get("price", 0)
            vip_additional = 50000 if self.studio_combo.currentText() == "VIP" else 0
            self.total_price = (base_price + vip_additional) * len(self.selected_seats)
            self.total_price_label.setText(f"Rp {self.total_price:,}".replace(',', '.'))
            
            # Enable confirm button
            self.confirm_button.setEnabled(True)
        else:
            self.selected_seats_label.setText("Belum ada kursi dipilih")
            self.tickets_count_label.setText("0")
            self.total_price_label.setText("Rp 0")
            self.total_price = 0
            self.confirm_button.setEnabled(False)
            
    def on_studio_changed(self, studio_type):
        """Handler when studio type is changed"""
        self.update_booking_summary()
        
    def on_confirm_clicked(self):
        """Handler untuk konfirmasi pemesanan"""
        if not self.selected_seats:
            msg = QMessageBox(self)
            setup_message_box(msg, 
                            "Peringatan", 
                            "Silakan pilih kursi terlebih dahulu!", 
                            icon=QMessageBox.Warning)
            msg.exec_()
            return
            
        # Get current user balance
        current_saldo = self.user_data.get('saldo', 0)
        
        if current_saldo < self.total_price:
            msg = QMessageBox(self)
            setup_message_box(msg,
                            "Saldo Tidak Mencukupi",
                            f"Saldo Anda (Rp {current_saldo:,}) tidak mencukupi untuk pembelian ini (Rp {self.total_price:,})".replace(',', '.'),
                            "Silakan top up saldo Anda terlebih dahulu.",
                            QMessageBox.Warning)
            msg.exec_()
            return
            
        # Konfirmasi pembelian
        confirm_msg = QMessageBox(self)
        setup_message_box(confirm_msg,
                         "Konfirmasi Pembelian",
                         f"Anda akan membeli {len(self.selected_seats)} tiket\nTotal: Rp {self.total_price:,}".replace(',', '.'),
                         "Lanjutkan pembelian?",
                         QMessageBox.Question)
        confirm_msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        confirm_msg.setDefaultButton(QMessageBox.No)
        
        if confirm_msg.exec_() == QMessageBox.Yes:
            # Process payment
            success, message, new_saldo = UserModel.update_saldo(
                self.user_data['username'],
                -self.total_price
            )
            
            if success:
                # Update user data
                self.user_data['saldo'] = new_saldo
                
                # Prepare ticket data
                ticket_data = {
                    "movie_title": self.movie_data["title"],
                    "cinema": self.cinema_combo.currentText(),
                    "theater": self.theater_combo.currentText(),
                    "studio_type": self.studio_combo.currentText(),
                    "seats": self.selected_seats,
                    "total_price": self.total_price,
                    "show_date": self.schedule_combo.currentText(),
                    "show_time": self.time_combo.currentText(),
                    "status": "Sukses",
                    "timestamp": QDateTime.currentDateTime().toString("dd/MM/yyyy HH:mm")
                }
                
                # Show success message
                success_msg = QMessageBox(self)
                setup_message_box(success_msg,
                                "Pembelian Berhasil",
                                "Tiket berhasil dipesan!",
                                "Anda dapat melihat detail pembelian di halaman History.",
                                QMessageBox.Information)
                success_msg.exec_()
                
                # Emit booking confirmed signal for e-ticket
                self.booking_confirmed.emit(ticket_data)
                
                # Clear any existing ticket processed flag
                if hasattr(self, '_ticket_processed'):
                    delattr(self, '_ticket_processed')
                
                # Emit payment processed signal for history and balance update
                self.payment_processed.emit({
                    "new_saldo": new_saldo,
                    "ticket_data": ticket_data
                })
                
                # Go back to movie detail
                self.back_to_detail.emit()
            else:
                # Show error message
                error_msg = QMessageBox(self)
                setup_message_box(error_msg,
                                "Pembelian Gagal",
                                "Terjadi kesalahan saat memproses pembayaran.",
                                message,
                                QMessageBox.Critical)
                error_msg.exec_()
    
    def on_back_clicked(self):
        """Handler ketika tombol kembali diklik"""
        self.back_to_detail.emit()
    
    def find_poster_for_film(self, title):
        """Mencari poster film berdasarkan judul"""
        # Path ke folder assets
        assets_folder = 'assets'
        
        # Normalisasi judul untuk pencarian file
        normalized_title = title.lower().replace(' ', '_').replace(':', '').replace('-', '_')
        
        # Cek semua file di folder assets
        for filename in os.listdir(assets_folder):
            # Jika nama file mengandung judul film
            file_lower = filename.lower()
            if normalized_title in file_lower or title.lower().replace(' ', '') in file_lower:
                return os.path.join(assets_folder, filename)
        
        # Jika tidak menemukan kecocokan persis, coba dengan sebagian judul
        for filename in os.listdir(assets_folder):
            file_lower = filename.lower()
            words = title.lower().split()
            for word in words:
                if len(word) > 3 and word in file_lower:  # Cari kata dengan panjang >3 karakter
                    return os.path.join(assets_folder, filename)
        
        # Default placeholder
        return "no_poster.jpg" 