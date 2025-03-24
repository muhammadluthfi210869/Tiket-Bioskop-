import sys
import os
from PyQt5.QtWidgets import QApplication
from flask import Flask
from flask_bcrypt import Bcrypt
import threading
import sqlite3

from gui.login_window import LoginWindow

# Inisialisasi Flask
app = Flask(__name__)
app.secret_key = os.urandom(24)
bcrypt = Bcrypt(app)

# Konfigurasi database
DATABASE = 'bioskop.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with app.app_context():
        db = get_db()
        with open('schema.sql', 'r') as f:
            db.cursor().executescript(f.read())
        db.commit()

# Jalankan server Flask di thread terpisah
def run_flask():
    app.run(debug=False, port=5000)

if __name__ == "__main__":
    # Buat database jika belum ada
    if not os.path.exists(DATABASE):
        init_db()
    
    # Jalankan server Flask di thread terpisah
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    
    # Jalankan aplikasi PyQt
    app_qt = QApplication(sys.argv)
    login_window = LoginWindow(bcrypt)
    login_window.show()
    sys.exit(app_qt.exec_()) 