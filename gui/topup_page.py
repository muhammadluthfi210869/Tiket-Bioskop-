from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                          QLineEdit, QComboBox, QPushButton, QFrame, QMessageBox,
                          QRadioButton, QButtonGroup, QSpacerItem, QSizePolicy, QGridLayout, QScrollArea)
from PyQt5.QtGui import QFont, QPixmap, QIcon, QIntValidator
from PyQt5.QtCore import Qt, pyqtSignal, QSize, QDateTime
import os
from models import UserModel
from datetime import datetime

class BankButton(QPushButton):
    """Button khusus untuk menampilkan ikon bank"""
    
    def __init__(self, bank_name, bank_logo_path, parent=None):
        super().__init__(parent)
        self.bank_name = bank_name
        self.bank_logo_path = bank_logo_path
        self.setCheckable(True)
        self.setCursor(Qt.PointingHandCursor)
        self.init_ui()
        
    def init_ui(self):
        """Setup tampilan button"""
        # Set ukuran tetap
        self.setFixedSize(90, 70)
        
        # Load logo
        if os.path.exists(self.bank_logo_path):
            pixmap = QPixmap(self.bank_logo_path)
            pixmap = pixmap.scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.setIcon(QIcon(pixmap))
            self.setIconSize(QSize(40, 40))
        
        # Setup style
        self.setStyleSheet("""
            QPushButton {
                background-color: #1E1E1E;
                border: 1px solid #2A2A2A;
                border-radius: 8px;
                padding: 10px;
                text-align: center;
            }
            QPushButton:hover {
                background-color: #2A2A2A;
            }
            QPushButton:checked {
                background-color: #FFD700;
                border: none;
            }
        """)

class TopUpPage(QWidget):
    """Halaman untuk melakukan top-up saldo"""
    # Signal ketika top-up berhasil
    top_up_success = pyqtSignal(int)
    
    def __init__(self, user_data):
        super().__init__()
        self.user_data = user_data
        self.selected_bank = None
        self.init_ui()
        
    def update_display_saldo(self, new_saldo):
        """Memperbarui tampilan saldo pada halaman top up"""
        # This method is kept for compatibility
        # The actual updating is done by the dashboard
        print(f"TopUpPage: Received saldo update request to {new_saldo}")
        pass
        
    def init_ui(self):
        """Inisialisasi antarmuka pengguna"""
        # Buat scroll area
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: #1E1E1E;
                border: none;
            }
        """)
        
        # Widget untuk konten
        content_widget = QWidget()
        
        # Layout utama
        main_layout = QVBoxLayout(content_widget)
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(25)
        
        # Set background untuk seluruh halaman
        self.setStyleSheet("""
            QWidget {
                background-color: #1E1E1E;
            }
        """)
        
        # Judul halaman
        title_label = QLabel("Top-Up Saldo")
        title_label.setObjectName("page_title")
        title_font = QFont("Montserrat", 24, QFont.Bold)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #121212; margin-bottom: 10px;")
        main_layout.addWidget(title_label)
        
        # Informasi saldo saat ini
        current_balance_frame = QFrame()
        current_balance_frame.setFrameShape(QFrame.StyledPanel)
        current_balance_frame.setStyleSheet("""
            QFrame {
                background-color: #121212;
                border-radius: 10px;
                padding: 25px;
            }
        """)
        
        balance_layout = QVBoxLayout(current_balance_frame)
        balance_layout.setSpacing(15)
        
        current_balance_label = QLabel("Saldo Saat Ini:")
        current_balance_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #FFFFFF; font-family: 'Montserrat';")
        
        # Ambil saldo saat ini dari database
        current_saldo = UserModel.get_saldo(self.user_data['username'])
        self.saldo_value_label = QLabel(f"Rp {current_saldo:,}".replace(',', '.'))
        self.saldo_value_label.setStyleSheet("font-size: 32px; color: #FFD700; font-weight: bold; font-family: 'Montserrat';")
        self.saldo_value_label.setAlignment(Qt.AlignCenter)
        
        balance_layout.addWidget(current_balance_label)
        balance_layout.addWidget(self.saldo_value_label)
        
        main_layout.addWidget(current_balance_frame)
        
        # Nominal Top-Up
        nominal_frame = QFrame()
        nominal_frame.setFrameShape(QFrame.StyledPanel)
        nominal_frame.setStyleSheet("""
            QFrame {
                background-color: #2A2A2A;
                border-radius: 10px;
                border: none;
                padding: 25px;
            }
        """)
        
        nominal_layout = QVBoxLayout(nominal_frame)
        nominal_layout.setSpacing(20)
        
        nominal_label = QLabel("Pilih Nominal Top-Up:")
        nominal_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #121212; font-family: 'Montserrat';")
        nominal_layout.addWidget(nominal_label)
        
        # Grid untuk tombol nominal
        nominal_grid = QGridLayout()
        nominal_grid.setSpacing(15)
        
        # Nominal preset
        nominal_values = [
            ("Rp 10.000", 10000),
            ("Rp 20.000", 20000),
            ("Rp 50.000", 50000),
            ("Rp 100.000", 100000),
            ("Rp 200.000", 200000),
            ("Rp 500.000", 500000)
        ]
        
        # Buat tombol untuk setiap nominal
        self.nominal_buttons = []
        row, col = 0, 0
        for label, value in nominal_values:
            button = QPushButton(label)
            button.setProperty("value", value)
            button.setStyleSheet("""
                QPushButton {
                    background-color: #333333;
                    border: none;
                    border-radius: 6px;
                    padding: 12px;
                    font-size: 14px;
                    font-family: 'Montserrat';
                    color: white;
                }
                QPushButton:hover {
                    background-color: #3A3A3A;
                }
                QPushButton:checked {
                    background-color: #FFD700;
                    color: #121212;
                    font-weight: bold;
                }
            """)
            button.setCheckable(True)
            button.clicked.connect(self.nominal_button_clicked)
            
            nominal_grid.addWidget(button, row, col)
            self.nominal_buttons.append(button)
            
            col += 1
            if col > 2:  # 3 kolom per baris
                col = 0
                row += 1
        
        # Tombol nominal lainnya
        other_nominal_layout = QHBoxLayout()
        other_nominal_layout.setSpacing(15)
        
        other_nominal_label = QLabel("Nominal Lainnya:")
        other_nominal_label.setStyleSheet("font-family: 'Montserrat'; color: #121212;")
        
        self.other_nominal_input = QLineEdit()
        self.other_nominal_input.setPlaceholderText("Masukkan jumlah")
        self.other_nominal_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 1px solid #3A3A3A;
                border-radius: 6px;
                font-family: 'Montserrat';
                background-color: #333333;
                color: white;
            }
            QLineEdit:focus {
                border: 1px solid #FFD700;
            }
        """)
        
        # Hanya menerima input angka
        self.other_nominal_input.setValidator(QIntValidator(10000, 10000000))
        self.other_nominal_input.textChanged.connect(self.other_nominal_changed)
        
        other_nominal_layout.addWidget(other_nominal_label)
        other_nominal_layout.addWidget(self.other_nominal_input)
        
        nominal_layout.addLayout(nominal_grid)
        nominal_layout.addLayout(other_nominal_layout)
        
        main_layout.addWidget(nominal_frame)
        
        # Metode Pembayaran
        payment_frame = QFrame()
        payment_frame.setFrameShape(QFrame.StyledPanel)
        payment_frame.setStyleSheet("""
            QFrame {
                background-color: #2A2A2A;
                border-radius: 10px;
                border: none;
                padding: 25px;
            }
        """)
        
        payment_layout = QVBoxLayout(payment_frame)
        payment_layout.setSpacing(15)
        
        payment_label = QLabel("Pilih Metode Pembayaran:")
        payment_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #121212; font-family: 'Montserrat';")
        payment_layout.addWidget(payment_label)
        
        # Bank-bank yang tersedia
        bank_data = [
            {"name": "BCA", "logo": "BCA-512.webp"},
            {"name": "Mandiri", "logo": "mandiri.jpg"},
            {"name": "BNI", "logo": "BNI.webp"},
            {"name": "BRI", "logo": "BRI.png"},
            {"name": "OVO", "logo": "ovo.jpg"},
            {"name": "GoPay", "logo": "gopay.jpeg"}
        ]
        
        # Grid untuk bank buttons
        bank_grid = QGridLayout()
        bank_grid.setHorizontalSpacing(15)
        bank_grid.setVerticalSpacing(15)
        
        self.bank_buttons = []
        self.bank_button_group = QButtonGroup(self)
        self.bank_button_group.setExclusive(True)
        
        # Tambahkan bank buttons
        row, col = 0, 0
        for i, bank in enumerate(bank_data):
            icon_path = os.path.join("assets", "icons", "banks", bank["logo"])
            bank_button = BankButton(bank["name"], icon_path)
            bank_button.setProperty("bank_name", bank["name"])
            
            self.bank_button_group.addButton(bank_button, i)
            bank_grid.addWidget(bank_button, row, col)
            self.bank_buttons.append(bank_button)
            
            col += 1
            if col > 2:  # 3 kolom per baris
                col = 0
                row += 1
        
        # Connect button group
        self.bank_button_group.buttonClicked.connect(self.bank_button_clicked)
        
        # Set default bank
        if self.bank_buttons:
            self.bank_buttons[0].setChecked(True)
            self.selected_bank = self.bank_buttons[0].bank_name
        
        payment_layout.addLayout(bank_grid)
        main_layout.addWidget(payment_frame)
        
        # Tombol konfirmasi
        self.confirm_button = QPushButton("Konfirmasi Top-Up")
        self.confirm_button.setStyleSheet("""
            QPushButton {
                background-color: #FFD700;
                color: #121212;
                border: none;
                border-radius: 6px;
                padding: 15px;
                font-size: 16px;
                font-weight: bold;
                font-family: 'Montserrat';
                margin-top: 10px;
            }
            QPushButton:hover {
                background-color: #F5CB0C;
            }
            QPushButton:disabled {
                background-color: #E0E0E0;
                color: #999999;
            }
        """)
        self.confirm_button.setEnabled(False)  # Dinonaktifkan sampai nominal dipilih
        self.confirm_button.clicked.connect(self.confirm_top_up)
        
        main_layout.addWidget(self.confirm_button)
        
        # Tombol submit
        self.submit_btn = QPushButton("Top Up Sekarang")
        self.submit_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        self.submit_btn.clicked.connect(self.on_topup_clicked)
        
        # Spacer di bagian bawah
        main_layout.addStretch()
        
        # Set scroll area content
        scroll_area.setWidget(content_widget)
        
        # Layout untuk halaman
        page_layout = QVBoxLayout(self)
        page_layout.setContentsMargins(0, 0, 0, 0)
        page_layout.addWidget(scroll_area)
    
    def bank_button_clicked(self, button):
        """Handler ketika tombol bank diklik"""
        self.selected_bank = button.property("bank_name")
    
    def nominal_button_clicked(self):
        """Handler ketika tombol nominal diklik"""
        # Uncheck semua tombol lain
        sender = self.sender()
        for button in self.nominal_buttons:
            if button != sender:
                button.setChecked(False)
        
        # Clear input nominal lainnya
        self.other_nominal_input.clear()
        
        # Aktifkan tombol konfirmasi
        self.confirm_button.setEnabled(True)
    
    def other_nominal_changed(self, text):
        """Handler ketika input nominal lainnya diubah"""
        # Uncheck semua tombol nominal
        for button in self.nominal_buttons:
            button.setChecked(False)
        
        # Aktifkan/nonaktifkan tombol konfirmasi berdasarkan input
        try:
            value = int(text) if text else 0
            self.confirm_button.setEnabled(value >= 10000)
        except ValueError:
            self.confirm_button.setEnabled(False)
    
    def get_selected_nominal(self):
        """Mendapatkan nominal yang dipilih"""
        # Cek apakah ada tombol nominal yang dipilih
        for button in self.nominal_buttons:
            if button.isChecked():
                return button.property("value")
        
        # Cek input nominal lainnya
        try:
            return int(self.other_nominal_input.text())
        except (ValueError, TypeError):
            return 0
    
    def get_selected_payment_method(self):
        """Mendapatkan metode pembayaran yang dipilih"""
        return self.selected_bank
    
    def confirm_top_up(self):
        """Konfirmasi top-up saldo"""
        nominal = self.get_selected_nominal()
        payment_method = self.get_selected_payment_method()
        
        if nominal <= 0:
            QMessageBox.warning(self, "Peringatan", "Silakan pilih nominal top-up")
            return
        
        if not payment_method:
            QMessageBox.warning(self, "Peringatan", "Silakan pilih metode pembayaran")
            return
        
        # Konfirmasi top-up
        msg = QMessageBox.question(
            self,
            "Konfirmasi Top-Up",
            f"Anda akan melakukan top-up sebesar Rp {nominal:,} melalui {payment_method}. Lanjutkan?".replace(',', '.'),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if msg == QMessageBox.Yes:
            # Proses top-up
            success, message, new_saldo = UserModel.update_saldo(self.user_data['username'], nominal)
            
            if success:
                QMessageBox.information(
                    self,
                    "Top-Up Berhasil",
                    f"Saldo berhasil ditambahkan.\nSaldo saat ini: Rp {new_saldo:,}".replace(',', '.')
                )
                
                # Reset UI
                for button in self.nominal_buttons:
                    button.setChecked(False)
                self.other_nominal_input.clear()
                self.confirm_button.setEnabled(False)
                
                # Emit signal top-up berhasil - let dashboard handle everything
                self.top_up_success.emit(nominal)
            else:
                QMessageBox.warning(self, "Top-Up Gagal", message)
    
    def process_topup(self, amount):
        """Process the top-up transaction"""
        try:
            if self.user_data and 'username' in self.user_data:
                # Update the user's balance in the database
                success, message, new_saldo = UserModel.update_saldo(self.user_data['username'], amount)
                if success:
                    # Show success message
                    QMessageBox.information(
                        self,
                        "Top Up Berhasil",
                        f"Saldo berhasil ditambahkan.\nSaldo akan diperbarui pada tampilan."
                    )
                    
                    # Reset UI elements
                    for button in self.nominal_buttons:
                        button.setChecked(False)
                    self.other_nominal_input.clear()
                    self.confirm_button.setEnabled(False)
                    
                    # Enable back button if it exists
                    if hasattr(self, 'back_button'):
                        self.back_button.setEnabled(True)
                    
                    # Emit the signal with the amount - the dashboard will handle everything else
                    print(f"Emitting top_up_success with amount: {amount}")
                    self.top_up_success.emit(amount)
                    
                else:
                    # Handle error case
                    QMessageBox.warning(self, "Top Up Gagal", message)
            else:
                # Handle error case
                QMessageBox.warning(self, "Top Up Gagal", "Data pengguna tidak ditemukan")
        except Exception as e:
            print(f"Error processing top-up: {str(e)}")
            QMessageBox.critical(self, "Top Up Gagal", f"Gagal: {str(e)}")

    def on_topup_clicked(self):
        """Handler for top up button click"""
        try:
            # Get the amount from the appropriate input source
            amount = self.get_selected_nominal()
            
            # Validate amount
            if amount <= 0:
                QMessageBox.warning(self, "Input Tidak Valid", "Jumlah top up harus lebih dari 0!")
                return
            
            # Get payment method if needed
            payment_method = self.get_selected_payment_method()
            if not payment_method:
                QMessageBox.warning(self, "Metode Pembayaran", "Silakan pilih metode pembayaran")
                return
                
            # Confirm top-up with user
            confirm = QMessageBox.question(
                self,
                "Konfirmasi Top Up",
                f"Anda akan melakukan top up sebesar Rp {amount:,}. Lanjutkan?".replace(',', '.'),
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if confirm == QMessageBox.Yes:
                # Process the top-up - let dashboard handle the rest
                self.process_topup(amount)
                
        except Exception as e:
            print(f"Error in on_topup_clicked: {str(e)}")
            QMessageBox.critical(self, "Top Up Gagal", f"Gagal: {str(e)}") 