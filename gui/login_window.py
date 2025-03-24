from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QPushButton, QMessageBox, QFrame, QGraphicsDropShadowEffect)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QFont, QPixmap, QIcon, QColor, QPalette, QBrush
import os

from models import UserModel
from gui.register_window import RegisterWindow
from gui.dashboard_window import DashboardWindow

class LoginWindow(QMainWindow):
    def __init__(self, bcrypt):
        super().__init__()
        self.bcrypt = bcrypt
        self.init_ui()
        
    def init_ui(self):
        # Set window properties
        self.setWindowTitle('CinemaTIX - Sistem Pemesanan Tiket Bioskop')
        self.setGeometry(300, 300, 900, 600)
        
        # Load background image if available
        bg_image_path = os.path.join("assets", "bg_cinema.jpg")
        if os.path.exists(bg_image_path):
            # Set background image
            palette = QPalette()
            pixmap = QPixmap(bg_image_path)
            palette.setBrush(QPalette.Window, QBrush(pixmap))
            self.setPalette(palette)
        
        # Global stylesheet
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
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #FFC000;
            }
            QPushButton:pressed {
                background-color: #E6B800;
            }
            QLineEdit {
                background-color: #1F1F1F;
                color: #FFFFFF;
                border: 1px solid #333333;
                border-radius: 8px;
                padding: 8px 12px;
            }
            QLineEdit:focus {
                border: 1px solid #FFD700;
            }
            QLabel {
                color: #FFFFFF;
            }
            .error {
                color: #FF4444;
            }
        """)
        
        # Main widget and layout
        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        self.setCentralWidget(main_widget)
        
        # Content container with transparency
        content_container = QWidget()
        content_container.setObjectName("content_container")
        content_container.setStyleSheet("""
            #content_container {
                background-color: rgba(10, 10, 10, 0.85);
                border-radius: 20px;
                margin: 30px;
            }
        """)
        
        # Add shadow effect to content container
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(0, 0, 0, 180))
        shadow.setOffset(0, 0)
        content_container.setGraphicsEffect(shadow)
        
        # Content layout
        content_layout = QHBoxLayout(content_container)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        # Left panel - Brand/Logo
        left_panel = QWidget()
        left_panel.setObjectName("left_panel")
        left_panel.setStyleSheet("""
            #left_panel {
                background-color: rgba(10, 10, 10, 0.7);
                border-top-left-radius: 20px;
                border-bottom-left-radius: 20px;
            }
        """)
        left_panel.setFixedWidth(400)
        
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(40, 40, 40, 40)
        left_layout.setAlignment(Qt.AlignCenter)
        
        # Logo
        logo_label = QLabel("CinemaTIX")
        logo_label.setStyleSheet("""
            QLabel {
                color: #FFD700;
                font-size: 42px;
                font-weight: bold;
                font-family: 'Poppins', 'Montserrat', sans-serif;
                letter-spacing: 2px;
            }
        """)
        # Add shadow effect to logo
        logo_shadow = QGraphicsDropShadowEffect()
        logo_shadow.setBlurRadius(4)
        logo_shadow.setColor(QColor(0, 0, 0, 128))
        logo_shadow.setOffset(0, 2)
        logo_label.setGraphicsEffect(logo_shadow)
        logo_label.setAlignment(Qt.AlignCenter)
        
        # Tagline
        tagline_label = QLabel("Pengalaman Menonton Premium")
        tagline_label.setStyleSheet("""
            QLabel {
                color: #E0E0E0;
                font-size: 16px;
                font-family: 'Poppins', 'Montserrat', sans-serif;
                margin-top: 10px;
                letter-spacing: 1px;
            }
        """)
        tagline_label.setAlignment(Qt.AlignCenter)
        
        # Add cinema icon if available
        cinema_icon = QLabel()
        cinema_icon.setAlignment(Qt.AlignCenter)
        
        icon_path = os.path.join("assets", "icons", "cinema.png")
        if os.path.exists(icon_path):
            pixmap = QPixmap(icon_path)
            pixmap = pixmap.scaled(180, 180, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            cinema_icon.setPixmap(pixmap)
        else:
            # Fallback if icon doesn't exist
            cinema_icon.setText("🎬")
            cinema_icon.setStyleSheet("""
                QLabel {
                    color: #FFD700;
                    font-size: 120px;
                }
            """)
            # Add shadow effect to emoji
            emoji_shadow = QGraphicsDropShadowEffect()
            emoji_shadow.setBlurRadius(10)
            emoji_shadow.setColor(QColor(0, 0, 0, 180))
            emoji_shadow.setOffset(0, 2)
            cinema_icon.setGraphicsEffect(emoji_shadow)
        
        left_layout.addStretch(1)
        left_layout.addWidget(cinema_icon)
        left_layout.addWidget(logo_label)
        left_layout.addWidget(tagline_label)
        left_layout.addStretch(1)
        
        # Right panel - Login Form
        right_panel = QWidget()
        right_panel.setObjectName("right_panel")
        right_panel.setStyleSheet("""
            #right_panel {
                background-color: rgba(18, 18, 18, 0.9);
                border-top-right-radius: 20px;
                border-bottom-right-radius: 20px;
            }
        """)
        
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(50, 50, 50, 50)
        right_layout.setSpacing(20)
        
        # Header with welcome icon
        header_layout = QHBoxLayout()
        header_layout.setAlignment(Qt.AlignCenter)
        
        welcome_icon = QLabel("")
        welcome_icon.setStyleSheet("font-size: 28px; margin-right: 10px;")
        
        header_label = QLabel('Selamat Datang')
        header_label.setFont(QFont('Poppins', 28, QFont.Bold))
        header_label.setStyleSheet("""
            color: #FFFFFF; 
            margin-bottom: 5px; 
            letter-spacing: 1px;
        """)
        # Add shadow effect to header
        header_shadow = QGraphicsDropShadowEffect()
        header_shadow.setBlurRadius(4)
        header_shadow.setColor(QColor(0, 0, 0, 77))
        header_shadow.setOffset(0, 2)
        header_label.setGraphicsEffect(header_shadow)
        
        header_layout.addWidget(welcome_icon)
        header_layout.addWidget(header_label)
        
        subheader_label = QLabel('Silakan login untuk melanjutkan')
        subheader_label.setFont(QFont('Poppins', 14))
        subheader_label.setStyleSheet("color: #CCCCCC; margin-bottom: 15px;")
        subheader_label.setAlignment(Qt.AlignCenter)
        
        # Form layout
        form_container = QFrame()
        form_container.setObjectName("form_container")
        form_container.setStyleSheet("""
            #form_container {
                background-color: rgba(25, 25, 25, 0.7);
                border-radius: 15px;
                padding: 30px;
                border: 1px solid rgba(80, 80, 80, 0.2);
            }
        """)
        
        # Add shadow to form container
        form_shadow = QGraphicsDropShadowEffect()
        form_shadow.setBlurRadius(20)
        form_shadow.setColor(QColor(0, 0, 0, 100))
        form_shadow.setOffset(0, 5)
        form_container.setGraphicsEffect(form_shadow)
        
        form_layout = QVBoxLayout(form_container)
        form_layout.setSpacing(20)
        
        # Username
        username_label = QLabel('Username')
        username_label.setStyleSheet("font-weight: bold; color: #DDDDDD; font-size: 14px; letter-spacing: 0.5px;")
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Masukkan username Anda")
        self.username_input.setStyleSheet("""
            QLineEdit {
                padding: 15px;
                border: 1px solid #444444;
                border-radius: 8px;
                font-size: 14px;
                background-color: rgba(40, 40, 40, 0.7);
            }
            QLineEdit:hover {
                background-color: rgba(50, 50, 50, 0.8);
                border: 1px solid #555555;
            }
            QLineEdit:focus {
                background-color: rgba(60, 60, 60, 0.9);
                border: 1px solid #FFD700;
            }
        """)
        
        # Password
        password_label = QLabel('Password')
        password_label.setStyleSheet("font-weight: bold; color: #DDDDDD; font-size: 14px; letter-spacing: 0.5px;")
        
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Masukkan password Anda")
        self.password_input.setStyleSheet("""
            QLineEdit {
                padding: 15px;
                border: 1px solid #444444;
                border-radius: 8px;
                font-size: 14px;
                background-color: rgba(40, 40, 40, 0.7);
            }
            QLineEdit:hover {
                background-color: rgba(50, 50, 50, 0.8);
                border: 1px solid #555555;
            }
            QLineEdit:focus {
                background-color: rgba(60, 60, 60, 0.9);
                border: 1px solid #FFD700;
            }
        """)
        
        # Add to form layout
        form_layout.addWidget(username_label)
        form_layout.addWidget(self.username_input)
        form_layout.addWidget(password_label)
        form_layout.addWidget(self.password_input)
        
        # Buttons
        button_layout = QVBoxLayout()
        button_layout.setSpacing(20)
        
        login_button = QPushButton('Login')
        login_button.setCursor(Qt.PointingHandCursor)
        login_button.setStyleSheet("""
            QPushButton {
                background-color: #FFD700;
                color: #121212;
                border: none;
                border-radius: 8px;
                padding: 15px;
                font-size: 16px;
                font-weight: bold;
                letter-spacing: 1px;
            }
            QPushButton:hover {
                background-color: #F5CB0C;
            }
            QPushButton:pressed {
                background-color: #E6C000;
            }
        """)
        # Add shadow effect to login button
        login_shadow = QGraphicsDropShadowEffect()
        login_shadow.setBlurRadius(15)
        login_shadow.setColor(QColor(0, 0, 0, 77))
        login_shadow.setOffset(0, 5)
        login_button.setGraphicsEffect(login_shadow)
        
        login_button.clicked.connect(self.handle_login)
        
        register_layout = QHBoxLayout()
        register_layout.setAlignment(Qt.AlignCenter)
        
        register_label = QLabel('Belum memiliki akun?')
        register_label.setStyleSheet("color: #AAAAAA; font-size: 14px;")
        
        register_button = QPushButton('Daftar Sekarang')
        register_button.setCursor(Qt.PointingHandCursor)
        register_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #FFD700;
                border: none;
                padding: 5px;
                font-weight: bold;
                font-size: 14px;
                text-decoration: none;
                border-bottom: 1px solid transparent;
            }
            QPushButton:hover {
                color: #FFFFFF;
                border-bottom: 1px solid #FFD700;
            }
        """)
        register_button.clicked.connect(self.open_register)
        
        register_layout.addWidget(register_label)
        register_layout.addWidget(register_button)
        
        button_layout.addWidget(login_button)
        button_layout.addSpacing(10)
        button_layout.addLayout(register_layout)
        
        # Add everything to right panel
        right_layout.addLayout(header_layout)
        right_layout.addWidget(subheader_label)
        right_layout.addSpacing(30)
        right_layout.addWidget(form_container)
        right_layout.addSpacing(20)
        right_layout.addLayout(button_layout)
        right_layout.addStretch()
        
        # Add both panels to content layout
        content_layout.addWidget(left_panel)
        content_layout.addWidget(right_panel)
        
        # Add content container to main layout
        main_layout.addWidget(content_container)
        
        # Set focus on username input
        self.username_input.setFocus()
        
        # Animations for login button
        self.login_button_animation = QPropertyAnimation(login_button, b"geometry")
        self.login_button_animation.setDuration(150)
        self.login_button_animation.setEasingCurve(QEasingCurve.OutCubic)
        
    def handle_login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        
        # Validasi input
        if not username or not password:
            QMessageBox.warning(self, 'Error', 'Username dan password harus diisi')
            return
        
        # Proses login
        success, message, user_data = UserModel.login_user(username, password, self.bcrypt)
        
        if success:
            # Buka dashboard
            self.dashboard = DashboardWindow(user_data)
            self.dashboard.show()
            self.close()
        else:
            QMessageBox.warning(self, 'Login Gagal', message)
    
    def open_register(self):
        self.register_window = RegisterWindow(self.bcrypt)
        self.register_window.show()
        self.close() 