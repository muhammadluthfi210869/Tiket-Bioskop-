from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QPushButton, QLabel, QFrame, QStackedWidget, QScrollArea,
                            QSizePolicy)
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt, QSize

# Impor halaman-halaman lain yang diperlukan
# from movies_page import MoviesPage
# from topup_page import TopupPage
# from history_page import HistoryPage
# from food_page import FoodPage

class DashboardWindow(QMainWindow):
    def __init__(self, user_data):
        super().__init__()
        self.user_data = user_data
        self.setWindowTitle("Sistem Pemesanan Tiket Bioskop")
        self.setGeometry(100, 100, 900, 600)
        self.init_ui()
        
    def init_ui(self):
        # Widget utama
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout utama
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # === NAVBAR DI SISI KIRI ===
        navbar_widget = QWidget()
        navbar_widget.setObjectName("navbar")
        navbar_widget.setFixedWidth(200)  # Lebar navbar
        navbar_layout = QVBoxLayout(navbar_widget)
        navbar_layout.setContentsMargins(0, 0, 0, 0)
        navbar_layout.setSpacing(0)
        
        # Judul aplikasi di navbar
        app_title = QLabel("CineTix")
        app_title.setObjectName("app_title")
        app_title.setAlignment(Qt.AlignCenter)
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(14)
        app_title.setFont(title_font)
        app_title.setStyleSheet("padding: 20px 0; background-color: #032541; color: white;")
        navbar_layout.addWidget(app_title)
        
        # Tombol-tombol navbar
        nav_buttons = [
            {"text": "Dashboard", "icon": "dashboard.png"},
            {"text": "Movies", "icon": "movie.png"},
            {"text": "Top-Up Saldo", "icon": "wallet.png"},
            {"text": "Riwayat", "icon": "history.png"},
            {"text": "Pesan Makanan", "icon": "food.png"}
        ]
        
        self.nav_button_list = []
        
        for i, button_info in enumerate(nav_buttons):
            button = QPushButton(button_info["text"])
            button.setObjectName(f"nav_button_{i}")
            
            # Coba tambahkan ikon jika ada
            try:
                button.setIcon(QIcon(f"assets/icons/{button_info['icon']}"))
                button.setIconSize(QSize(20, 20))
            except:
                pass  # Jika ikon tidak ditemukan, lanjutkan tanpa ikon
                
            button.setCheckable(True)
            button.setStyleSheet("""
                QPushButton {
                    text-align: left;
                    padding: 12px 15px;
                    border: none;
                    color: white;
                    background-color: #1a3b5d;
                }
                QPushButton:checked, QPushButton:hover {
                    background-color: #01b4e4;
                }
            """)
            
            # Tambahkan fungsi on_click ke setiap tombol
            button.clicked.connect(lambda checked, index=i: self.switch_page(index))
            
            navbar_layout.addWidget(button)
            self.nav_button_list.append(button)
        
        # Spacer untuk mengisi space kosong
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        navbar_layout.addWidget(spacer)
        
        # Tombol logout di bagian bawah navbar
        logout_button = QPushButton("Logout")
        logout_button.setObjectName("logout_button")
        logout_button.setStyleSheet("""
            QPushButton {
                text-align: center;
                padding: 12px 15px;
                border: none;
                color: white;
                background-color: #e74c3c;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        logout_button.clicked.connect(self.logout)
        navbar_layout.addWidget(logout_button)
        
        # === AREA KONTEN ===
        content_widget = QWidget()
        content_widget.setObjectName("content")
        content_layout = QVBoxLayout(content_widget)
        
        # Stack widget untuk menampilkan halaman-halaman berbeda
        self.stack_widget = QStackedWidget()
        
        # Halaman Dashboard
        dashboard_page = QWidget()
        dashboard_layout = QVBoxLayout(dashboard_page)
        
        # Judul Dashboard
        dashboard_title = QLabel("Dashboard")
        dashboard_title.setObjectName("page_title")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(18)
        dashboard_title.setFont(title_font)
        dashboard_layout.addWidget(dashboard_title)
        
        # Konten Dashboard
        welcome_label = QLabel(f"Selamat datang, {self.user_data['nama']}!")
        welcome_label.setStyleSheet("font-size: 16px; margin: 10px 0;")
        dashboard_layout.addWidget(welcome_label)
        
        # Informasi Pengguna
        info_frame = QFrame()
        info_frame.setFrameShape(QFrame.StyledPanel)
        info_frame.setStyleSheet("background-color: #f8f9fa; padding: 15px; border-radius: 5px;")
        info_layout = QVBoxLayout(info_frame)
        
        info_title = QLabel("Informasi Pengguna:")
        info_title.setStyleSheet("font-weight: bold; font-size: 14px;")
        info_layout.addWidget(info_title)
        
        username_label = QLabel(f"Username: {self.user_data['username']}")
        info_layout.addWidget(username_label)
        
        usia_label = QLabel(f"Usia: {self.user_data['usia']} tahun")
        info_layout.addWidget(usia_label)
        
        genre_label = QLabel(f"Genre Favorit: {self.user_data['genre_favorit']}")
        info_layout.addWidget(genre_label)
        
        dashboard_layout.addWidget(info_frame)
        
        # Pesan tentang fitur yang akan datang
        note_label = QLabel("Fitur pemesanan tiket akan segera hadir")
        note_label.setStyleSheet("font-style: italic; color: #666; margin-top: 20px;")
        note_label.setAlignment(Qt.AlignCenter)
        dashboard_layout.addWidget(note_label)
        
        # Tambahkan spacer
        dashboard_layout.addStretch()
        
        # Tambahkan halaman ke stack widget
        self.stack_widget.addWidget(dashboard_page)
        
        # Tambahkan placeholder untuk halaman lain
        for i in range(4):  # 4 halaman lainnya
            placeholder = QWidget()
            placeholder_layout = QVBoxLayout(placeholder)
            placeholder_label = QLabel(f"Halaman {nav_buttons[i+1]['text']} dalam pengembangan")
            placeholder_label.setAlignment(Qt.AlignCenter)
            placeholder_layout.addWidget(placeholder_label)
            self.stack_widget.addWidget(placeholder)
        
        content_layout.addWidget(self.stack_widget)
        
        # Tambahkan navbar dan content ke layout utama
        main_layout.addWidget(navbar_widget)
        main_layout.addWidget(content_widget)
        
        # Atur halaman awal dan tombol yang aktif
        self.stack_widget.setCurrentIndex(0)
        self.nav_button_list[0].setChecked(True)
        
        # Set window stylesheet
        self.setStyleSheet("""
            QMainWindow {
                background-color: white;
            }
            #content {
                background-color: white;
                padding: 20px;
            }
            #navbar {
                background-color: #1a3b5d;
            }
        """)
    
    def switch_page(self, index):
        # Ubah halaman yang aktif
        self.stack_widget.setCurrentIndex(index)
        
        # Ubah tombol yang aktif
        for i, button in enumerate(self.nav_button_list):
            button.setChecked(i == index)
    
    def logout(self):
        # Tutup window dashboard
        self.close()
        
        # Di sini Anda dapat menambahkan kode untuk kembali ke halaman login
        # Contoh:
        # from login_window import LoginWindow
        # self.login_window = LoginWindow()
        # self.login_window.show()

# Jika file ini dijalankan langsung (untuk testing)
if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    # Data contoh untuk pengujian
    user_data = {
        "nama": "luthfi",
        "username": "luthfi",
        "usia": 18,
        "genre_favorit": "Action"
    }
    
    window = DashboardWindow(user_data)
    window.show()
    
    sys.exit(app.exec_()) 