from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QPushButton, QMessageBox,
                             QSpinBox, QComboBox, QFrame, QGraphicsDropShadowEffect)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QSize
from PyQt5.QtGui import QFont, QPixmap, QIcon, QColor, QPalette, QBrush
import os

from models import UserModel

class RegisterWindow(QMainWindow):
    def __init__(self, bcrypt):
        super().__init__()
        self.bcrypt = bcrypt
        self.genre_list = ['Action', 'Biography', 'Drama', 'Sci-Fi']
        self.init_ui()
        
    def init_ui(self):
        # Set window properties
        self.setWindowTitle('CinemaTIX - Pendaftaran Akun')
        self.setGeometry(300, 300, 900, 600)
        
        # Load background image if available
        bg_image_path = os.path.join("assets", "bg_cinema.jpg")
        if os.path.exists(bg_image_path):
            # Set background image
            palette = QPalette()
            pixmap = QPixmap(bg_image_path)
            # Apply blur effect through style
            palette.setBrush(QPalette.Window, QBrush(pixmap))
            self.setPalette(palette)
        
        # Global stylesheet
        self.setStyleSheet("""
            QMainWindow {
                background-color: #121212;
            }
            QLabel {
                font-family: 'Poppins', 'Montserrat', sans-serif;
                color: #FFFFFF;
            }
            QLineEdit {
                padding: 15px;
                border: 1px solid #333333;
                border-radius: 8px;
                font-family: 'Poppins', 'Montserrat', sans-serif;
                background-color: rgba(30, 30, 30, 0.8);
                color: #FFFFFF;
                selection-background-color: #FFD700;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 1px solid #FFD700;
                background-color: rgba(40, 40, 40, 0.9);
            }
            QLineEdit::placeholder {
                color: #999999;
            }
            QPushButton {
                font-family: 'Poppins', 'Montserrat', sans-serif;
                font-weight: bold;
            }
            QSpinBox, QComboBox {
                padding: 15px;
                border: 1px solid #333333;
                border-radius: 8px;
                font-family: 'Poppins', 'Montserrat', sans-serif;
                background-color: rgba(30, 30, 30, 0.8);
                color: #FFFFFF;
                selection-background-color: #FFD700;
                font-size: 14px;
            }
            QSpinBox:focus, QComboBox:focus {
                border: 1px solid #FFD700;
                background-color: rgba(40, 40, 40, 0.9);
            }
            QComboBox::drop-down {
                border: 0px;
                width: 30px;
            }
            QComboBox::down-arrow {
                image: url(assets/icons/dropdown.png);
                width: 12px;
                height: 12px;
            }
            QComboBox QAbstractItemView {
                border: 1px solid #444444;
                selection-background-color: #FFD700;
                selection-color: #121212;
                background-color: #1E1E1E;
                color: #FFFFFF;
                outline: none;
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
        left_panel.setFixedWidth(350)
        
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
                text-shadow: 0px 2px 4px rgba(0, 0, 0, 0.5);
            }
        """)
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
                    text-shadow: 0px 2px 10px rgba(0, 0, 0, 0.7);
                }
            """)
        
        left_layout.addStretch(1)
        left_layout.addWidget(cinema_icon)
        left_layout.addWidget(logo_label)
        left_layout.addWidget(tagline_label)
        left_layout.addStretch(1)
        
        # Right panel - Register Form
        right_panel = QWidget()
        right_panel.setObjectName("right_panel")
        right_panel.setStyleSheet("""
            #right_panel {
                background-color: rgba(18, 18, 18, 0.9);
                border-top-right-radius: 20px;
                border-bottom-right-radius: 20px;
            }
        """)
        
        # Create scroll area for potentially longer form
        scroll_layout = QVBoxLayout(right_panel)
        scroll_layout.setContentsMargins(50, 50, 50, 50)
        scroll_layout.setSpacing(20)
        
        # Header with icon
        header_layout = QHBoxLayout()
        header_layout.setAlignment(Qt.AlignCenter)
        
        register_icon = QLabel("✨")
        register_icon.setStyleSheet("font-size: 28px; margin-right: 10px;")
        
        header_label = QLabel('Daftar Akun Baru')
        header_label.setFont(QFont('Poppins', 28, QFont.Bold))
        header_label.setStyleSheet("""
            color: #FFFFFF; 
            margin-bottom: 5px; 
            letter-spacing: 1px;
            text-shadow: 0px 2px 4px rgba(0, 0, 0, 0.3);
        """)
        
        header_layout.addWidget(register_icon)
        header_layout.addWidget(header_label)
        
        subheader_label = QLabel('Lengkapi data diri Anda untuk membuat akun')
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
        
        # Organize form in 2 columns to save space
        form_upper_layout = QHBoxLayout()
        form_upper_layout.setSpacing(15)
        
        # Left column - Personal info
        left_col_layout = QVBoxLayout()
        left_col_layout.setSpacing(15)
        
        # Nama
        nama_label = QLabel('Nama Lengkap')
        nama_label.setStyleSheet("font-weight: bold; color: #DDDDDD; font-size: 14px; letter-spacing: 0.5px;")
        
        self.nama_input = QLineEdit()
        self.nama_input.setPlaceholderText("Masukkan nama lengkap Anda")
        self.nama_input.setStyleSheet("""
            QLineEdit {
                padding: 15px;
                border: 1px solid #444444;
                border-radius: 8px;
                font-size: 14px;
                background-color: rgba(40, 40, 40, 0.7);
            }
        """)
        
        # Usia - using QSpinBox to ensure integer input
        usia_label = QLabel('Usia')
        usia_label.setStyleSheet("font-weight: bold; color: #DDDDDD; font-size: 14px; letter-spacing: 0.5px;")
        
        self.usia_input = QSpinBox()
        self.usia_input.setRange(1, 120)  # Reasonable age range
        self.usia_input.setValue(18)  # Default value
        self.usia_input.setStyleSheet("""
            QSpinBox {
                padding: 15px;
                border: 1px solid #444444;
                border-radius: 8px;
                font-size: 14px;
                background-color: rgba(40, 40, 40, 0.7);
                color: #FFFFFF;
                min-height: 20px;
            }
        """)
        
        # Add to left column
        left_col_layout.addWidget(nama_label)
        left_col_layout.addWidget(self.nama_input)
        left_col_layout.addWidget(usia_label)
        left_col_layout.addWidget(self.usia_input)
        
        # Right column - Account info
        right_col_layout = QVBoxLayout()
        right_col_layout.setSpacing(15)
        
        # Genre Favorit - using QComboBox for dropdown list
        genre_label = QLabel('Genre Film Favorit')
        genre_label.setStyleSheet("font-weight: bold; color: #DDDDDD; font-size: 14px; letter-spacing: 0.5px;")
        
        self.genre_input = QComboBox()
        self.genre_input.addItems(self.genre_list)
        self.genre_input.setStyleSheet("""
            QComboBox {
                padding: 15px;
                border: 1px solid #444444;
                border-radius: 8px;
                font-size: 14px;
                background-color: rgba(40, 40, 40, 0.7);
                color: #FFFFFF;
                min-height: 20px;
            }
        """)
        
        # Add to right column
        right_col_layout.addWidget(genre_label)
        right_col_layout.addWidget(self.genre_input)
        
        # Add columns to upper layout
        form_upper_layout.addLayout(left_col_layout)
        form_upper_layout.addLayout(right_col_layout)
        
        # Add upper layout to form
        form_layout.addLayout(form_upper_layout)
        
        # Account section divider
        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        divider.setStyleSheet("background-color: #444444; min-height: 1px; margin: 5px 0;")
        form_layout.addWidget(divider)
        
        # Account credentials section header
        account_header = QLabel("Informasi Akun")
        account_header.setStyleSheet("color: #FFD700; font-size: 16px; font-weight: bold; margin-top: 5px;")
        form_layout.addWidget(account_header)
        
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
        """)
        
        # Add account fields
        form_layout.addWidget(username_label)
        form_layout.addWidget(self.username_input)
        form_layout.addWidget(password_label)
        form_layout.addWidget(self.password_input)
        
        # Buttons
        button_layout = QVBoxLayout()
        button_layout.setSpacing(20)
        
        register_button = QPushButton('Daftar Akun')
        register_button.setCursor(Qt.PointingHandCursor)
        register_button.setStyleSheet("""
            QPushButton {
                background-color: #FFD700;
                color: #000000;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
                min-width: 100px;
            }
        """)
        register_button.clicked.connect(self.handle_register)
        
        login_layout = QHBoxLayout()
        login_layout.setAlignment(Qt.AlignCenter)
        
        login_label = QLabel('Sudah memiliki akun?')
        login_label.setStyleSheet("color: #AAAAAA; font-size: 14px;")
        
        back_button = QPushButton('Login Sekarang')
        back_button.setCursor(Qt.PointingHandCursor)
        back_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #007bff;
                border: none;
                text-decoration: underline;
            }
        """)
        back_button.clicked.connect(self.back_to_login)
        
        login_layout.addWidget(login_label)
        login_layout.addWidget(back_button)
        
        button_layout.addWidget(register_button)
        button_layout.addSpacing(10)
        button_layout.addLayout(login_layout)
        
        # Add everything to right panel
        scroll_layout.addLayout(header_layout)
        scroll_layout.addWidget(subheader_label)
        scroll_layout.addSpacing(20)
        scroll_layout.addWidget(form_container)
        scroll_layout.addSpacing(20)
        scroll_layout.addLayout(button_layout)
        scroll_layout.addStretch()
        
        # Add both panels to content layout
        content_layout.addWidget(left_panel)
        content_layout.addWidget(right_panel)
        
        # Add content container to main layout
        main_layout.addWidget(content_container)
        
        # Set focus on nama input
        self.nama_input.setFocus()
        
        # Animations for register button
        self.register_button_animation = QPropertyAnimation(register_button, b"geometry")
        self.register_button_animation.setDuration(150)
        self.register_button_animation.setEasingCurve(QEasingCurve.OutCubic)
    
    def handle_register(self):
        nama = self.nama_input.text()
        username = self.username_input.text()
        password = self.password_input.text()
        usia = self.usia_input.value()
        genre_favorit = self.genre_input.currentText()
        
        # Validasi input
        if not all([nama, username, password]):
            QMessageBox.warning(self, 'Error', 'Semua field harus diisi')
            return
        
        # Proses registrasi
        success, message = UserModel.register_user(nama, username, password, usia, genre_favorit, self.bcrypt)
        
        if success:
            QMessageBox.information(self, 'Registrasi Berhasil', message)
            self.back_to_login()
        else:
            QMessageBox.warning(self, 'Registrasi Gagal', message)
    
    def back_to_login(self):
        from gui.login_window import LoginWindow
        self.login_window = LoginWindow(self.bcrypt)
        self.login_window.show()
        self.close() 