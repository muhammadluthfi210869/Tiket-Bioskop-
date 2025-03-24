from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                          QPushButton, QFrame, QScrollArea, QSizePolicy, QGridLayout)
from PyQt5.QtGui import QFont, QPixmap, QIcon
from PyQt5.QtCore import Qt, pyqtSignal
import os

class MovieDetailPage(QWidget):
    """Halaman untuk menampilkan detail film"""
    
    back_to_movies = pyqtSignal()
    book_movie = pyqtSignal(dict)
    
    def __init__(self, user_data=None):
        super().__init__()
        self.user_data = user_data
        self.current_movie = None
        self.init_ui()
        
    def init_ui(self):
        # Layout utama
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(30)
        
        # Header dengan tombol kembali
        header_layout = QHBoxLayout()
        
        # Tombol kembali
        self.back_button = QPushButton("← Kembali ke Daftar Film")
        self.back_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #121212;
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
        
        header_layout.addWidget(self.back_button)
        header_layout.addStretch()
        
        main_layout.addLayout(header_layout)
        
        # Container untuk konten
        content_container = QWidget()
        content_container.setObjectName("content_container")
        content_container.setStyleSheet("""
            #content_container {
                background-color: #FFFFFF;
                border-radius: 10px;
            }
        """)
        
        content_layout = QVBoxLayout(content_container)
        content_layout.setContentsMargins(30, 30, 30, 30)
        content_layout.setSpacing(20)
        
        # Informasi film
        info_container = QWidget()
        info_layout = QHBoxLayout(info_container)
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(30)
        
        # Poster film
        self.poster_label = QLabel()
        self.poster_label.setFixedSize(300, 450)
        self.poster_label.setStyleSheet("""
            QLabel {
                background-color: #000000;
                border-radius: 10px;
            }
        """)
        info_layout.addWidget(self.poster_label)
        
        # Detail film
        detail_container = QWidget()
        detail_layout = QVBoxLayout(detail_container)
        detail_layout.setContentsMargins(0, 0, 0, 0)
        detail_layout.setSpacing(15)
        
        # Judul film
        self.title_label = QLabel()
        self.title_label.setStyleSheet("""
            QLabel {
                color: #000000;
                font-size: 24px;
                font-weight: bold;
                font-family: 'Montserrat';
            }
        """)
        detail_layout.addWidget(self.title_label)
        
        # Genre dan durasi
        self.info_label = QLabel()
        self.info_label.setStyleSheet("""
            QLabel {
                color: #666666;
                font-size: 16px;
                font-family: 'Montserrat';
            }
        """)
        detail_layout.addWidget(self.info_label)
        
        # Sinopsis
        synopsis_label = QLabel("Sinopsis")
        synopsis_label.setStyleSheet("""
            QLabel {
                color: #000000;
                font-size: 18px;
                font-weight: bold;
                font-family: 'Montserrat';
                margin-top: 20px;
            }
        """)
        detail_layout.addWidget(synopsis_label)
        
        self.synopsis_text = QLabel()
        self.synopsis_text.setWordWrap(True)
        self.synopsis_text.setStyleSheet("""
            QLabel {
                color: #333333;
                font-size: 14px;
                font-family: 'Montserrat';
                line-height: 1.5;
            }
        """)
        detail_layout.addWidget(self.synopsis_text)
        
        # Jadwal
        schedule_label = QLabel("Jadwal Tayang")
        schedule_label.setStyleSheet("""
            QLabel {
                color: #000000;
                font-size: 18px;
                font-weight: bold;
                font-family: 'Montserrat';
                margin-top: 20px;
            }
        """)
        detail_layout.addWidget(schedule_label)
        
        self.schedule_list = QLabel()
        self.schedule_list.setStyleSheet("""
            QLabel {
                color: #333333;
                font-size: 14px;
                font-family: 'Montserrat';
            }
        """)
        detail_layout.addWidget(self.schedule_list)
        
        # Harga
        self.price_label = QLabel()
        self.price_label.setStyleSheet("""
            QLabel {
                color: #000000;
                font-size: 20px;
                font-weight: bold;
                font-family: 'Montserrat';
                margin-top: 20px;
            }
        """)
        detail_layout.addWidget(self.price_label)
        
        # Tombol booking
        self.book_button = QPushButton("Pesan Tiket")
        self.book_button.setCursor(Qt.PointingHandCursor)
        self.book_button.setStyleSheet("""
            QPushButton {
                background-color: #FFD700;
                color: #000000;
                border: none;
                border-radius: 5px;
                padding: 15px 30px;
                font-weight: bold;
                font-family: 'Montserrat';
                font-size: 16px;
                margin-top: 20px;
            }
            QPushButton:hover {
                background-color: #F5CB0C;
            }
            QPushButton:pressed {
                background-color: #E6C000;
            }
        """)
        self.book_button.clicked.connect(self.on_book_clicked)
        detail_layout.addWidget(self.book_button)
        
        detail_layout.addStretch()
        info_layout.addWidget(detail_container)
        
        content_layout.addWidget(info_container)
        main_layout.addWidget(content_container)
    
    def display_movie_detail(self, movie_data):
        """Menampilkan detail film"""
        self.current_movie = movie_data
        
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
        else:
            # Default poster jika tidak ada
            default_poster = os.path.join("assets", "no_poster.jpg")
            if os.path.exists(default_poster):
                self.poster_label.setPixmap(QPixmap(default_poster))
        
        # Set informasi film
        self.title_label.setText(movie_data["title"])
        self.info_label.setText(f"{movie_data['genre']} • {movie_data['duration']} menit")
        self.synopsis_text.setText(movie_data.get("synopsis", "Tidak ada sinopsis tersedia."))
        
        # Format jadwal
        schedules = movie_data.get("schedule", [])
        if isinstance(schedules, list):
            schedule_text = ", ".join(schedules)
        else:
            schedule_text = schedules
        self.schedule_list.setText(schedule_text)
        
        # Format harga
        self.price_label.setText(f"Rp {movie_data['price']:,}".replace(',', '.'))
    
    def on_back_clicked(self):
        """Handler ketika tombol kembali diklik"""
        self.back_to_movies.emit()
    
    def on_book_clicked(self):
        """Handler ketika tombol booking diklik"""
        if self.current_movie:
            self.book_movie.emit(self.current_movie) 