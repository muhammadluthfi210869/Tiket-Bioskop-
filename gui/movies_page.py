from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                          QLineEdit, QComboBox, QScrollArea, QFrame, QPushButton,
                          QGridLayout, QSizePolicy, QStackedWidget, QMessageBox, QFileDialog)
from PyQt5.QtGui import QFont, QPixmap, QIcon, QPainter, QColor
from PyQt5.QtCore import Qt, QSize, pyqtSignal, QDateTime, QRectF, QPoint
import os
import time
import traceback
import qrcode
from PIL import Image
import io
from datetime import datetime

from gui.movie_detail_page import MovieDetailPage
from gui.booking_page import BookingPage
from gui.ticket_page import TicketPage
from utils.helper import find_poster_for_film
from models import MovieModel

class ClickableLabel(QLabel):
    """Label yang bisa diklik"""
    clicked = pyqtSignal()
    
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        
    def mousePressEvent(self, event):
        self.clicked.emit()
        super().mousePressEvent(event)

class MovieCard(QWidget):
    """Widget untuk menampilkan informasi film dalam bentuk kartu"""
    
    book_clicked = pyqtSignal(dict)
    movie_clicked = pyqtSignal(dict)
    
    def __init__(self, movie_data, parent=None):
        super().__init__(parent)
        self.movie_data = movie_data
        self.init_ui()
        
    def init_ui(self):
        # Layout Utama
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Container Card
        card_container = QFrame(self)
        card_container.setObjectName("card_container")
        card_container.setStyleSheet("""
            #card_container {
                background-color: #2D2D2D;
                border-radius: 10px;
                border: none;
            }
            #card_container:hover {
                background-color: #363636;
            }
        """)
        
        card_layout = QVBoxLayout(card_container)
        card_layout.setContentsMargins(0, 0, 0, 0)
        card_layout.setSpacing(0)
        
        # Poster Container
        poster_container = QFrame()
        poster_container.setFixedWidth(200)
        poster_container.setFixedHeight(300)
        poster_container.setCursor(Qt.PointingHandCursor)
        poster_layout = QVBoxLayout(poster_container)
        poster_layout.setContentsMargins(0, 0, 0, 0)
        
        self.poster_label = ClickableLabel()
        self.poster_label.setCursor(Qt.PointingHandCursor)
        self.poster_label.setFixedSize(200, 300)
        self.poster_label.setAlignment(Qt.AlignCenter)
        self.poster_label.clicked.connect(self.on_movie_clicked)
        self.poster_label.setStyleSheet("""
            QLabel {
                background-color: #1E1E1E;
                border-top-left-radius: 10px;
                border-top-right-radius: 10px;
            }
        """)
        
        # Cari dan set poster image
        poster_path = self.movie_data.get("poster_path")
        print(f"Setting poster for {self.movie_data.get('title')}, path: {poster_path}")
        if poster_path and os.path.exists(poster_path):
            print(f"Poster file exists: {poster_path}")
            pixmap = QPixmap(poster_path)
            # Scale poster dengan mempertahankan aspect ratio
            pixmap = pixmap.scaled(200, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        else:
            if poster_path:
                print(f"Poster file does not exist: {poster_path}")
            else:
                print(f"No poster path provided for {self.movie_data.get('title')}")
            # Default poster jika tidak ada
            default_poster = os.path.join("assets", "no_poster.jpg")
            print(f"Using default poster: {default_poster}")
            # Jika default poster tidak ditemukan, gunakan poster yang pasti ada
            if not os.path.exists(default_poster):
                # Gunakan salah satu poster yang pasti ada sebagai fallback
                backup_posters = [
                    os.path.join("assets", "avenger.jpg"),
                    os.path.join("assets", "Dark-night.jpg"),
                    os.path.join("assets", "joker.jpg")
                ]
                
                for backup in backup_posters:
                    if os.path.exists(backup):
                        print(f"Using backup poster: {backup}")
                        pixmap = QPixmap(backup)
                        pixmap = pixmap.scaled(200, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                        break
                else:
                    # Jika semua backup tidak ada, buat pixmap kosong
                    print("All backup posters not found, creating blank pixmap")
                    pixmap = QPixmap(200, 300)
                    pixmap.fill(Qt.black)
            else:
                pixmap = QPixmap(default_poster)
                pixmap = pixmap.scaled(200, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        
        self.poster_label.setPixmap(pixmap)
        
        # Info Container
        info_container = QWidget()
        info_container.setCursor(Qt.PointingHandCursor)
        info_container.setStyleSheet("""
            QWidget {
                background-color: #2D2D2D;
                border-bottom-left-radius: 10px;
                border-bottom-right-radius: 10px;
            }
        """)
        
        info_layout = QVBoxLayout(info_container)
        info_layout.setContentsMargins(15, 15, 15, 15)
        info_layout.setSpacing(8)
        
        # Movie Title
        self.title_label = ClickableLabel(self.movie_data["title"])
        self.title_label.setCursor(Qt.PointingHandCursor)
        self.title_label.setStyleSheet("""
            QLabel {
                color: #FFFFFF;
                font-weight: bold;
                font-size: 16px;
                font-family: 'Montserrat';
            }
        """)
        
        # Duration and Genre
        movie_details = QWidget()
        movie_details.setCursor(Qt.PointingHandCursor)
        details_layout = QHBoxLayout(movie_details)
        details_layout.setContentsMargins(0, 0, 0, 0)
        details_layout.setSpacing(5)
        
        duration_label = QLabel(f"{self.movie_data['duration']} menit")
        duration_label.setStyleSheet("""
            QLabel {
                color: #CCCCCC;
                font-size: 12px;
                font-family: 'Montserrat';
            }
        """)
        
        separator = QLabel("•")
        separator.setStyleSheet("color: #CCCCCC;")
        
        genre_label = QLabel(self.movie_data["genre"])
        genre_label.setStyleSheet("""
            QLabel {
                color: #CCCCCC;
                font-size: 12px;
                font-family: 'Montserrat';
            }
        """)
        
        details_layout.addWidget(duration_label)
        details_layout.addWidget(separator)
        details_layout.addWidget(genre_label)
        details_layout.addStretch()
        
        # Price
        price_label = QLabel(f"Rp {self.movie_data['price']:,}".replace(',', '.'))
        price_label.setAlignment(Qt.AlignRight)
        price_label.setStyleSheet("""
            QLabel {
                color: #FFFFFF;
                font-weight: bold;
                font-size: 14px;
                font-family: 'Montserrat';
            }
        """)
        
        # Book Button
        self.book_button = QPushButton("Book")
        self.book_button.setCursor(Qt.PointingHandCursor)
        self.book_button.setStyleSheet("""
            QPushButton {
                background-color: #FFD700;
                color: #000000;
                border: none;
                border-radius: 5px;
                padding: 8px;
                font-weight: bold;
                font-family: 'Montserrat';
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #F5CB0C;
            }
            QPushButton:pressed {
                background-color: #E6C000;
            }
        """)
        
        # Add all elements
        info_layout.addWidget(self.title_label)
        info_layout.addWidget(movie_details)
        info_layout.addWidget(price_label)
        info_layout.addWidget(self.book_button)
        
        # Add to main layout
        card_layout.addWidget(self.poster_label)
        card_layout.addWidget(info_container)
        main_layout.addWidget(card_container)
        
        # Set cursor dan effect
        self.setMouseTracking(True)
        
    def on_book_clicked(self):
        """Handler ketika tombol booking diklik"""
        self.book_clicked.emit(self.movie_data)
    
    def on_movie_clicked(self):
        """Handler ketika kartu film diklik"""
        self.movie_clicked.emit(self.movie_data)
        
    def enterEvent(self, event):
        """Effect ketika mouse masuk area widget"""
        self.setStyleSheet("background-color: transparent;")
        
    def leaveEvent(self, event):
        """Effect ketika mouse keluar area widget"""
        self.setStyleSheet("background-color: transparent;")

class MoviesPage(QWidget):
    """Halaman untuk menampilkan daftar film"""
    
    movie_booked = pyqtSignal(dict)
    switch_page_signal = pyqtSignal(str, dict)
    ticket_purchased = pyqtSignal(dict)
    
    def __init__(self, user_data=None):
        """Initialize MoviesPage with user data if available"""
        super().__init__()
        self.user_data = user_data
        self.current_movie = None  # Simpan data film yang sedang diproses
        self.all_movies = []  # Simpan semua film untuk filtering
        self.genre_filters = []  # Simpan genre yang dipilih
        
        # Dictionary untuk menyimpan indeks dari setiap halaman
        self.pages = {}
        
        self.init_ui()
        self.load_movies()
        
        # Initialize other pages
        self.movie_detail_page = MovieDetailPage(self.user_data)
        self.movie_detail_page.back_to_movies.connect(self.show_movies_list)
        self.movie_detail_page.book_movie.connect(self.show_booking_page)
        self.stack_widget.addWidget(self.movie_detail_page)
        self.pages["movie_detail"] = self.stack_widget.count() - 1
        
        self.booking_page = BookingPage(self.user_data)
        self.booking_page.back_to_detail.connect(self.show_movie_detail)
        self.booking_page.booking_confirmed.connect(self.handle_booking_confirmed)
        self.booking_page.payment_processed.connect(self.handle_payment_processed)
        self.stack_widget.addWidget(self.booking_page)
        self.pages["booking"] = self.stack_widget.count() - 1
        
        self.ticket_page = TicketPage(self.user_data)
        self.ticket_page.back_to_movies.connect(self.show_movies_list)
        # Tambahkan signal show_history untuk menampilkan history setelah melihat e-ticket
        if hasattr(self, 'switch_page_signal'):
            self.ticket_page.show_history.connect(lambda: self.switch_page_signal.emit("show_history", {}))
        self.stack_widget.addWidget(self.ticket_page)
        self.pages["ticket"] = self.stack_widget.count() - 1
        
        # Show movies list initially
        self.show_movies_list()
        
    def handle_booking_confirmed(self, ticket_data):
        """Handle booking confirmation and show e-ticket"""
        # Show e-ticket
        self.show_e_ticket(ticket_data)
        # Show ticket page
        self.show_ticket_page(ticket_data)
        
    def handle_payment_processed(self, data):
        """Handle payment processing and update history"""
        # Update balance
        new_saldo = data.get("new_saldo", 0)
        if hasattr(self, 'switch_page_signal'):
            self.switch_page_signal.emit("update_saldo", {"new_saldo": new_saldo})
        
        # Reset ticket processed flag at the start of new transaction
        if hasattr(self, '_ticket_processed'):
            delattr(self, '_ticket_processed')
        
        # Emit ticket purchase for history only once
        ticket_data = data.get("ticket_data", {})
        if ticket_data and not hasattr(self, '_ticket_processed'):
            # Format data for history
            history_data = {
                "type": "Tiket",
                "movie_title": ticket_data.get("movie_title", ""),
                "total": -ticket_data.get("total_price", 0),  # Make sure it's negative for purchases
                "studio_type": ticket_data.get("studio_type", ""),
                "theater": ticket_data.get("theater", ""),
                "cinema": ticket_data.get("cinema", ""),
                "seats": ticket_data.get("seats", []),
                "show_date": ticket_data.get("show_date", ""),
                "show_time": ticket_data.get("show_time", ""),
                "status": "Sukses",
                "timestamp": QDateTime.currentDateTime().toString("dd/MM/yyyy HH:mm"),
                "total_price": ticket_data.get("total_price", 0)  # Add total_price explicitly
            }
            
            # Set the flag to prevent duplicate emissions
            self._ticket_processed = True
            
            # Emit the signal only once
            self.ticket_purchased.emit(history_data)
        
    def show_e_ticket(self, ticket_data):
        """Display e-ticket after successful booking"""
        try:
            # Create QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            
            # Add ticket data to QR code
            qr_data = f"""
            CinemaTIX E-Ticket
            Film: {ticket_data['movie_title']}
            Bioskop: {ticket_data['cinema']}
            Theater: {ticket_data['theater']}
            Studio: {ticket_data['studio_type']}
            Tanggal: {ticket_data['show_date']}
            Waktu: {ticket_data['show_time']}
            Kursi: {', '.join(ticket_data['seats'])}
            """
            qr.add_data(qr_data)
            qr.make(fit=True)
            
            # Create QR code image
            qr_img = qr.make_image(fill_color="black", back_color="white")
            
            # Convert PIL image to QPixmap
            qr_bytes = io.BytesIO()
            qr_img.save(qr_bytes, format='PNG')
            qr_bytes = qr_bytes.getvalue()
            
            qr_pixmap = QPixmap()
            qr_pixmap.loadFromData(qr_bytes)
            qr_pixmap = qr_pixmap.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            
            # Create e-ticket image
            ticket_width = 800
            ticket_height = 600
            ticket_pixmap = QPixmap(ticket_width, ticket_height)
            ticket_pixmap.fill(QColor("#1A1A1A"))
            
            # Setup painter
            painter = QPainter(ticket_pixmap)
            painter.setRenderHint(QPainter.Antialiasing)
            
            # Draw border
            painter.setPen(QColor("#FFD700"))
            painter.drawRect(10, 10, ticket_width-20, ticket_height-20)
            
            # Set font
            title_font = QFont("Montserrat", 24, QFont.Bold)
            header_font = QFont("Montserrat", 14, QFont.Bold)
            content_font = QFont("Montserrat", 12)
            
            # Draw title
            painter.setFont(title_font)
            painter.setPen(QColor("#FFD700"))
            painter.drawText(QRectF(0, 40, ticket_width, 50), Qt.AlignCenter, "CinemaTIX E-Ticket")
            
            # Draw content
            painter.setFont(content_font)
            painter.setPen(QColor("white"))
            
            y_pos = 120
            line_height = 30
            
            # Draw movie details
            content_items = [
                ("Film", ticket_data['movie_title']),
                ("Bioskop", ticket_data['cinema']),
                ("Theater", ticket_data['theater']),
                ("Studio", ticket_data['studio_type']),
                ("Tanggal", ticket_data['show_date']),
                ("Waktu", ticket_data['show_time']),
                ("Kursi", ', '.join(ticket_data['seats'])),
                ("Total", f"Rp {ticket_data['total_price']:,}".replace(',', '.'))
            ]
            
            for label, value in content_items:
                painter.setFont(header_font)
                painter.setPen(QColor("#FFD700"))
                painter.drawText(50, y_pos, f"{label}:")
                
                painter.setFont(content_font)
                painter.setPen(QColor("white"))
                painter.drawText(200, y_pos, value)
                y_pos += line_height
            
            # Draw QR code
            qr_x = (ticket_width - qr_pixmap.width()) // 2
            qr_y = y_pos + 20
            painter.drawPixmap(qr_x, qr_y, qr_pixmap)
            
            # Draw footer text
            footer_y = qr_y + qr_pixmap.height() + 20
            painter.setFont(content_font)
            painter.setPen(QColor("white"))
            painter.drawText(QRectF(0, footer_y, ticket_width, 30), Qt.AlignCenter, "Silakan tunjukkan e-ticket ini kepada petugas bioskop")
            
            painter.end()
            
            # Save the ticket image
            downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"cinematix_ticket_{timestamp}.png"
            save_path = os.path.join(downloads_path, filename)
            
            ticket_pixmap.save(save_path, "PNG")
            
            # Create message box with custom layout
            msg = QMessageBox()
            msg.setWindowTitle("E-Ticket CinemaTIX")
            
            # Create a widget to hold the content
            content_widget = QWidget()
            content_layout = QVBoxLayout(content_widget)
            
            # Add save location text
            save_location = QLabel(f"E-Ticket telah berhasil disimpan di:\n{save_path}")
            save_location.setStyleSheet("color: #FFFFFF; font-family: 'Montserrat';")
            content_layout.addWidget(save_location)
            
            # Create and add ticket preview label
            ticket_label = QLabel()
            ticket_label.setPixmap(ticket_pixmap.scaled(600, 450, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            content_layout.addWidget(ticket_label)
            
            # Create download button
            download_button = QPushButton("Download E-Ticket")
            download_button.setStyleSheet("""
                QPushButton {
                    background-color: #FFD700;
                    color: #000000;
                    border: none;
                    border-radius: 5px;
                    padding: 10px 20px;
                    font-weight: bold;
                    font-family: 'Montserrat';
                    font-size: 12px;
                    min-width: 150px;
                }
                QPushButton:hover {
                    background-color: #FFC000;
                }
            """)
            
            def save_ticket():
                file_name, _ = QFileDialog.getSaveFileName(
                    msg,
                    "Save E-Ticket",
                    os.path.join(os.path.expanduser("~"), "Downloads", f"cinematix_ticket_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"),
                    "Images (*.png)"
                )
                if file_name:
                    ticket_pixmap.save(file_name, "PNG")
                    QMessageBox.information(msg, "Success", f"E-Ticket berhasil disimpan di:\n{file_name}")
            
            download_button.clicked.connect(save_ticket)
            content_layout.addWidget(download_button)
            
            # Set the content widget as the message box's layout
            msg.layout().addWidget(content_widget, 0, 0, 1, msg.layout().columnCount())
            
            msg.setStyleSheet("""
                QMessageBox {
                    background-color: #1A1A1A;
                }
                QMessageBox QLabel {
                    color: #FFFFFF;
                    font-family: 'Montserrat';
                }
                QMessageBox QPushButton {
                    background-color: #FFD700;
                    color: #000000;
                    border: none;
                    border-radius: 5px;
                    padding: 8px 16px;
                    font-weight: bold;
                    font-family: 'Montserrat';
                    font-size: 12px;
                }
                QMessageBox QPushButton:hover {
                    background-color: #FFC000;
                }
            """)
            
            msg.exec_()
            
        except Exception as e:
            print(f"Error generating e-ticket: {str(e)}")
            import traceback
            traceback.print_exc()
            
            # Show error message
            error_msg = QMessageBox()
            error_msg.setIcon(QMessageBox.Critical)
            error_msg.setWindowTitle("Error")
            error_msg.setText("Terjadi kesalahan saat membuat e-ticket")
            error_msg.setInformativeText(str(e))
            error_msg.exec_()
        
    def init_ui(self):
        """Initialize UI"""
        # Set window properties
        self.setObjectName("movies_page")
        self.setMinimumWidth(800)
        self.setMinimumHeight(600)
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Stack widget untuk menampilkan berbagai halaman
        self.stack_widget = QStackedWidget()
        layout.addWidget(self.stack_widget)
        
        # Halaman daftar film
        self.movies_list_page = QWidget()
        self.movies_list_page.setObjectName("movies_list_page")
        self.movies_list_page.setStyleSheet("""
            #movies_list_page {
                background-color: #1E1E1E;
            }
        """)
        
        # Layout untuk halaman daftar film
        movies_list_layout = QVBoxLayout(self.movies_list_page)
        movies_list_layout.setContentsMargins(0, 0, 0, 0)
        
        # Search and Filter Container
        search_filter_container = QWidget()
        search_filter_container.setObjectName("search_filter_container")
        search_filter_container.setStyleSheet("""
            #search_filter_container {
                background-color: #151515;
                border-bottom: 1px solid #2A2A2A;
                padding: 20px 40px;
            }
        """)
        
        search_filter_layout = QVBoxLayout(search_filter_container)
        search_filter_layout.setContentsMargins(0, 0, 0, 0)
        search_filter_layout.setSpacing(20)
        
        # Search Bar
        search_container = QWidget()
        search_layout = QHBoxLayout(search_container)
        search_layout.setContentsMargins(0, 0, 0, 0)
        
        search_icon = QLabel()
        search_icon_path = os.path.join("assets", "icons", "search.png")
        if os.path.exists(search_icon_path):
            search_pixmap = QPixmap(search_icon_path)
            search_icon.setPixmap(search_pixmap.scaled(20, 20, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Cari film...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                background-color: #2A2A2A;
                border: none;
                border-radius: 8px;
                padding: 12px;
                color: #FFFFFF;
                font-size: 14px;
                font-family: 'Poppins';
            }
            QLineEdit:focus {
                background-color: #333333;
            }
        """)
        self.search_input.textChanged.connect(self.filter_movies)
        
        search_layout.addWidget(search_icon)
        search_layout.addWidget(self.search_input)
        
        # Genre Filter Section
        genre_section = QWidget()
        genre_layout = QVBoxLayout(genre_section)
        genre_layout.setContentsMargins(0, 0, 0, 0)
        genre_layout.setSpacing(10)
        
        genre_title = QLabel("Filter Genre")
        genre_title.setStyleSheet("""
            QLabel {
                color: #FFFFFF;
                font-size: 16px;
                font-weight: 600;
                font-family: 'Poppins';
            }
        """)
        
        # Genre Checkboxes Container
        self.genre_container = QWidget()
        self.genre_container.setObjectName("genre_container")
        self.genre_container.setStyleSheet("""
            #genre_container {
                background-color: transparent;
            }
        """)
        
        self.genre_grid = QGridLayout(self.genre_container)
        self.genre_grid.setContentsMargins(0, 0, 0, 0)
        self.genre_grid.setSpacing(10)
        
        # Add all components to search filter container
        search_filter_layout.addWidget(search_container)
        search_filter_layout.addWidget(genre_title)
        search_filter_layout.addWidget(self.genre_container)
        
        # Buat scroll area untuk daftar film
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: #1E1E1E;
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
        
        # Widget untuk konten
        content_widget = QWidget()
        content_widget.setStyleSheet("""
            QWidget {
                background-color: #1E1E1E;
            }
        """)
        
        # Layout untuk konten
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(40, 40, 40, 40)
        content_layout.setSpacing(30)
        
        # Grid untuk film
        self.movies_grid = QGridLayout()
        self.movies_grid.setSpacing(30)
        content_layout.addLayout(self.movies_grid)
        content_layout.addStretch()
        
        # Set scroll area content
        scroll_area.setWidget(content_widget)
        
        # Add components to movies list layout
        movies_list_layout.addWidget(search_filter_container)
        movies_list_layout.addWidget(scroll_area)
        
        # Tambahkan halaman daftar film ke stack widget
        self.stack_widget.addWidget(self.movies_list_page)
        self.pages["movies_list"] = self.stack_widget.count() - 1
        
    def setup_genre_filters(self, movies):
        """Setup genre filter checkboxes"""
        # Clear existing checkboxes
        for i in reversed(range(self.genre_grid.count())): 
            self.genre_grid.itemAt(i).widget().setParent(None)
        
        # Get unique genres
        all_genres = set()
        for movie in movies:
            genres = movie.get('genre', '').split(', ')
            all_genres.update(genres)
        
        # Create checkboxes for each genre
        row, col = 0, 0
        for genre in sorted(all_genres):
            if not genre:  # Skip empty genre
                continue
                
            checkbox = QPushButton(genre)
            checkbox.setCheckable(True)
            checkbox.setStyleSheet("""
                QPushButton {
                    background-color: #2A2A2A;
                    color: #B3B3B3;
                    border: none;
                    border-radius: 15px;
                    padding: 8px 15px;
                    font-size: 13px;
                    font-family: 'Poppins';
                    text-align: center;
                }
                QPushButton:checked {
                    background-color: #FFD700;
                    color: #000000;
                    font-weight: 600;
                }
                QPushButton:hover:!checked {
                    background-color: #333333;
                    color: #FFFFFF;
                }
            """)
            checkbox.clicked.connect(self.filter_movies)
            
            self.genre_grid.addWidget(checkbox, row, col)
            col += 1
            if col >= 4:  # 4 columns per row
                col = 0
                row += 1
    
    def filter_movies(self):
        """Filter movies based on search text and selected genres"""
        search_text = self.search_input.text().lower()
        
        # Get selected genres
        selected_genres = []
        for i in range(self.genre_grid.count()):
            checkbox = self.genre_grid.itemAt(i).widget()
            if checkbox and checkbox.isChecked():
                selected_genres.append(checkbox.text())
        
        # Clear existing grid
        for i in reversed(range(self.movies_grid.count())): 
            self.movies_grid.itemAt(i).widget().setParent(None)
        
        # Filter and display movies
        row, col = 0, 0
        for movie in self.all_movies:
            title = movie.get('title', '').lower()
            movie_genres = movie.get('genre', '').split(', ')
            
            # Check if movie matches filters
            matches_search = search_text in title
            
            # Case-insensitive comparison for genres
            matches_genre = False
            if not selected_genres:
                matches_genre = True
            else:
                for selected_genre in selected_genres:
                    if any(selected_genre == genre for genre in movie_genres):
                        matches_genre = True
                        break
            
            if matches_search and matches_genre:
                movie_card = MovieCard(movie)
                movie_card.book_clicked.connect(self.on_book_clicked)
                movie_card.movie_clicked.connect(self.on_movie_clicked)
                
                self.movies_grid.addWidget(movie_card, row, col)
                
                col += 1
                if col >= 4:  # 4 columns per row
                    col = 0
                    row += 1

    def load_movies(self):
        """Memuat daftar film dari file data_film.txt"""
        movies = []
        try:
            with open('data_film.txt', 'r', encoding='utf-8') as file:
                # Read all lines
                lines = file.readlines()
                
                # Get header line (first line)
                header = lines[0].strip().split('|')
                
                # Process each movie data line (skip header)
                for line in lines[1:]:
                    line = line.strip()
                    if not line:  # Skip empty lines
                        continue
                    
                    # Split by pipe character
                    values = line.split('|')
                    if len(values) < len(header):
                        continue  # Skip incomplete data
                    
                    # Create movie dictionary
                    movie = {}
                    for i, field in enumerate(header):
                        key = field.lower().replace(' ', '_')
                        value = values[i].strip()
                        
                        # Convert values to appropriate types
                        if key == 'harga':
                            movie['price'] = int(value)
                        elif key == 'durasi':
                            movie['duration'] = int(value)
                        elif key == 'jadwal':
                            movie['schedule'] = [time.strip() for time in value.split(',')]
                        elif key == 'judul_film':
                            movie['title'] = value
                        elif key == 'genre':
                            movie['genre'] = value
                        elif key == 'sinopsis':
                            movie['synopsis'] = value
                        elif key == 'sutradara':
                            movie['director'] = value
                        elif key == 'pemeran':
                            movie['cast'] = value
                        elif key == 'usia_minimal':
                            movie['age_rating'] = value
                    
                    movies.append(movie)
        except FileNotFoundError:
            print("File data_film.txt tidak ditemukan")
            # Fallback to dummy data if file not found
            movies = self.load_movies_from_db()
        except Exception as e:
            print(f"Error saat membaca file: {e}")
            # Fallback to dummy data on error
            movies = self.load_movies_from_db()
        
        # Store all movies for filtering
        self.all_movies = []
        
        # Process movies and add posters
        for movie in movies:
            # Add poster path to movie data
            movie_with_poster = movie.copy()
            title = movie.get("title", "")
            poster_path = find_poster_for_film(title)
            print(f"Film: {title}, Poster path: {poster_path}")
            movie_with_poster["poster_path"] = poster_path
            self.all_movies.append(movie_with_poster)
        
        # Setup genre filters
        self.setup_genre_filters(self.all_movies)
        
        # Display all movies initially
        self.filter_movies()
        
        return movies

    def on_book_clicked(self, movie_data):
        """Handler ketika tombol booking diklik"""
        self.current_movie = movie_data
        
        # Tampilkan halaman detail film dulu
        self.movie_detail_page.display_movie_detail(movie_data)
        self.stack_widget.setCurrentIndex(self.pages["movie_detail"])

    def on_movie_clicked(self, movie_data):
        """Handler ketika kartu film diklik"""
        self.current_movie = movie_data
        
        # Tampilkan halaman detail film
        self.movie_detail_page.display_movie_detail(movie_data)
        self.stack_widget.setCurrentIndex(self.pages["movie_detail"])
        
    def show_movies_list(self):
        """Kembali ke halaman daftar film"""
        if "movies_list" in self.pages:
            self.stack_widget.setCurrentIndex(self.pages["movies_list"])
        
    def show_movie_detail(self):
        """Tampilkan halaman detail film"""
        self.stack_widget.setCurrentIndex(self.pages["movie_detail"])
        
    def show_booking_page(self, movie_data):
        """Tampilkan halaman booking"""
        # Konfirmasi booking
        confirm = QMessageBox()
        confirm.setWindowTitle("Konfirmasi Booking")
        confirm.setText(f"Apakah Anda yakin ingin memesan tiket untuk film {movie_data['title']}?")
        confirm.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        confirm.setDefaultButton(QMessageBox.No)
        confirm.setStyleSheet("""
            QMessageBox {
                background-color: #FFFFFF;
            }
            QMessageBox QLabel {
                color: #000000;
                font-size: 14px;
                font-family: 'Montserrat';
            }
            QPushButton {
                background-color: #FFD700;
                color: #000000;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                font-weight: bold;
                font-family: 'Montserrat';
                font-size: 13px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #F5CB0C;
            }
            QPushButton:pressed {
                background-color: #E6C000;
            }
        """)
        
        if confirm.exec_() == QMessageBox.Yes:
            self.booking_page.setup_for_movie(movie_data)
            self.stack_widget.setCurrentIndex(self.pages["booking"])
        
    def show_ticket_page(self, booking_data):
        """Tampilkan halaman tiket setelah booking berhasil"""
        print(f"Showing ticket page with booking data: {booking_data.get('movie_title')}, price: {booking_data.get('total_price')}")
        # Simpan saldo sebelum menampilkan ticket
        saldo_before = self.user_data.get('saldo', 0) if self.user_data else 0
        print(f"Saldo before ticket processing: {saldo_before}")
        
        # Jika tiket sudah dibayar di booking page, emit signal update saldo segera
        if booking_data.get("payment_status") == "PAID" and hasattr(self, 'switch_page_signal'):
            try:
                print(f"Emitting immediate saldo update for paid ticket: {self.user_data.get('saldo')}")
                self.switch_page_signal.emit("update_saldo", {"new_saldo": self.user_data.get('saldo')})
            except Exception as e:
                print(f"Error emitting immediate switch_page_signal: {e}")
        
        # Set user_data ke ticket_page
        if hasattr(self, 'ticket_page') and self.user_data:
            self.ticket_page.user_data = self.user_data
        
        self.ticket_page.display_ticket(booking_data)
        self.stack_widget.setCurrentIndex(self.pages["ticket"])
        
        # Periksa apakah saldo di ticket_page sudah berubah
        if hasattr(self.ticket_page, 'user_data') and self.ticket_page.user_data:
            ticket_saldo = self.ticket_page.user_data.get('saldo')
            print(f"Saldo in ticket_page after processing: {ticket_saldo}")
            
            if self.user_data and ticket_saldo is not None:
                if self.user_data.get('saldo') != ticket_saldo:
                    print(f"Updating saldo from {self.user_data.get('saldo')} to {ticket_saldo}")
                    self.user_data['saldo'] = ticket_saldo
                    # Update saldo di halaman lain
                    self.update_user_data(self.user_data)
                    
                    # Emit signal jika merupakan bagian dari window utama untuk merefresh saldo di semua komponen UI
                    if hasattr(self, 'switch_page_signal'):
                        try:
                            self.switch_page_signal.emit("update_saldo", {"new_saldo": ticket_saldo})
                            print(f"Emitted switch_page_signal with saldo: {ticket_saldo}")
                        except Exception as e:
                            print(f"Error emitting switch_page_signal: {e}")
                            
    def update_saldo_after_payment(self, data):
        """Update saldo setelah pembayaran berhasil"""
        if 'new_saldo' in data and self.user_data:
            print(f"Updating saldo after payment: {self.user_data.get('saldo')} -> {data['new_saldo']}")
            
            # Perbarui saldo di user_data
            self.user_data['saldo'] = data['new_saldo']
            
            # Emit signal untuk memperbarui saldo di seluruh aplikasi
            if hasattr(self, 'switch_page_signal'):
                try:
                    self.switch_page_signal.emit("update_saldo", {"new_saldo": data['new_saldo']})
                    print(f"Emitted switch_page_signal with saldo: {data['new_saldo']}")
                except Exception as e:
                    print(f"Error emitting switch_page_signal after payment: {e}")
            
            # Perbarui saldo di komponen lain yang diperlukan
            if hasattr(self, 'movie_detail_page'):
                self.movie_detail_page.user_data = self.user_data
            if hasattr(self, 'booking_page'):
                self.booking_page.user_data = self.user_data
            if hasattr(self, 'ticket_page'):
                self.ticket_page.user_data = self.user_data

    def update_user_data(self, user_data):
        """Update data pengguna"""
        self.user_data = user_data
        if hasattr(self, 'movie_detail_page'):
            self.movie_detail_page.user_data = user_data
        if hasattr(self, 'booking_page'):
            self.booking_page.user_data = user_data
        
    def load_movies_from_db(self):
        """Fungsi untuk memuat data film dari database atau dummy data"""
        # Try to get data from MovieModel first
        try:
            from models import MovieModel
            movies = MovieModel.get_all_movies()
            if movies:
                return movies
        except Exception as e:
            print(f"Error loading from MovieModel: {e}")
        
        # Fallback dummy data if all else fails
        return [
            {
                "id": 1,
                "title": "Avengers: Endgame",
                "genre": "Action, Adventure",
                "duration": 181,
                "price": 75000,
                "age_rating": 13,
                "synopsis": "Setelah peristiwa yang menghancurkan setengah dari semua kehidupan di alam semesta, Avengers yang tersisa harus bersatu kembali untuk membatalkan tindakan Thanos dan memulihkan keseimbangan.",
                "director": "Russo Brothers",
                "cast": "Robert Downey Jr., Chris Evans, Mark Ruffalo",
                "schedule": ["14:00", "17:00", "20:00"]
            },
            {
                "id": 2,
                "title": "Spider-Man: No Way Home",
                "genre": "Action, Adventure",
                "duration": 148,
                "price": 65000,
                "age_rating": 13,
                "synopsis": "Peter Parker meminta bantuan Doctor Strange untuk membuat identitasnya sebagai Spider-Man terlupakan, namun mantra tersebut membuka multiverse dan membebaskan penjahat dari universe lain.",
                "director": "Jon Watts",
                "cast": "Tom Holland, Zendaya, Benedict Cumberbatch",
                "schedule": ["13:00", "16:00", "19:00"]
            }
        ]

    def handle_booking_success(self, booking_data):
        """Handle successful booking and emit signals for it"""
        try:
            # Extract data
            print("Handling booking success with data:", booking_data)
            
            # Ubah format data untuk ticket page dan history
            processed_booking_data = {
                "movie_title": booking_data.get("movie_title", "Unknown Movie"),
                "selected_seats": booking_data.get("selected_seats", []),
                "seats": booking_data.get("selected_seats", []),  # Alias untuk selected_seats
                "seat_count": len(booking_data.get("selected_seats", [])),
                "total_price": booking_data.get("total_price", 0),
                "price_per_ticket": booking_data.get("total_price", 0) // max(1, len(booking_data.get("selected_seats", []))),
                "studio_type": booking_data.get("studio", "Regular"),  # Use studio as studio_type
                "studio": booking_data.get("studio", "Regular"),
                "schedule": booking_data.get("show_date", ""),
                "cinema": booking_data.get("cinema", "Unknown Cinema"),
                "theater": booking_data.get("theater", ""),
                "city": booking_data.get("city", "Unknown City"),
                "payment_status": "PAID",
                "booking_date": QDateTime.currentDateTime().toString("dd/MM/yyyy HH:mm"),
                "transaction_type": "Pembelian Tiket",
                "timestamp": QDateTime.currentDateTime().toString("dd/MM/yyyy HH:mm")
            }
            
            print("Processed booking data for history:", processed_booking_data)
            
            # Update saldo user
            new_saldo = self.user_data["saldo"] - booking_data.get("total_price", 0)
            self.user_data["saldo"] = new_saldo
            print(f"Updated user saldo: {new_saldo}")
            
            # Emit signal untuk update saldo di dashboard
            self.switch_page_signal.emit("update_saldo", {"new_saldo": new_saldo})
            print("Emitted switch_page_signal for saldo update")
            
            # Emit signal untuk history transaksi
            print("Emitting ticket_purchased signal...")
            
            # Format data untuk sesuai dengan format yang diharapkan di handle_ticket_purchase
            ticket_history_data = {
                "type": "Tiket",
                "movie_title": processed_booking_data["movie_title"],
                "movie_id": processed_booking_data.get("movie_id", 0),
                "total_price": processed_booking_data["total_price"],
                "studio_type": processed_booking_data["studio_type"],
                "studio": processed_booking_data["studio"],
                "theater": processed_booking_data["theater"],
                "cinema": processed_booking_data["cinema"],
                "seats": processed_booking_data["selected_seats"],
                "schedule": processed_booking_data["schedule"] if "schedule" in processed_booking_data else processed_booking_data.get("show_date", ""),
                "show_date": processed_booking_data["show_date"] if "show_date" in processed_booking_data else processed_booking_data.get("schedule", ""),
                "show_time": processed_booking_data.get("show_time", ""),
                "timestamp": processed_booking_data["timestamp"],
                "status": "Sukses",
                "total": -processed_booking_data["total_price"]  # Make sure this matches the format expected in history
            }
            
            # Try to add directly to history page if parent has access
            try:
                if hasattr(self.parent(), 'history_page'):
                    print("Adding ticket directly to history")
                    self.parent().history_page.add_transaction(ticket_history_data)
                    self.parent().history_page.filter_transactions()
                    print("Direct history addition completed")
            except Exception as e:
                print(f"Error adding to history directly: {e}")
            
            # Also emit the signal for DashboardWindow to handle
            self.ticket_purchased.emit(ticket_history_data)
            print("Ticket purchased signal emitted with data:", ticket_history_data)
            
            # Show ticket page
            self.show_ticket_page(processed_booking_data)
            print("Showing ticket page")
            
        except Exception as e:
            print(f"Error in handle_booking_success: {str(e)}")
            import traceback
            traceback.print_exc()
            QMessageBox.warning(
                self,
                "Error",
                f"Terjadi kesalahan saat memproses pemesanan: {str(e)}"
            )

# Untuk testing
if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    window = MoviesPage()
    window.setGeometry(100, 100, 900, 600)
    window.show()
    sys.exit(app.exec_()) 