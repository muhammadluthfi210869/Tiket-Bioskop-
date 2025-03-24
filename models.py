import sqlite3
from flask_bcrypt import Bcrypt
from datetime import datetime

# Konfigurasi database
DATABASE = 'bioskop.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Inisialisasi database dan buat tabel jika belum ada"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Buat tabel movies jika belum ada
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS movies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            genre TEXT NOT NULL,
            duration INTEGER NOT NULL,
            price INTEGER NOT NULL,
            synopsis TEXT,
            director TEXT,
            cast TEXT,
            schedule TEXT,
            imdb_rating TEXT,
            poster_path TEXT
        )
    ''')
    
    # Buat tabel users jika belum ada
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nama TEXT NOT NULL,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            usia INTEGER NOT NULL,
            genre_favorit TEXT,
            saldo INTEGER DEFAULT 0
        )
    ''')
    
    conn.commit()
    conn.close()

class MovieModel:
    @staticmethod
    def initialize_movies():
        """Inisialisasi data film jika tabel kosong"""
        try:
            conn = get_db()
            cursor = conn.cursor()
            
            # Cek apakah tabel sudah ada data
            cursor.execute("SELECT COUNT(*) FROM movies")
            count = cursor.fetchone()[0]
            
            if count == 0:
                # Masukkan data dummy ke database
                dummy_movies = MovieModel.get_dummy_movies()
                for movie in dummy_movies:
                    cursor.execute("""
                        INSERT INTO movies (title, genre, duration, price, synopsis, director, cast, schedule, imdb_rating)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        movie['title'],
                        movie['genre'],
                        movie['duration'],
                        movie['price'],
                        movie['synopsis'],
                        movie['director'],
                        movie['cast'],
                        movie['schedule'],
                        movie['imdb_rating']
                    ))
                
                conn.commit()
                print("Data film berhasil diinisialisasi")
            
            conn.close()
            
        except Exception as e:
            print(f"Error initializing movies: {str(e)}")
    
    @staticmethod
    def get_all_movies():
        """Mendapatkan semua data film"""
        try:
            conn = get_db()
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM movies")
            movies = cursor.fetchall()
            
            conn.close()
            
            if movies:
                return [dict(movie) for movie in movies]
            else:
                # Jika tidak ada data, inisialisasi dan ambil lagi
                MovieModel.initialize_movies()
                return MovieModel.get_all_movies()
                
        except sqlite3.OperationalError as e:
            if "no such table" in str(e):
                # Jika tabel belum ada, buat tabel dan inisialisasi
                init_db()
                MovieModel.initialize_movies()
                return MovieModel.get_all_movies()
            else:
                print(f"Database error: {str(e)}")
                return MovieModel.get_dummy_movies()
        except Exception as e:
            print(f"Error: {str(e)}")
            return MovieModel.get_dummy_movies()
    
    @staticmethod
    def get_dummy_movies():
        """Data film dummy jika database belum ada"""
        return [
            {
                "id": 1,
                "title": "Avengers: Endgame",
                "genre": "Action",
                "duration": 181,
                "price": 45000,
                "synopsis": "Adrift in space with no food or water, Tony Stark sends a message to Pepper Potts as his oxygen supply starts to dwindle. Meanwhile, the remaining Avengers -- Thor, Black Widow, Captain America and Bruce Banner -- must figure out a way to bring back their vanquished allies for an epic showdown with Thanos.",
                "director": "Anthony Russo, Joe Russo",
                "cast": "Robert Downey Jr., Chris Evans, Mark Ruffalo",
                "schedule": "10:00, 13:00, 16:00, 19:00",
                "imdb_rating": "8.4",
                "age_rating": "13",
                "release_date": "2019"
            },
            {
                "id": 2,
                "title": "Joker",
                "genre": "Crime, Drama",
                "duration": 122,
                "price": 40000,
                "synopsis": "Forever alone in a crowd, failed comedian Arthur Fleck seeks connection as he walks the streets of Gotham City. Arthur wears two masks -- the one he paints for his day job as a clown, and the guise he projects in a futile attempt to feel like he's part of the world around him.",
                "director": "Todd Phillips",
                "cast": "Joaquin Phoenix, Robert De Niro, Zazie Beetz",
                "schedule": "11:00, 14:00, 17:00, 20:00",
                "imdb_rating": "8.4",
                "age_rating": "17",
                "release_date": "2019"
            },
            {
                "id": 3,
                "title": "The Lion King",
                "genre": "Animation, Adventure",
                "duration": 118,
                "price": 35000,
                "synopsis": "Simba idolizes his father, King Mufasa, and takes to heart his own royal destiny on the plains of Africa. But not everyone in the kingdom celebrates the new cub's arrival. Scar, Mufasa's brother -- and former heir to the throne -- has plans of his own.",
                "director": "Jon Favreau",
                "cast": "Donald Glover, Beyoncé, Seth Rogen",
                "schedule": "09:00, 12:00, 15:00, 18:00",
                "imdb_rating": "6.9",
                "age_rating": "7",
                "release_date": "2019"
            },
            {
                "id": 4,
                "title": "Spider-Man: Far From Home",
                "genre": "Action, Adventure",
                "duration": 129,
                "price": 40000,
                "synopsis": "Following the events of Avengers: Endgame, Spider-Man must step up to take on new threats in a world that has changed forever.",
                "director": "Jon Watts",
                "cast": "Tom Holland, Zendaya, Jake Gyllenhaal",
                "schedule": "10:30, 13:30, 16:30, 19:30",
                "imdb_rating": "7.5",
                "age_rating": "13",
                "release_date": "2019"
            },
            {
                "id": 5,
                "title": "Aladdin",
                "genre": "Adventure, Family",
                "duration": 128,
                "price": 35000,
                "synopsis": "A kind-hearted street urchin and a power-hungry Grand Vizier vie for a magic lamp that has the power to make their deepest wishes come true.",
                "director": "Guy Ritchie",
                "cast": "Will Smith, Mena Massoud, Naomi Scott",
                "schedule": "09:30, 12:30, 15:30, 18:30",
                "imdb_rating": "7.0",
                "age_rating": "7",
                "release_date": "2019"
            },
            {
                "id": 6,
                "title": "Toy Story 4",
                "genre": "Animation, Adventure",
                "duration": 100,
                "price": 35000,
                "synopsis": "Woody, Buzz Lightyear and the rest of the gang embark on a road trip with Bonnie and a new toy named Forky. The adventurous journey turns into an unexpected reunion as Woody's slight detour leads him to his long-lost friend Bo Peep.",
                "director": "Josh Cooley",
                "cast": "Tom Hanks, Tim Allen, Annie Potts",
                "schedule": "10:00, 13:00, 16:00, 19:00",
                "imdb_rating": "7.8",
                "age_rating": "7",
                "release_date": "2019"
            },
            {
                "id": 7,
                "title": "John Wick: Chapter 3",
                "genre": "Action, Crime",
                "duration": 131,
                "price": 40000,
                "synopsis": "After gunning down a member of the High Table -- the shadowy international assassin's guild -- legendary hit man John Wick finds himself stripped of the organization's protective services. Now stuck with a $14 million bounty on his head, Wick must fight his way through the streets of New York as he becomes the target of the world's most ruthless killers.",
                "director": "Chad Stahelski",
                "cast": "Keanu Reeves, Halle Berry, Ian McShane",
                "schedule": "11:30, 14:30, 17:30, 20:30",
                "imdb_rating": "7.4",
                "age_rating": "17",
                "release_date": "2019"
            },
            {
                "id": 8,
                "title": "Captain Marvel",
                "genre": "Action, Adventure",
                "duration": 123,
                "price": 40000,
                "synopsis": "Captain Marvel is an extraterrestrial Kree warrior who finds herself caught in the middle of an intergalactic battle between her people and the Skrulls. Living on Earth in 1995, she keeps having recurring memories of another life as U.S. Air Force pilot Carol Danvers. With help from Nick Fury, Captain Marvel tries to uncover the secrets of her past while harnessing her special superpowers to end the war with the evil Skrulls.",
                "director": "Anna Boden, Ryan Fleck",
                "cast": "Brie Larson, Samuel L. Jackson, Ben Mendelsohn",
                "schedule": "09:00, 12:00, 15:00, 18:00",
                "imdb_rating": "6.8",
                "age_rating": "13",
                "release_date": "2019"
            }
        ]
    
    @staticmethod
    def get_movie_by_id(movie_id):
        """Mendapatkan data film berdasarkan id"""
        try:
            conn = get_db()
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM movies WHERE id = ?", (movie_id,))
            movie = cursor.fetchone()
            
            conn.close()
            
            if movie:
                return dict(movie)
            else:
                return None
                
        except Exception as e:
            print(f"Error: {str(e)}")
            return None

class UserModel:
    @staticmethod
    def get_db():
        """Mendapatkan koneksi database"""
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row
        return conn
    
    @staticmethod
    def login_user(username, password, bcrypt):
        """Verifikasi login pengguna"""
        try:
            conn = UserModel.get_db()
            cursor = conn.cursor()
            
            # Cari pengguna dengan username yang diberikan
            cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
            user = cursor.fetchone()
            
            conn.close()
            
            if user is None:
                return False, "Username tidak ditemukan", None
            
            # Verifikasi password
            stored_password = user["password"]
            if bcrypt.check_password_hash(stored_password, password):
                return True, "Login berhasil", dict(user)
            else:
                return False, "Password salah", None
                
        except Exception as e:
            return False, f"Error: {str(e)}", None
    
    @staticmethod
    def register_user(nama, username, password, usia, genre_favorit, bcrypt):
        """Mendaftarkan pengguna baru"""
        try:
            conn = UserModel.get_db()
            cursor = conn.cursor()
            
            # Cek apakah username sudah ada
            cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
            if cursor.fetchone() is not None:
                conn.close()
                return False, "Username sudah digunakan"
            
            # Hash password
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
            
            # Insert pengguna baru
            cursor.execute(
                "INSERT INTO users (username, password, nama, usia, genre_favorit, saldo) VALUES (?, ?, ?, ?, ?, ?)",
                (username, hashed_password, nama, usia, genre_favorit, 0)
            )
            conn.commit()
            conn.close()
            return True, "Registrasi berhasil"
            
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    @staticmethod
    def get_user(username):
        """Mendapatkan data pengguna"""
        try:
            conn = UserModel.get_db()
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
            user = cursor.fetchone()
            
            conn.close()
            
            if user:
                return dict(user)
            else:
                return None
                
        except Exception as e:
            print(f"Error: {str(e)}")
            return None
    
    @staticmethod
    def get_saldo(username):
        """Mendapatkan saldo pengguna"""
        try:
            conn = UserModel.get_db()
            cursor = conn.cursor()
            
            cursor.execute("SELECT saldo FROM users WHERE username = ?", (username,))
            result = cursor.fetchone()
            
            conn.close()
            
            if result:
                return result["saldo"]
            else:
                return 0
                
        except Exception as e:
            print(f"Error: {str(e)}")
            return 0
    
    @staticmethod
    def update_saldo(username, amount):
        """Update saldo pengguna"""
        try:
            conn = UserModel.get_db()
            cursor = conn.cursor()
            
            # Ambil saldo saat ini
            cursor.execute("SELECT saldo FROM users WHERE username = ?", (username,))
            result = cursor.fetchone()
            
            if not result:
                conn.close()
                return False, "Pengguna tidak ditemukan", 0
            
            current_saldo = result["saldo"]
            new_saldo = current_saldo + amount
            
            # Pastikan saldo tidak negatif saat pengurangan
            if amount < 0 and new_saldo < 0:
                conn.close()
                return False, "Saldo tidak mencukupi", current_saldo
            
            # Update saldo
            cursor.execute(
                "UPDATE users SET saldo = ? WHERE username = ?",
                (new_saldo, username)
            )
            conn.commit()
            conn.close()
            
            return True, "Saldo berhasil diperbarui", new_saldo
            
        except Exception as e:
            return False, f"Error: {str(e)}", 0 