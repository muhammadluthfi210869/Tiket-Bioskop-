import os

def find_poster_for_film(title):
    """Mencari poster film berdasarkan judul"""
    # Print untuk debugging
    print(f"Mencari poster untuk film: '{title}'")
    
    # Dictionary untuk kasus khusus judul film
    special_cases = {
        "Aladdin": "aladdin.jpg",
        "Avengers: Endgame": "avenger.jpg",
        "Avengers": "avenger.jpg",
        "Batman": "Dark-night.jpg",
        "Captain Marvel": "captain_marvel.jpg", 
        "Joker": "joker.jpg",
        "John Wick: Chapter 3": "John_Wick.jpeg",
        "John Wick": "John_Wick.jpeg",
        "John Wick: Chapter 4": "John_Wick.jpeg",
        "Spider-Man: Far From Home": "Poster_Spider-Man_No_Way_Home.jpg",
        "Spider-Man: No Way Home": "Poster_Spider-Man_No_Way_Home.jpg",
        "Spiderman": "Poster_Spider-Man_No_Way_Home.jpg",
        "The Lion King": "lion_king.jpg",
        "Toy Story 4": "toy_story_4.jpg",
        "The Dark Knight": "Dark-night.jpg",
        "The Batman : Darknight": "Dark-night.jpg",
        "Pulp Fiction": "pulp_fiction.jpg",
        "Inception": "Inception.jpg",
        "Interstellar": "Interstellar.jpg",
        "The Matrix": "Matrix.jpg",
        "The Godfather": "The_Godfather.jpeg",
        "Forrest Gump": "Forrest_Gump_poster.jpg",
        "The Shawshank Redemption": "ShawshankRedemptionMoviePoster.jpg",
        "Bohemian Rhapsody": "Bohemian_Rhapsody.jpg",
        "The Theory of Everything": "The_Theory_of_Everything_(2014).jpg",
        "Dune": "dune.jpg",
        "Dune: Part Two": "dune.jpg",
        "Oppenheimer": "Openheimer.jpeg"
    }
    
    # Cek apakah ada kasus khusus untuk judul ini
    if title in special_cases:
        poster_path = os.path.join("assets", special_cases[title])
        print(f"Menggunakan kasus khusus: {poster_path}")
        if os.path.exists(poster_path):
            print(f"Poster ditemukan di kasus khusus: {poster_path}")
            return poster_path
        else:
            print(f"File poster tidak ditemukan di path: {poster_path}")
    
    # Path ke folder assets
    assets_folder = 'assets'
    
    # Cek apakah folder assets ada
    if not os.path.exists(assets_folder):
        print(f"Folder assets tidak ditemukan")
        return os.path.join("assets", "no_poster.jpg")
    
    # Normalisasi judul untuk pencarian file
    normalized_title = title.lower().replace(' ', '_').replace(':', '').replace('-', '_')
    print(f"Judul dinormalisasi menjadi: {normalized_title}")
    
    # Cek semua file di folder assets
    file_list = os.listdir(assets_folder)
    print(f"Daftar file di assets: {file_list}")
    
    for filename in file_list:
        # Jika nama file mengandung judul film
        file_lower = filename.lower()
        if normalized_title in file_lower or title.lower().replace(' ', '') in file_lower:
            poster_path = os.path.join(assets_folder, filename)
            print(f"Poster ditemukan berdasarkan nama: {poster_path}")
            return os.path.join(assets_folder, filename)
    
    # Jika tidak menemukan kecocokan persis, coba dengan sebagian judul
    for filename in file_list:
        file_lower = filename.lower()
        words = title.lower().split()
        for word in words:
            if len(word) > 3 and word in file_lower:  # Cari kata dengan panjang >3 karakter
                poster_path = os.path.join(assets_folder, filename)
                print(f"Poster ditemukan berdasarkan kata kunci '{word}': {poster_path}")
                return os.path.join(assets_folder, filename)
    
    print(f"Tidak menemukan poster untuk '{title}', menggunakan default")
    # Default placeholder
    return os.path.join("assets", "no_poster.jpg")

def create_movie_card(movie_data):
    """Fungsi helper untuk membuat movie card"""
    from gui.movies_page import MovieCard
    return MovieCard(movie_data) 