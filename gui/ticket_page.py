from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                          QPushButton, QFrame, QScrollArea, QSizePolicy, QGridLayout, QMessageBox, QFileDialog)
from PyQt5.QtGui import QFont, QPixmap, QIcon, QPainter, QColor, QPen, QBrush
from PyQt5.QtCore import Qt, pyqtSignal, QSize, QRect, QRectF, QDate, QDateTime, QTimer
import os
import qrcode
from PIL import Image, ImageDraw, ImageFont
from PIL.ImageQt import ImageQt
from io import BytesIO
import uuid
import json
from shutil import copyfile
import traceback
import time

from models import UserModel
from utils.helper import find_poster_for_film

class TicketPage(QWidget):
    """Halaman untuk menampilkan e-ticket"""
    
    back_to_movies = pyqtSignal()
    show_history = pyqtSignal()  # Signal baru untuk menampilkan history
    
    def __init__(self, user_data=None):
        super().__init__()
        self.user_data = user_data
        self.booking_data = None
        self.ticket_image_path = None
        self.init_ui()
        
    def init_ui(self):
        # Layout utama
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(30)
        
        # Header dengan tombol kembali
        header_layout = QHBoxLayout()
        
        # Tombol kembali
        back_button = QPushButton("← Kembali ke Daftar Film")
        back_button.setStyleSheet("""
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
        back_button.setCursor(Qt.PointingHandCursor)
        back_button.clicked.connect(self.back_to_movies.emit)
        
        # Judul halaman
        title_label = QLabel("E-Ticket")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                color: #FFFFFF;
                font-size: 24px;
                font-weight: bold;
                font-family: 'Montserrat';
            }
        """)
        
        header_layout.addWidget(back_button)
        header_layout.addStretch()
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        main_layout.addLayout(header_layout)
        
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
        """)
        
        content_layout = QVBoxLayout(content_container)
        content_layout.setContentsMargins(30, 30, 30, 30)
        content_layout.setSpacing(20)
        
        # E-ticket preview
        self.ticket_preview = QLabel()
        self.ticket_preview.setAlignment(Qt.AlignCenter)
        self.ticket_preview.setMinimumSize(400, 600)
        self.ticket_preview.setStyleSheet("""
            QLabel {
                background-color: #1E1E1E;
                border-radius: 10px;
            }
        """)
        content_layout.addWidget(self.ticket_preview)
        
        # Download button
        download_button = QPushButton("Download E-Ticket")
        download_button.setCursor(Qt.PointingHandCursor)
        download_button.setStyleSheet("""
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
        """)
        download_button.clicked.connect(self.download_ticket)
        content_layout.addWidget(download_button)
        
        main_layout.addWidget(content_container)
        
        # Set window background
        self.setStyleSheet("background-color: #1E1E1E;")
        
    def generate_qr_code(self, data, size=200):
        """Generate QR code from data"""
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(json.dumps(data))
        qr.make(fit=True)
        
        qr_image = qr.make_image(fill_color="black", back_color="white")
        return qr_image.resize((size, size))
        
    def generate_e_ticket(self, booking_data):
        """Generate e-ticket image"""
        try:
            # Ensure booking_data has all required keys
            required_keys = ['movie_title', 'schedule', 'studio_type', 'cinema', 'theater', 'city', 'total_price']
            
            # Check for the selected_seats or seats key
            if 'seats' not in booking_data and 'selected_seats' in booking_data:
                booking_data['seats'] = booking_data['selected_seats']  # Use selected_seats as seats if available
            
            # Validate all required keys exist
            missing_keys = [key for key in required_keys if key not in booking_data]
            if missing_keys:
                print(f"Warning: Missing required keys in booking_data: {missing_keys}")
                # Add default values for missing keys
                for key in missing_keys:
                    booking_data[key] = "N/A"
            
            # Calculate seat count and price per ticket if not provided
            if 'seat_count' not in booking_data and 'seats' in booking_data:
                booking_data['seat_count'] = len(booking_data['seats'])
            else:
                booking_data['seat_count'] = 0
                
            # Get total price from booking_data, ensuring it's not 0
            total_price = booking_data.get('total_price', 0)
            if total_price == 0:
                total_price = abs(booking_data.get('total', 0))  # Try getting from 'total' if total_price is 0
                
            if 'price_per_ticket' not in booking_data and total_price > 0 and booking_data['seat_count'] > 0:
                booking_data['price_per_ticket'] = total_price // booking_data['seat_count']
            else:
                booking_data['price_per_ticket'] = 0
                
            # Add booking date if not provided
            if 'booking_date' not in booking_data:
                booking_data['booking_date'] = QDateTime.currentDateTime().toString("dd/MM/yyyy HH:mm")

            # Safe access with default values
            seats = booking_data.get('seats', [])
            if isinstance(seats, list):
                seats_str = ", ".join(seats)
            else:
                seats_str = str(seats)

            # Create or load template
            width, height = 800, 1200
            template_path = "assets/templates/ticket_template.png"
            
            if os.path.exists(template_path):
                # If template exists, load it
                img = Image.open(template_path)
                width, height = img.size
            else:
                # Create a directory for templates if it doesn't exist
                os.makedirs("assets/templates", exist_ok=True)
                
                # If template doesn't exist, create a new image
                img = Image.new('RGB', (width, height), '#1E1E1E')
                
                # Add a gold header bar
                draw = ImageDraw.Draw(img)
                draw.rectangle([0, 0, width, 100], fill='#FFD700')
                
                # Save the template for future use
                img.save(template_path)
            
            # Create draw object
            draw = ImageDraw.Draw(img)
            
            # Load fonts
            try:
                title_font = ImageFont.truetype("assets/fonts/Montserrat-Bold.ttf", 36)
                heading_font = ImageFont.truetype("assets/fonts/Montserrat-Bold.ttf", 24)
                regular_font = ImageFont.truetype("assets/fonts/Montserrat-Regular.ttf", 14)
                small_font = ImageFont.truetype("assets/fonts/Montserrat-Regular.ttf", 12)
            except IOError:
                # Fallback to default font if custom font not found
                title_font = ImageFont.load_default()
                heading_font = ImageFont.load_default()
                regular_font = ImageFont.load_default()
                small_font = ImageFont.load_default()
            
            # Draw title
            draw.text((width//2, 50), 'E-TICKET', font=title_font, fill='#000000', anchor="mm")
            
            # Draw movie title
            draw.text((40, 140), booking_data.get("movie_title", "Unknown Movie"), font=heading_font, fill='#FFFFFF')
            
            # Draw booking details
            y = 220
            details = [
                ("Bioskop:", f"{booking_data.get('cinema', 'N/A')}"),
                ("Kota:", booking_data.get("city", "N/A")),
                ("Theater:", booking_data.get("theater", "N/A")),
                ("Studio:", booking_data.get("studio_type", "Regular")),
                ("Jadwal:", booking_data.get("schedule", "N/A")),
                ("Kursi:", seats_str),
                ("Jumlah Tiket:", str(booking_data.get("seat_count", 0))),
                ("Harga per Tiket:", f"Rp {booking_data.get('price_per_ticket', 0):,}".replace(',', '.')),
                ("Total Harga:", f"Rp {booking_data.get('total_price', 0):,}".replace(',', '.')),
                ("Tanggal Booking:", booking_data.get("booking_date", "N/A"))
            ]
            
            for label, value in details:
                # Draw label and value
                draw.text((40, y), label, font=regular_font, fill='#CCCCCC')
                draw.text((200, y), value, font=regular_font, fill='#FFFFFF')
                y += 30
            
            # Generate QR code
            qr_data = {
                "movie": booking_data.get("movie_title", ""),
                "cinema": booking_data.get("cinema", ""),
                "theater": booking_data.get("theater", ""),
                "date": booking_data.get("schedule", ""),
                "seats": seats_str,
                "id": uuid.uuid4().hex[:8].upper()
            }
            
            # Convert to JSON and generate QR
            qr_json = json.dumps(qr_data)
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(qr_json)
            qr.make(fit=True)
            
            qr_img = qr.make_image(fill_color="black", back_color="white")
            
            # Resize QR code
            qr_size = 200
            qr_img = qr_img.resize((qr_size, qr_size))
            
            # Calculate QR code position (right side of ticket)
            qr_x = width - qr_size - 40
            qr_y = 240
            
            # Paste QR code onto ticket
            img.paste(qr_img, (qr_x, qr_y))
            
            # Draw note below QR code
            note_text = "Scan QR code ini di bioskop untuk masuk"
            draw.text((qr_x + qr_size // 2, qr_y + qr_size + 20), note_text, 
                    font=small_font, fill='#FFFFFF', anchor="mm")
            
            # Add ticket ID
            ticket_id = f"Ticket ID: {qr_data['id']}"
            draw.text((qr_x + qr_size // 2, qr_y + qr_size + 40), ticket_id, 
                    font=small_font, fill='#FFD700', anchor="mm")
            
            # Save the ticket
            os.makedirs("temp", exist_ok=True)
            file_path = f"temp/ticket_{qr_data['id']}.png"
            img.save(file_path)
            
            return file_path
            
        except Exception as e:
            print(f"Error generating e-ticket: {str(e)}")
            traceback.print_exc()
            # Create a simple error ticket
            try:
                error_img = Image.new('RGB', (800, 600), color=(30, 30, 30))
                draw = ImageDraw.Draw(error_img)
                
                # Try to use a default font
                try:
                    font = ImageFont.truetype("assets/fonts/Montserrat-Bold.ttf", 24)
                    small_font = ImageFont.truetype("assets/fonts/Montserrat-Regular.ttf", 16)
                except:
                    font = ImageFont.load_default()
                    small_font = ImageFont.load_default()
                
                draw.text((400, 100), "Terjadi Kesalahan", font=font, fill=(255, 255, 255), anchor="mm")
                draw.text((400, 150), "Tidak dapat membuat e-ticket", font=small_font, fill=(255, 255, 255), anchor="mm")
                draw.text((400, 200), f"Error: {str(e)}", font=small_font, fill=(255, 215, 0), anchor="mm")
                draw.text((400, 250), "Silakan hubungi customer service", font=small_font, fill=(255, 255, 255), anchor="mm")
                
                # Add movie details if available
                y = 300
                if 'movie_title' in booking_data:
                    draw.text((400, y), f"Film: {booking_data.get('movie_title', 'N/A')}", font=small_font, fill=(255, 255, 255), anchor="mm")
                    y += 30
                
                if 'cinema' in booking_data and 'theater' in booking_data:
                    draw.text((400, y), f"Lokasi: {booking_data.get('cinema', 'N/A')} - {booking_data.get('theater', 'N/A')}", font=small_font, fill=(255, 255, 255), anchor="mm")
                    y += 30
                
                # Save the error ticket
                os.makedirs("temp", exist_ok=True)
                error_file_path = f"temp/error_ticket_{int(time.time())}.png"
                error_img.save(error_file_path)
                return error_file_path
                
            except Exception as inner_e:
                print(f"Failed to create error ticket: {str(inner_e)}")
                return None
        
    def display_ticket(self, booking_data):
        """Display the e-ticket"""
        self.booking_data = booking_data
        
        # Proses pembayaran jika belum dibayar
        payment_status = booking_data.get("payment_status", "UNPAID")  # Default to UNPAID if status not specified
        print(f"Ticket payment status: {payment_status}")
        
        # Hanya proses pembayaran jika status UNPAID (pembayaran sekarang dilakukan di booking_page)
        if payment_status == "UNPAID" and self.user_data and 'username' in self.user_data:
            total_price = booking_data.get("total_price", 0)
            print(f"Processing payment for ticket: Rp {total_price:,}")
            
            # Lakukan pembayaran dengan mengurangi saldo
            try:
                success, message, new_saldo = UserModel.update_saldo(
                    self.user_data['username'],
                    -total_price  # Kurangi saldo
                )
                print(f"Payment result: success={success}, message={message}, new_saldo={new_saldo}")
                
                if success:
                    # Update status pembayaran
                    self.booking_data["payment_status"] = "PAID"
                    
                    # Update user data dengan saldo baru
                    if self.user_data:
                        print(f"Updating user saldo from {self.user_data.get('saldo', 0)} to {new_saldo}")
                        self.user_data['saldo'] = new_saldo
                        
                    # Tampilkan notifikasi pembayaran berhasil
                    QMessageBox.information(
                        self,
                        "Pembayaran Berhasil",
                        f"Pembayaran tiket sebesar Rp {total_price:,} berhasil.\nSaldo Anda sekarang: Rp {new_saldo:,}".replace(',', '.')
                    )
                else:
                    # Jika gagal, tampilkan pesan error
                    QMessageBox.critical(
                        self,
                        "Pembayaran Gagal",
                        f"Gagal melakukan pembayaran: {message}\nSilakan coba lagi atau hubungi customer service."
                    )
                    # Kembali ke halaman sebelumnya
                    self.back_to_movies.emit()
                    return
            except Exception as e:
                print(f"Error during payment processing: {str(e)}")
                QMessageBox.critical(
                    self,
                    "Error Pembayaran",
                    f"Terjadi kesalahan saat memproses pembayaran: {str(e)}"
                )
                self.back_to_movies.emit()
                return
        # Jika sudah dibayar, pastikan data saldo di user_data terupdate
        elif payment_status == "PAID" and self.user_data and booking_data.get("total_price"):
            print(f"Ticket already paid. Ensuring user data has current saldo.")
            # Pastikan saldo di user_data terupdate dengan yang terbaru dari database
            if 'username' in self.user_data:
                current_saldo = UserModel.get_saldo(self.user_data['username'])
                if current_saldo != self.user_data.get('saldo'):
                    print(f"Updating user_data saldo from {self.user_data.get('saldo')} to {current_saldo}")
                    self.user_data['saldo'] = current_saldo
        
        # Generate e-ticket image
        self.ticket_image_path = self.generate_e_ticket(booking_data)
        
        # Display the ticket
        if os.path.exists(self.ticket_image_path):
            pixmap = QPixmap(self.ticket_image_path)
            scaled_pixmap = pixmap.scaled(
                self.ticket_preview.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.ticket_preview.setPixmap(scaled_pixmap)
            
            # Tampilkan history setelah 2 detik (memberikan waktu untuk melihat e-ticket)
            QTimer.singleShot(2000, self.show_history.emit)
            
    def download_ticket(self):
        """Download the e-ticket"""
        if not self.ticket_image_path or not os.path.exists(self.ticket_image_path):
            return
            
        # Open file dialog
        file_name, _ = QFileDialog.getSaveFileName(
            self,
            "Save E-Ticket",
            f"ticket_{self.booking_data['movie_title'].replace(' ', '_')}.png",
            "Images (*.png)"
        )
        
        if file_name:
            # Copy the temporary file to the selected location
            copyfile(self.ticket_image_path, file_name)
    
    def __del__(self):
        """Cleanup temporary files when object is destroyed"""
        if self.ticket_image_path and os.path.exists(self.ticket_image_path):
            try:
                os.remove(self.ticket_image_path)
            except:
                pass 