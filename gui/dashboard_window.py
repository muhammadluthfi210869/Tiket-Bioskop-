from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QMessageBox, QFrame, QStackedWidget, QScrollArea,
                             QSizePolicy, QGridLayout, QGraphicsDropShadowEffect)
from PyQt5.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve, QDateTime, QPoint
from PyQt5.QtGui import QFont, QIcon, QPixmap, QColor, QPalette, QBrush
import os
from PyQt5.QtCore import pyqtSignal
import uuid

# Impor halaman yang diperlukan
from gui.movies_page import MoviesPage
from gui.food_page import FoodPage
from gui.topup_page import TopUpPage
from gui.history_page import HistoryPage
from models import UserModel, MovieModel
from utils.helper import find_poster_for_film

class AnimatedWidget(QWidget):
    """Widget dengan dukungan animasi"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self._animations = {}
        
    def add_shadow_effect(self, blur_radius=10, x_offset=0, y_offset=4, color=QColor(0, 0, 0, 60)):
        """Menambahkan efek bayangan"""
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(blur_radius)
        shadow.setOffset(x_offset, y_offset)
        shadow.setColor(color)
        self.setGraphicsEffect(shadow)
        
    def add_hover_animation(self, property_name, start_value, end_value, duration=200):
        """Menambahkan animasi hover"""
        animation = QPropertyAnimation(self, property_name)
        animation.setDuration(duration)
        animation.setStartValue(start_value)
        animation.setEndValue(end_value)
        animation.setEasingCurve(QEasingCurve.OutCubic)
        self._animations[property_name] = animation
        
    def enterEvent(self, event):
        """Handler saat mouse masuk widget"""
        for animation in self._animations.values():
            animation.setDirection(QPropertyAnimation.Forward)
            animation.start()
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        """Handler saat mouse keluar widget"""
        for animation in self._animations.values():
            animation.setDirection(QPropertyAnimation.Backward)
            animation.start()
        super().leaveEvent(event)

class MovieCard(AnimatedWidget):
    """Widget untuk menampilkan film"""
    clicked = pyqtSignal(dict)
    
    def __init__(self, movie_data, parent=None):
        super().__init__(parent)
        self.movie_data = movie_data
        self.init_ui()
        
        # Tambahkan efek bayangan
        self.add_shadow_effect(blur_radius=15, y_offset=4)
        
        # Tambahkan animasi hover
        self.add_hover_animation(b"pos", QPoint(0, 0), QPoint(0, -5))
        
    def init_ui(self):
        self.setObjectName("movie_card")
        self.setStyleSheet("""
            #movie_card {
                background-color: #1A1A1A;
                border-radius: 12px;
                padding: 10px;
                margin: 5px;
            }
            QLabel {
                color: #FFFFFF;
                font-family: 'Poppins', 'Montserrat', sans-serif;
            }
        """)
        
        # Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 10)
        layout.setSpacing(10)
        
        # Poster
        poster_container = QFrame()
        poster_container.setObjectName("poster_container")
        poster_container.setStyleSheet("""
            #poster_container {
                background-color: #0D0D0D;
                border-radius: 8px;
                padding: 0px;
            }
        """)
        
        poster_layout = QVBoxLayout(poster_container)
        poster_layout.setContentsMargins(0, 0, 0, 0)
        
        poster_label = QLabel()
        poster_label.setFixedSize(200, 300)
        poster_label.setScaledContents(True)
        
        # Load poster image
        poster_path = self.movie_data.get("poster_path", "")
        if poster_path and os.path.exists(poster_path):
            pixmap = QPixmap(poster_path)
            poster_label.setPixmap(pixmap)
        else:
            # Default poster jika tidak ada
            default_poster = os.path.join("assets", "templates", "template.jpg")
            if os.path.exists(default_poster):
                pixmap = QPixmap(default_poster)
                poster_label.setPixmap(pixmap)
            else:
                print(f"Warning: Default poster not found at {default_poster}")
                # Set background color sebagai fallback
                poster_label.setStyleSheet("background-color: #2A2A2A; border-radius: 8px;")
        
        poster_layout.addWidget(poster_label)
        
        # Movie info
        info_container = QWidget()
        info_layout = QVBoxLayout(info_container)
        info_layout.setContentsMargins(10, 0, 10, 0)
        info_layout.setSpacing(5)
        
        # Title
        title_label = QLabel(self.movie_data.get("title", ""))
        title_label.setStyleSheet("""
            font-weight: bold;
            font-size: 16px;
        """)
        title_label.setWordWrap(True)
        
        # Genre
        genre_label = QLabel(self.movie_data.get("genre", ""))
        genre_label.setStyleSheet("""
            color: #888888;
            font-size: 14px;
        """)
        
        # Price
        price = self.movie_data.get("price", 0)
        price_label = QLabel(f"Rp {price:,.0f}".replace(",", "."))
        price_label.setStyleSheet("""
            color: #FFD700;
            font-weight: bold;
            font-size: 14px;
        """)
        
        # Book button
        book_button = QPushButton("Pesan")
        book_button.setCursor(Qt.PointingHandCursor)
        book_button.setStyleSheet("""
            QPushButton {
                background-color: #FFD700;
                color: #000000;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #FFC000;
            }
            QPushButton:pressed {
                background-color: #E6B800;
            }
        """)
        book_button.clicked.connect(self.on_book_clicked)
        
        info_layout.addWidget(title_label)
        info_layout.addWidget(genre_label)
        info_layout.addWidget(price_label)
        info_layout.addWidget(book_button)
        
        layout.addWidget(poster_container)
        layout.addWidget(info_container)
        
    def on_book_clicked(self):
        self.clicked.emit(self.movie_data)
        
    def mousePressEvent(self, event):
        self.clicked.emit(self.movie_data)
        super().mousePressEvent(event)

class DashboardWindow(QMainWindow):
    def __init__(self, user_data):
        super().__init__()
        self.user_data = user_data
        self.recommendations = []
        self.setWindowTitle("CinemaTIX - Sistem Pemesanan Tiket Bioskop")
        self.setGeometry(100, 100, 900, 600)
        self.init_ui()
        self.setup_signals()
        
    def init_ui(self):
        # Set window background and styling
        self.setStyleSheet("""
            QMainWindow {
                background-color: #0A0A0A;
            }
            QWidget {
                font-family: 'Poppins', 'Montserrat', sans-serif;
            }
            QPushButton {
                background-color: #FFD700;
                color: #000000;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #FFC000;
            }
            QPushButton:pressed {
                background-color: #E6B800;
            }
            QLabel {
                color: #FFFFFF;
            }
        """)
        
        # Widget utama
        central_widget = QWidget()
        central_widget.setObjectName("central_widget")
        central_widget.setStyleSheet("""
            #central_widget {
                background-color: rgba(10, 10, 10, 0.95);
            }
        """)
        self.setCentralWidget(central_widget)
        
        # Layout utama
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # === NAVBAR DI SISI KIRI ===
        navbar_widget = QWidget()
        navbar_widget.setObjectName("navbar")
        navbar_widget.setFixedWidth(250)  # Increased width for better spacing
        navbar_widget.setStyleSheet("""
            #navbar {
                background-color: #0F0F0F;
                border-right: 1px solid #1A1A1A;
            }
        """)
        
        # Add shadow effect to navbar
        navbar_shadow = QGraphicsDropShadowEffect()
        navbar_shadow.setBlurRadius(20)
        navbar_shadow.setColor(QColor(0, 0, 0, 80))
        navbar_shadow.setOffset(5, 0)
        navbar_widget.setGraphicsEffect(navbar_shadow)
        
        navbar_layout = QVBoxLayout(navbar_widget)
        navbar_layout.setContentsMargins(0, 0, 0, 0)
        navbar_layout.setSpacing(0)
        
        # Logo and title container
        logo_container = QWidget()
        logo_container.setObjectName("logo_container")
        logo_container.setStyleSheet("""
            #logo_container {
                background-color: #0F0F0F;
                padding: 25px 20px;
                border-bottom: 1px solid #1A1A1A;
            }
        """)
        logo_layout = QHBoxLayout(logo_container)
        logo_layout.setContentsMargins(15, 0, 15, 0)
        
        # App logo (assuming you have a logo.png in assets/icons)
        logo_label = QLabel()
        logo_pixmap = QPixmap(os.path.join("assets", "icons", "logo.png"))
        if not logo_pixmap.isNull():
            logo_label.setPixmap(logo_pixmap.scaled(32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        
        # App title with new styling
        app_title = QLabel("CinemaTIX")
        app_title.setObjectName("app_title")
        title_font = QFont("Poppins", 18, QFont.Bold)
        app_title.setFont(title_font)
        app_title.setStyleSheet("""
            #app_title {
                color: #FFD700;
                letter-spacing: 1px;
                margin-left: 10px;
            }
        """)
        
        logo_layout.addWidget(logo_label)
        logo_layout.addWidget(app_title)
        navbar_layout.addWidget(logo_container)
        
        # Saldo widget with new design
        saldo_widget = QWidget()
        saldo_widget.setObjectName("saldo_widget")
        saldo_widget.setStyleSheet("""
            #saldo_widget {
                background-color: #151515;
                margin: 20px;
                border-radius: 12px;
                padding: 20px;
            }
        """)
        
        # Add shadow effect to saldo widget
        saldo_shadow = QGraphicsDropShadowEffect()
        saldo_shadow.setBlurRadius(15)
        saldo_shadow.setColor(QColor(0, 0, 0, 60))
        saldo_shadow.setOffset(0, 2)
        saldo_widget.setGraphicsEffect(saldo_shadow)
        
        saldo_layout = QVBoxLayout(saldo_widget)
        saldo_layout.setContentsMargins(15, 15, 15, 15)
        saldo_layout.setSpacing(8)
        
        saldo_label = QLabel("Saldo Anda")
        saldo_label.setStyleSheet("""
            color: #B3B3B3;
            font-size: 13px;
            font-weight: 500;
            margin-bottom: 5px;
        """)
        
        current_saldo = self.user_data.get('saldo', UserModel.get_saldo(self.user_data['username']))
        self.user_data['saldo'] = current_saldo
        
        self.saldo_value_label = QLabel(f"Rp {current_saldo:,}".replace(',', '.'))
        self.saldo_value_label.setStyleSheet("""
            color: #FFD700;
            font-size: 24px;
            font-weight: 600;
            letter-spacing: 0.5px;
        """)
        
        saldo_layout.addWidget(saldo_label)
        saldo_layout.addWidget(self.saldo_value_label)
        
        navbar_layout.addWidget(saldo_widget)
        
        # Navigation buttons with new styling
        nav_buttons = [
            {"text": "Dashboard", "icon": "dashboard.png"},
            {"text": "Movies", "icon": "movie.png"},
            {"text": "Pesan Makanan", "icon": "food.png"},
            {"text": "Top Up Saldo", "icon": "wallet.png"},
            {"text": "History", "icon": "history.png"}
        ]
        
        self.nav_button_list = []
        
        nav_button_container = QWidget()
        nav_button_container.setObjectName("nav_button_container")
        nav_button_container.setStyleSheet("""
            #nav_button_container {
                background-color: transparent;
                margin: 10px 0;
            }
        """)
        nav_button_layout = QVBoxLayout(nav_button_container)
        nav_button_layout.setContentsMargins(20, 0, 20, 0)
        nav_button_layout.setSpacing(8)
        
        for i, button_info in enumerate(nav_buttons):
            button = QPushButton(button_info["text"])
            button.setObjectName(f"nav_button_{i}")
            
            try:
                icon_path = os.path.join("assets", "icons", button_info["icon"])
                if os.path.exists(icon_path):
                    button.setIcon(QIcon(icon_path))
                    button.setIconSize(QSize(20, 20))
            except:
                pass
                
            button.setCheckable(True)
            button.setStyleSheet("""
                QPushButton {
                    text-align: left;
                    padding: 12px 20px;
                    border: none;
                    border-radius: 8px;
                    color: #B3B3B3;
                    background-color: transparent;
                    font-size: 14px;
                    font-weight: 500;
                }
                QPushButton:checked {
                    background-color: #FFD700;
                    color: #000000;
                    font-weight: 600;
                }
                QPushButton:hover:!checked {
                    background-color: rgba(255, 215, 0, 0.1);
                    color: #FFD700;
                }
            """)
            
            button.clicked.connect(lambda checked, index=i: self.switch_page(index))
            nav_button_layout.addWidget(button)
            self.nav_button_list.append(button)
        
        navbar_layout.addWidget(nav_button_container)
        navbar_layout.addStretch(1)
        
        # Logout button with new styling
        logout_button = QPushButton("Logout")
        logout_button.setObjectName("logout_button")
        logout_button.setCursor(Qt.PointingHandCursor)
        logout_button.setStyleSheet("""
            QPushButton#logout_button {
                margin: 20px;
                padding: 12px;
                border: none;
                border-radius: 8px;
                color: #E5E5E5;
                background-color: #1A1A1A;
                font-size: 14px;
                font-weight: 500;
            }
            QPushButton#logout_button:hover {
                background-color: #B71C1C;
                color: white;
            }
        """)
        logout_button.clicked.connect(self.handle_logout)
        navbar_layout.addWidget(logout_button)
        
        # === CONTENT AREA ===
        content_widget = QWidget()
        content_widget.setObjectName("content")
        content_widget.setStyleSheet("""
            #content {
                background-color: #0A0A0A;
            }
        """)
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        
        # Stack widget for different pages
        self.stack_widget = QStackedWidget()
        
        # Dashboard page with new styling
        dashboard_page = QWidget()
        dashboard_page.setObjectName("dashboard_page")
        dashboard_page.setStyleSheet("""
            #dashboard_page {
                background-color: #0A0A0A;
            }
        """)
        
        # Scroll area for dashboard
        dashboard_scroll_area = QScrollArea()
        dashboard_scroll_area.setObjectName("dashboard_scroll")
        dashboard_scroll_area.setWidgetResizable(True)
        dashboard_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        dashboard_scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: transparent;
                border: none;
            }
            QScrollBar:vertical {
                background-color: #1A1A1A;
                width: 8px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background-color: #333333;
                min-height: 30px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #444444;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        dashboard_scroll_area.setWidget(dashboard_page)
        
        dashboard_layout = QVBoxLayout(dashboard_page)
        dashboard_layout.setContentsMargins(40, 40, 40, 40)
        dashboard_layout.setSpacing(30)
        
        # Welcome section with new styling
        welcome_section = QWidget()
        welcome_section.setObjectName("welcome_section")
        welcome_layout = QVBoxLayout(welcome_section)
        welcome_layout.setContentsMargins(0, 0, 0, 0)
        welcome_layout.setSpacing(5)
        
        # Welcome message with icon
        welcome_container = QWidget()
        welcome_container_layout = QHBoxLayout(welcome_container)
        welcome_container_layout.setContentsMargins(0, 0, 0, 0)
        
        welcome_icon = QLabel()
        welcome_icon_path = os.path.join("assets", "icons", "user.png")
        if os.path.exists(welcome_icon_path):
            welcome_pixmap = QPixmap(welcome_icon_path)
            welcome_icon.setPixmap(welcome_pixmap.scaled(32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        
        welcome_text = QLabel(f"Selamat datang, {self.user_data['nama']}!")
        welcome_text.setStyleSheet("""
            color: #FFFFFF;
            font-size: 28px;
            font-weight: 600;
            margin-left: 10px;
        """)
        
        welcome_container_layout.addWidget(welcome_icon)
        welcome_container_layout.addWidget(welcome_text)
        welcome_container_layout.addStretch()
        
        welcome_layout.addWidget(welcome_container)
        
        # Subtitle
        welcome_subtitle = QLabel("Nikmati pengalaman menonton film terbaik bersama CinemaTIX")
        welcome_subtitle.setStyleSheet("""
            color: #B3B3B3;
            font-size: 16px;
            font-weight: 400;
            margin-top: 5px;
        """)
        welcome_layout.addWidget(welcome_subtitle)
        
        dashboard_layout.addWidget(welcome_section)
        
        # Info cards with new styling
        info_cards_layout = QHBoxLayout()
        info_cards_layout.setSpacing(25)
        
        # Saldo card
        saldo_card = QFrame()
        saldo_card.setObjectName("saldo_card")
        saldo_card.setStyleSheet("""
            #saldo_card {
                background-color: #151515;
                border-radius: 15px;
                padding: 25px;
            }
        """)
        
        # Add shadow effect
        card_shadow = QGraphicsDropShadowEffect()
        card_shadow.setBlurRadius(20)
        card_shadow.setColor(QColor(0, 0, 0, 60))
        card_shadow.setOffset(0, 4)
        saldo_card.setGraphicsEffect(card_shadow)
        
        saldo_card_layout = QVBoxLayout(saldo_card)
        saldo_card_layout.setSpacing(15)
        
        # Saldo icon and title
        saldo_header = QHBoxLayout()
        saldo_icon = QLabel()
        saldo_icon_path = os.path.join("assets", "icons", "wallet.png")
        if os.path.exists(saldo_icon_path):
            saldo_pixmap = QPixmap(saldo_icon_path)
            saldo_icon.setPixmap(saldo_pixmap.scaled(24, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        
        saldo_card_title = QLabel("Saldo Anda")
        saldo_card_title.setStyleSheet("""
            color: #B3B3B3;
            font-size: 14px;
            font-weight: 500;
        """)
        
        saldo_header.addWidget(saldo_icon)
        saldo_header.addWidget(saldo_card_title)
        saldo_header.addStretch()
        
        saldo_card_layout.addLayout(saldo_header)
        
        # Saldo value
        self.dashboard_saldo_value = QLabel(f"Rp {current_saldo:,}".replace(',', '.'))
        self.dashboard_saldo_value.setStyleSheet("""
            color: #FFD700;
            font-size: 32px;
            font-weight: 600;
            letter-spacing: 0.5px;
        """)
        saldo_card_layout.addWidget(self.dashboard_saldo_value)
        
        # Top up button
        topup_button = QPushButton("Top Up Saldo")
        topup_button.setCursor(Qt.PointingHandCursor)
        topup_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 215, 0, 0.1);
                color: #FFD700;
                border: none;
                border-radius: 8px;
                padding: 12px;
                font-size: 14px;
                font-weight: 500;
                margin-top: 10px;
            }
            QPushButton:hover {
                background-color: rgba(255, 215, 0, 0.2);
            }
        """)
        topup_button.clicked.connect(lambda: self.switch_page(3))
        saldo_card_layout.addWidget(topup_button)
        
        # User info card
        user_card = QFrame()
        user_card.setObjectName("user_card")
        user_card.setStyleSheet("""
            #user_card {
                background-color: #151515;
                border-radius: 15px;
                padding: 25px;
            }
        """)
        
        # Add shadow effect
        user_card_shadow = QGraphicsDropShadowEffect()
        user_card_shadow.setBlurRadius(20)
        user_card_shadow.setColor(QColor(0, 0, 0, 60))
        user_card_shadow.setOffset(0, 4)
        user_card.setGraphicsEffect(user_card_shadow)
        
        user_card_layout = QVBoxLayout(user_card)
        user_card_layout.setSpacing(15)
        
        # User info icon and title
        user_header = QHBoxLayout()
        user_icon = QLabel()
        user_icon_path = os.path.join("assets", "icons", "user-info.png")
        if os.path.exists(user_icon_path):
            user_pixmap = QPixmap(user_icon_path)
            user_icon.setPixmap(user_pixmap.scaled(24, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        
        user_card_title = QLabel("Informasi Pengguna")
        user_card_title.setStyleSheet("""
            color: #B3B3B3;
            font-size: 14px;
            font-weight: 500;
        """)
        
        user_header.addWidget(user_icon)
        user_header.addWidget(user_card_title)
        user_header.addStretch()
        
        user_card_layout.addLayout(user_header)
        
        # User info details
        user_info_style = """
            color: #E0E0E0;
            font-size: 14px;
            font-weight: 400;
            margin-top: 5px;
        """
        
        username_label = QLabel(f"Username: {self.user_data['username']}")
        username_label.setStyleSheet(user_info_style)
        
        usia_label = QLabel(f"Usia: {self.user_data['usia']} tahun")
        usia_label.setStyleSheet(user_info_style)
        
        genre_label = QLabel(f"Genre Favorit: {self.user_data['genre_favorit']}")
        genre_label.setStyleSheet(user_info_style)
        
        user_card_layout.addWidget(username_label)
        user_card_layout.addWidget(usia_label)
        user_card_layout.addWidget(genre_label)
        
        # Add cards to layout
        info_cards_layout.addWidget(saldo_card)
        info_cards_layout.addWidget(user_card)
        
        dashboard_layout.addLayout(info_cards_layout)
        
        # Movie recommendations section
        rec_frame = QFrame()
        rec_frame.setObjectName("rec_frame")
        rec_frame.setStyleSheet("""
            #rec_frame {
                background-color: #151515;
                border-radius: 15px;
                padding: 30px;
            }
        """)
        
        # Add shadow effect
        rec_shadow = QGraphicsDropShadowEffect()
        rec_shadow.setBlurRadius(20)
        rec_shadow.setColor(QColor(0, 0, 0, 60))
        rec_shadow.setOffset(0, 4)
        rec_frame.setGraphicsEffect(rec_shadow)
        
        rec_layout = QVBoxLayout(rec_frame)
        rec_layout.setSpacing(25)
        
        # Recommendations header
        rec_header = QHBoxLayout()
        rec_icon = QLabel()
        rec_icon_path = os.path.join("assets", "icons", "movie-reel.png")
        if os.path.exists(rec_icon_path):
            rec_pixmap = QPixmap(rec_icon_path)
            rec_icon.setPixmap(rec_pixmap.scaled(24, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        
        rec_title = QLabel("Rekomendasi Film Untuk Anda")
        rec_title.setStyleSheet("""
            color: #FFFFFF;
            font-size: 18px;
            font-weight: 600;
        """)
        
        rec_header.addWidget(rec_icon)
        rec_header.addWidget(rec_title)
        rec_header.addStretch()
        
        rec_layout.addLayout(rec_header)
        
        # Recommendations subtitle
        rec_subtitle = QLabel(f"Berdasarkan genre favorit Anda: {self.user_data['genre_favorit']}")
        rec_subtitle.setStyleSheet("""
            color: #B3B3B3;
            font-size: 14px;
            font-weight: 400;
            margin-bottom: 10px;
        """)
        rec_layout.addWidget(rec_subtitle)
        
        # Movie recommendations grid
        rec_grid = QHBoxLayout()
        rec_grid.setSpacing(20)
        
        recommended_movies = self.get_recommended_movies()
        
        if recommended_movies:
            for movie in recommended_movies[:3]:
                movie_card = MovieCard(movie)
                movie_card.clicked.connect(self.on_recommended_movie_clicked)
                # Remove the hover animation effect for dashboard cards
                movie_card._animations.clear()  # Clear all animations
                rec_grid.addWidget(movie_card)
        else:
            rec_placeholder = QLabel(f"Tidak ada film {self.user_data['genre_favorit']} yang tersedia saat ini.")
            rec_placeholder.setStyleSheet("""
                color: #888888;
                font-size: 14px;
                font-style: italic;
                padding: 20px 0;
            """)
            rec_layout.addWidget(rec_placeholder)
        
        rec_layout.addLayout(rec_grid)
        
        # Browse all movies button
        browse_movies_button = QPushButton("Jelajahi Semua Film")
        browse_movies_button.setCursor(Qt.PointingHandCursor)
        browse_movies_button.setStyleSheet("""
            QPushButton {
                background-color: #FFD700;
                color: #000000;
                border: none;
                border-radius: 8px;
                padding: 15px;
                font-size: 14px;
                font-weight: 600;
                margin-top: 20px;
            }
            QPushButton:hover {
                background-color: #F5CB0C;
            }
        """)
        browse_movies_button.clicked.connect(lambda: self.switch_page(1))
        rec_layout.addWidget(browse_movies_button)
        
        dashboard_layout.addWidget(rec_frame)
        dashboard_layout.addStretch()
        
        # Add pages to stack widget
        self.stack_widget.addWidget(dashboard_scroll_area)
        
        # Add other pages
        self.movies_page = MoviesPage(self.user_data)
        if hasattr(self.movies_page, 'switch_page_signal'):
            self.movies_page.switch_page_signal.connect(self.handle_page_signals)
        if hasattr(self.movies_page, 'ticket_purchased'):
            print("Connecting ticket_purchased signal from MoviesPage to handle_ticket_purchase")
            self.movies_page.ticket_purchased.connect(self.handle_ticket_purchase)
        self.stack_widget.addWidget(self.movies_page)
        
        self.food_page = FoodPage(self.user_data)
        self.stack_widget.addWidget(self.food_page)
        
        self.topup_page = TopUpPage(self.user_data)
        self.stack_widget.addWidget(self.topup_page)
        
        # IMPORTANT: Only connect signals once during initialization to avoid duplicates
        self.topup_page.top_up_success.connect(self.handle_top_up)
        
        self.history_page = HistoryPage(self.user_data)
        self.stack_widget.addWidget(self.history_page)
        
        content_layout.addWidget(self.stack_widget)
        
        # Add navbar and content to main layout
        main_layout.addWidget(navbar_widget)
        main_layout.addWidget(content_widget)
        
        # Set initial page and active button
        self.stack_widget.setCurrentIndex(0)
        self.nav_button_list[0].setChecked(True)
    
    def update_saldo_display(self, new_saldo):
        """Update saldo setelah transaksi berhasil"""
        # Check if new_saldo is a dictionary or other unexpected type
        if not isinstance(new_saldo, (int, float)):
            print(f"Warning: non-numeric saldo received: {type(new_saldo)}")
            # Attempt to get saldo from user_data if available
            if self.user_data and 'saldo' in self.user_data:
                new_saldo = self.user_data['saldo']
            else:
                # Default to 0 if no valid saldo available
                new_saldo = 0

        # Log saldo update untuk debugging
        print(f"DashboardWindow: Updating saldo display from {self.user_data.get('saldo', 0)} to {new_saldo}")
        
        # Update data pengguna
        self.user_data['saldo'] = new_saldo
        
        # Update tampilan saldo di navbar
        try:
            self.saldo_value_label.setText(f"Rp {int(new_saldo):,}".replace(',', '.'))
        except (TypeError, ValueError) as e:
            print(f"Error formatting saldo: {e}")
            self.saldo_value_label.setText(f"Rp {new_saldo}")
        
        # Update tampilan di dashboard dengan referensi langsung
        if hasattr(self, 'dashboard_saldo_value'):
            try:
                self.dashboard_saldo_value.setText(f"Rp {int(new_saldo):,}".replace(',', '.'))
            except (TypeError, ValueError) as e:
                print(f"Error formatting dashboard saldo: {e}")
                self.dashboard_saldo_value.setText(f"Rp {new_saldo}")
        
        # Update data user di halaman lain
        # Update movies page
        if hasattr(self, 'movies_page'):
            self.movies_page.update_user_data(self.user_data)
        
        # Update food page
        if hasattr(self, 'food_page'):
            self.food_page.update_user_data(self.user_data)
        
        # Update data user di topup page jika saldo berubah
        if hasattr(self, 'topup_page'):
            # Update user_data di topup_page
            self.topup_page.user_data = self.user_data
            # Update tampilan saldo di topup_page jika ada method untuk itu
            if hasattr(self.topup_page, 'update_display_saldo'):
                self.topup_page.update_display_saldo(new_saldo)
            # Atau update label saldo jika ada
            elif hasattr(self.topup_page, 'current_saldo_label'):
                try:
                    self.topup_page.current_saldo_label.setText(f"Saldo saat ini: Rp {int(new_saldo):,}".replace(',', '.'))
                except (TypeError, ValueError) as e:
                    print(f"Error formatting topup page saldo: {e}")
                    self.topup_page.current_saldo_label.setText(f"Saldo saat ini: Rp {new_saldo}")
    
    def switch_page(self, index):
        # Ubah halaman yang aktif
        self.stack_widget.setCurrentIndex(index)
        
        # Ubah tombol yang aktif
        for i, button in enumerate(self.nav_button_list):
            button.setChecked(i == index)
    
    def handle_logout(self):
        from gui.login_window import LoginWindow
        msg = QMessageBox.question(self, 'Konfirmasi', 'Apakah Anda yakin ingin logout?', 
                                   QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if msg == QMessageBox.Yes:
            from main import bcrypt
            self.login_window = LoginWindow(bcrypt)
            self.login_window.show()
            self.close()
    
    def get_recommended_movies(self):
        """Mendapatkan film rekomendasi berdasarkan genre favorit pengguna"""
        fav_genre = self.user_data.get('genre_favorit', '').lower()
        
        # Normalize genre name to handle variations
        normalized_genre = fav_genre.replace('-', '').replace(' ', '')
        
        # Manual recommendations based on genre
        manual_recommendations = {
            'action': [
                {
                    "title": "Avengers",
                    "genre": "Action",
                    "price": 70000,
                    "synopsis": "Earth's mightiest heroes must come together to protect the world from Loki and his alien army.",
                    "duration": 143,
                    "director": "Joss Whedon",
                    "cast": "Robert Downey Jr., Chris Evans, Scarlett Johansson",
                    "schedule": "10:00, 13:00, 16:00, 19:00",
                    "poster_path": find_poster_for_film("Avengers")
                },
                {
                    "title": "Spiderman",
                    "genre": "Action",
                    "price": 65000,
                    "synopsis": "After being bitten by a genetically-modified spider, a high school student gains spider-like abilities.",
                    "duration": 121,
                    "director": "Sam Raimi",
                    "cast": "Tobey Maguire, Kirsten Dunst, Willem Dafoe",
                    "schedule": "11:00, 14:00, 17:00, 20:00",
                    "poster_path": find_poster_for_film("Spiderman")
                },
                {
                    "title": "Batman",
                    "genre": "Action",
                    "price": 65000,
                    "synopsis": "The Dark Knight fights crime in Gotham City with both physical prowess and detective skills.",
                    "duration": 126,
                    "director": "Christopher Nolan",
                    "cast": "Christian Bale, Michael Caine, Gary Oldman",
                    "schedule": "12:00, 15:00, 18:00, 21:00",
                    "poster_path": find_poster_for_film("Batman")
                }
            ],
            'biography': [
                {
                    "title": "Oppenheimer",
                    "genre": "Biography",
                    "price": 70000,
                    "synopsis": "The story of American scientist J. Robert Oppenheimer and his role in the development of the atomic bomb.",
                    "duration": 180,
                    "director": "Christopher Nolan",
                    "cast": "Cillian Murphy, Emily Blunt, Matt Damon",
                    "schedule": "10:30, 14:30, 18:30",
                    "poster_path": find_poster_for_film("Oppenheimer")
                },
                {
                    "title": "Bohemian Rhapsody",
                    "genre": "Biography",
                    "price": 65000,
                    "synopsis": "The story of the legendary British rock band Queen and lead singer Freddie Mercury.",
                    "duration": 134,
                    "director": "Bryan Singer",
                    "cast": "Rami Malek, Lucy Boynton, Gwilym Lee",
                    "schedule": "11:30, 15:30, 19:30",
                    "poster_path": find_poster_for_film("Bohemian Rhapsody")
                },
                {
                    "title": "The Theory of Everything",
                    "genre": "Biography",
                    "price": 65000,
                    "synopsis": "A look at the relationship between the famous physicist Stephen Hawking and his wife.",
                    "duration": 123,
                    "director": "James Marsh",
                    "cast": "Eddie Redmayne, Felicity Jones",
                    "schedule": "12:30, 16:30, 20:30",
                    "poster_path": find_poster_for_film("The Theory of Everything")
                }
            ],
            'drama': [
                {
                    "title": "Joker",
                    "genre": "Drama",
                    "price": 70000,
                    "synopsis": "A failed comedian goes insane and turns to crime and chaos in Gotham City.",
                    "duration": 122,
                    "director": "Todd Phillips",
                    "cast": "Joaquin Phoenix, Robert De Niro",
                    "schedule": "13:00, 16:00, 19:00",
                    "poster_path": find_poster_for_film("Joker")
                },
                {
                    "title": "The Godfather",
                    "genre": "Drama",
                    "price": 65000,
                    "synopsis": "The aging patriarch of an organized crime dynasty transfers control to his son.",
                    "duration": 175,
                    "director": "Francis Ford Coppola",
                    "cast": "Marlon Brando, Al Pacino, James Caan",
                    "schedule": "14:00, 18:00, 22:00",
                    "poster_path": find_poster_for_film("The Godfather")
                },
                {
                    "title": "Forrest Gump",
                    "genre": "Drama",
                    "price": 65000,
                    "synopsis": "The history of the United States from the 1950s to the '70s unfolds from the perspective of an Alabama man with an IQ of 75.",
                    "duration": 142,
                    "director": "Robert Zemeckis",
                    "cast": "Tom Hanks, Robin Wright, Gary Sinise",
                    "schedule": "13:30, 17:30, 21:30",
                    "poster_path": find_poster_for_film("Forrest Gump")
                }
            ],
            'scifi': [
                {
                    "title": "Dune",
                    "genre": "Sci-Fi",
                    "price": 70000,
                    "synopsis": "Feature adaptation of Frank Herbert's science fiction novel about the son of a noble family entrusted with the protection of the most valuable asset in the galaxy.",
                    "duration": 155,
                    "director": "Denis Villeneuve",
                    "cast": "Timothée Chalamet, Rebecca Ferguson, Zendaya",
                    "schedule": "12:00, 16:00, 20:00",
                    "poster_path": find_poster_for_film("Dune")
                },
                {
                    "title": "Inception",
                    "genre": "Sci-Fi",
                    "price": 65000,
                    "synopsis": "A thief who steals corporate secrets through dream-sharing technology is given the task of planting an idea into the mind of a CEO.",
                    "duration": 148,
                    "director": "Christopher Nolan",
                    "cast": "Leonardo DiCaprio, Joseph Gordon-Levitt, Ellen Page",
                    "schedule": "14:30, 18:30, 22:30",
                    "poster_path": find_poster_for_film("Inception")
                },
                {
                    "title": "The Matrix",
                    "genre": "Sci-Fi",
                    "price": 65000,
                    "synopsis": "A computer hacker learns about the true nature of reality and his role in the war against its controllers.",
                    "duration": 136,
                    "director": "Lana Wachowski, Lilly Wachowski",
                    "cast": "Keanu Reeves, Laurence Fishburne, Carrie-Anne Moss",
                    "schedule": "15:00, 19:00, 23:00",
                    "poster_path": find_poster_for_film("The Matrix")
                }
            ]
        }
        
        # Return the appropriate recommendations for the user's favorite genre
        # First check if we have manual recommendations for this genre
        if normalized_genre in manual_recommendations:
            return manual_recommendations[normalized_genre]
            
        # Check if a partial match can be found
        for genre_key in manual_recommendations.keys():
            if genre_key in normalized_genre or normalized_genre in genre_key:
                return manual_recommendations[genre_key]
            
        # If not in our manual recommendations, fallback to database search
        all_movies = MovieModel.get_all_movies()
        recommended = []
        
        for movie in all_movies:
            movie_genres = movie.get('genre', '').lower()
            if fav_genre in movie_genres:
                # Tambahkan path poster ke data film
                movie_with_poster = movie.copy()
                movie_with_poster["poster_path"] = find_poster_for_film(movie["title"])
                recommended.append(movie_with_poster)
        
        return recommended

    def handle_page_signals(self, signal_type, data):
        """Menangani signal dari halaman lain"""
        if signal_type == "update_saldo" and 'new_saldo' in data:
            # Update saldo dari halaman movies
            self.update_saldo_display(data['new_saldo'])
            print(f"Dashboard received saldo update: {data['new_saldo']}")
        elif signal_type == "show_history":
            # Beralih ke halaman history
            self.show_history()

    def on_recommended_movie_clicked(self, movie_data):
        """Handler ketika kartu film rekomendasi diklik"""
        # Beralih ke halaman movies terlebih dahulu
        self.switch_page(1)
        
        # Tampilkan halaman detail film dengan data film yang dipilih
        if hasattr(self, 'movies_page') and hasattr(self.movies_page, 'movie_detail_page'):
            self.movies_page.current_movie = movie_data
            self.movies_page.movie_detail_page.display_movie_detail(movie_data)
            self.movies_page.stack_widget.setCurrentIndex(self.movies_page.pages["movie_detail"]) 

    def handle_ticket_purchase(self, ticket_data):
        """Handler untuk pembelian tiket"""
        try:
            print("Received ticket data:", ticket_data)  # Debug print
            
            # Format data tiket untuk history
            transaction_data = {
                "type": "Tiket",
                "movie_title": ticket_data.get("movie_title", "Unknown Movie"),
                "total": -ticket_data.get("total_price", 0),  # Menggunakan total_price dari data tiket
                "studio": ticket_data.get("studio_type", "Regular"),
                "theater": ticket_data.get("theater", ""),
                "cinema": ticket_data.get("cinema", ""),
                "seats": ", ".join(ticket_data.get("seats", [])) if isinstance(ticket_data.get("seats"), list) else ticket_data.get("seats", ""),
                "show_date": ticket_data.get("show_date", ""),
                "show_time": ticket_data.get("show_time", ""),
                "status": "Sukses",
                "timestamp": QDateTime.currentDateTime().toString("dd/MM/yyyy HH:mm")
            }
            
            print("Formatted transaction data:", transaction_data)  # Debug print
            
            # Directly add to transactions in history_page if available
            if hasattr(self, 'history_page'):
                print("Adding transaction to history")
                self.history_page.add_transaction(transaction_data)
                # Force refresh the history page transactions
                self.history_page.filter_transactions()
                print("Transaction added to history page")
            else:
                print("Error: history_page not found")
            
        except Exception as e:
            print(f"Error handling ticket purchase: {str(e)}")
            import traceback
            traceback.print_exc()
            # Fallback dengan format minimal
            transaction_data = {
                "type": "Tiket",
                "movie_title": ticket_data.get("movie_title", "Unknown Movie"),
                "total": -ticket_data.get("total_price", 0),
                "status": "Sukses",
                "timestamp": QDateTime.currentDateTime().toString("dd/MM/yyyy HH:mm")
            }
            if hasattr(self, 'history_page'):
                self.history_page.add_transaction(transaction_data)
                # Force refresh again
                self.history_page.filter_transactions()
    
    def handle_food_order(self, order_data):
        """Handler untuk pemesanan makanan"""
        try:
            # Format items untuk history
            formatted_items = []
            items = order_data.get("items", [])
            
            # Jika items adalah dictionary
            if isinstance(items, dict):
                for name, details in items.items():
                    formatted_items.append({
                        "name": name,
                        "quantity": details.get("quantity", 0),
                        "price": details.get("price", 0)
                    })
            # Jika items adalah list
            elif isinstance(items, list):
                for item in items:
                    if isinstance(item, (list, tuple)):
                        # Jika item adalah tuple/list dengan format [nama, jumlah, harga]
                        if len(item) >= 3:
                            formatted_items.append({
                                "name": item[0],
                                "quantity": item[1],
                                "price": item[2]
                            })
                        # Jika item adalah tuple/list dengan format [nama, jumlah]
                        elif len(item) >= 2:
                            formatted_items.append({
                                "name": item[0],
                                "quantity": item[1],
                                "price": 0
                            })
                    elif isinstance(item, dict):
                        # Jika item sudah dalam format dictionary
                        formatted_items.append({
                            "name": item.get("name", ""),
                            "quantity": item.get("quantity", 0),
                            "price": item.get("price", 0)
                        })
            
            # Generate a unique transaction ID
            transaction_id = str(uuid.uuid4())
            
            transaction_data = {
                "type": "Makanan",
                "items": formatted_items,
                "total": -order_data.get("total", 0),
                "status": "Sukses",
                "transaction_id": transaction_id,  # Add transaction ID
                "timestamp": QDateTime.currentDateTime().toString("dd/MM/yyyy HH:mm")
            }
            
            # Add to history only once
            if hasattr(self, 'history_page'):
                self.history_page.add_transaction(transaction_data)
                self.history_page.filter_transactions()
            
        except Exception as e:
            print(f"Error handling food order: {str(e)}")
            # Fallback dengan format minimal
            transaction_data = {
                "type": "Makanan",
                "items": [{"name": "Pesanan Makanan", "quantity": 1, "price": order_data.get("total", 0)}],
                "total": -order_data.get("total", 0),
                "status": "Sukses",
                "transaction_id": str(uuid.uuid4()),  # Add transaction ID here too
                "timestamp": QDateTime.currentDateTime().toString("dd/MM/yyyy HH:mm")
            }
            if hasattr(self, 'history_page'):
                self.history_page.add_transaction(transaction_data)
                self.history_page.filter_transactions()
    
    def handle_top_up(self, amount):
        """Handler untuk top up saldo"""
        try:
            print(f"Handle top-up called with amount: {amount}")
            # Check if amount is a valid number
            if not isinstance(amount, (int, float)):
                print(f"Invalid top-up amount format: {amount}")
                return
                
            # Get current balance before updating
            previous_balance = self.user_data.get('saldo', UserModel.get_saldo(self.user_data['username']))
            print(f"Previous balance: {previous_balance}")
            
            # Calculate new balance
            new_balance = previous_balance + amount
            print(f"New balance calculated: {new_balance}")
            
            # Update user data in memory
            self.user_data['saldo'] = new_balance
            
            # Update UI
            self.update_saldo_display(new_balance)
            
            # Add transaction to history with the required format
            if hasattr(self, 'history_page'):
                # Create timestamp
                timestamp = QDateTime.currentDateTime().toString("dd/MM/yyyy HH:mm")
                
                # Generate a unique transaction ID
                transaction_id = str(uuid.uuid4())
                
                # Get the payment method from topup_page if available
                payment_method = "Cash"  # Default
                if hasattr(self, 'topup_page') and hasattr(self.topup_page, 'selected_payment_method'):
                    payment_method = self.topup_page.selected_payment_method
                    
                # Map payment IDs to readable bank names
                payment_method_map = {
                    "bca": "Bank BCA",
                    "bni": "Bank BNI",
                    "mandiri": "Bank Mandiri",
                    "bri": "Bank BRI",
                    "cash": "Cash",
                    "gopay": "GoPay",
                    "ovo": "OVO",
                    "dana": "DANA"
                }
                
                # Get readable payment method name
                readable_payment = payment_method_map.get(payment_method.lower(), payment_method)
                
                # Prepare transaction data with explicit previous and new balance
                transaction_data = {
                    "type": "Top Up",
                    "total": amount,
                    "previous_balance": previous_balance,
                    "new_balance": new_balance,
                    "payment_method": readable_payment,
                    "status": "Sukses",
                    "timestamp": timestamp,
                    "transaction_id": transaction_id
                }
                
                # Add to history and refresh display
                print(f"Adding top-up transaction to history: {amount}, ID: {transaction_id}, Method: {readable_payment}")
                self.history_page.add_transaction(transaction_data)
                self.history_page.filter_transactions()
        except Exception as e:
            print(f"Error in handle_top_up: {str(e)}")

    def setup_signals(self):
        """Setup signal connections"""
        print("Setting up signals in DashboardWindow")
        
        # Movies page signals
        if hasattr(self, 'movies_page'):
            print("Setting up movies_page signals")
            
            # Use a flag to check if signals are already connected
            if not hasattr(self, '_movies_page_signals_connected'):
                print("Connecting switch_page_signal")
                self.movies_page.switch_page_signal.connect(self.handle_page_signals)
                print("Connecting ticket_purchased signal")
                self.movies_page.ticket_purchased.connect(self.handle_ticket_purchase)
                
                # Mark signals as connected
                self._movies_page_signals_connected = True
            
            # Connect ticket_page signals
            if hasattr(self.movies_page, 'ticket_page'):
                print("Setting up ticket_page signals")
                self.movies_page.ticket_page.back_to_movies.connect(lambda: self.movies_page.stack_widget.setCurrentIndex(self.movies_page.pages["movies_list"]))
                self.movies_page.ticket_page.show_history.connect(self.show_history)
        
        # FoodPage signals
        if hasattr(self, 'food_page'):
            print("Setting up food_page signals")
            if not hasattr(self, '_food_page_signals_connected'):
                # Connect only to update_saldo_display for balance updates
                self.food_page.order_completed.connect(self.update_saldo_display)
                # Connect only once to handle_food_order for history updates
                self.food_page.order_completed.connect(self.handle_food_order)
                self._food_page_signals_connected = True
        
        # TopUpPage signals
        if hasattr(self, 'topup_page'):
            print("TopUpPage signals already connected during initialization")
            # Signals already connected during initialization
            # DO NOT connect again to avoid duplicates
    
    def show_history(self):
        """Beralih ke halaman history"""
        # Switch to history page (index 4 bukan 5)
        self.switch_page(4)
        
        # Show a notification
        QMessageBox.information(
            self,
            "History Transaksi",
            "Transaksi Anda telah berhasil dicatat. Anda dapat melihat riwayat transaksi di halaman ini."
        )

    def update_movie_in_history(self, movie_data):
        """Update displayed movie data in history if needed"""
        # ... existing code ... 