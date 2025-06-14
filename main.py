import sys
import os
import json
import requests
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QScrollArea,
    QFrame, QHBoxLayout, QGridLayout, QSizePolicy, QPushButton
)
from PyQt6.QtGui import QPixmap, QFont
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv
from io import BytesIO
from PIL import Image
from PIL.ImageQt import ImageQt

# Load environment variables from .env.local
load_dotenv('.env.local')

CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')

# Function to get Spotify access token
def get_access_token():
    url = 'https://accounts.spotify.com/api/token'
    data = {'grant_type': 'client_credentials'}
    response = requests.post(url, data=data, auth=HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET))
    token_info = response.json()
    return token_info['access_token']

# Function to search for songs
def search_songs(query):
    token = get_access_token()
    search_url = 'https://api.spotify.com/v1/search'
    headers = {'Authorization': f'Bearer {token}'}
    params = {'q': query, 'type': 'track', 'limit': 10}
    response = requests.get(search_url, headers=headers, params=params)

    if response.status_code == 200:
        return response.json()['tracks']['items']
    else:
        return []

# Thread class to handle background search
class SearchThread(QThread):
    results_ready = pyqtSignal(list)

    def __init__(self, query):
        super().__init__()
        self.query = query

    def run(self):
        songs = search_songs(self.query)
        self.results_ready.emit(songs)

# Custom QFrame for song items
class SongFrame(QFrame):
    def __init__(self, song, click_callback):
        super().__init__()
        self.song = song
        self.click_callback = click_callback

    def mouseReleaseEvent(self, event):
        self.click_callback(self.song)

# Custom QFrame for selected tracks
class SelectedTrackFrame(QFrame):
    def __init__(self, song, unselect_callback):
        super().__init__()
        self.song = song
        self.unselect_callback = unselect_callback

    def mouseReleaseEvent(self, event):
        self.unselect_callback(self.song['id'])

# Main PyQt6 App
class SpotifySearchApp(QWidget):
    def __init__(self):
        super().__init__()

        # Set up window
        self.setWindowTitle('Spotify Song Search')
        self.setGeometry(100, 100, 1000, 800)

        # Layout for the app
        self.layout = QVBoxLayout()

        # Search bar
        self.search_input = QLineEdit(self)
        self.search_input.setPlaceholderText("Search for a song or artist...")
        self.search_input.setFont(QFont("Arial", 16))  # Larger font size
        self.search_input.setMinimumHeight(40)
        self.search_input.textChanged.connect(self.on_text_change)
        self.layout.addWidget(self.search_input)

        # Scroll area to display results
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_content = QVBoxLayout()
        self.scroll_widget = QWidget()
        self.scroll_widget.setLayout(self.scroll_content)
        self.scroll_area.setWidget(self.scroll_widget)
        self.layout.addWidget(self.scroll_area)

        # Selected tracks grid
        self.selected_tracks = QGridLayout()
        self.selected_tracks_widget = QWidget()
        self.selected_tracks_widget.setLayout(self.selected_tracks)
        self.selected_scroll_area = QScrollArea(self)
        self.selected_scroll_area.setWidgetResizable(True)
        self.selected_scroll_area.setWidget(self.selected_tracks_widget)
        self.layout.addWidget(QLabel("Selected Tracks:", self, font=QFont("Arial", 16)))
        self.layout.addWidget(self.selected_scroll_area)

        # Finish button
        self.finish_button = QPushButton("Finish", self)
        self.finish_button.setFont(QFont("Arial", 16))
        self.finish_button.clicked.connect(self.save_selected_tracks_and_exit)
        self.layout.addWidget(self.finish_button)

        # Timer for search on typing
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self.perform_search)

        # Set the layout for the window
        self.setLayout(self.layout)

        self.search_thread = None
        self.selected_songs = {}

    def on_text_change(self):
        # Reset the timer every time the user types
        self.search_timer.start(500)

    def perform_search(self):
        query = self.search_input.text()
        if query:
            # Start background thread for searching
            self.search_thread = SearchThread(query)
            self.search_thread.results_ready.connect(self.display_results)
            self.search_thread.start()

    def display_results(self, songs):
        # Clear previous results
        for i in reversed(range(self.scroll_content.count())):
            widget_to_remove = self.scroll_content.itemAt(i).widget()
            widget_to_remove.setParent(None)

        # Display new results
        for song in songs:
            song_frame = SongFrame(song, self.song_clicked)
            song_layout = QHBoxLayout()

            # Get album image
            album_cover_url = song['album']['images'][0]['url']
            response = requests.get(album_cover_url)
            img_data = response.content
            img = Image.open(BytesIO(img_data))
            qt_img = ImageQt(img)
            pixmap = QPixmap.fromImage(qt_img)

            # Image label
            img_label = QLabel(self)
            img_label.setPixmap(pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio))
            img_label.setStyleSheet("background-color: transparent;")
            img_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
            song_layout.addWidget(img_label)

            # Song information
            song_info = QVBoxLayout()
            title_label = QLabel(f"Title: {song['name']}")
            title_label.setFont(QFont("Arial", 14))
            title_label.setWordWrap(True)
            title_label.setStyleSheet("background-color: transparent;")
            title_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

            artist_label = QLabel(f"Artist: {', '.join([artist['name'] for artist in song['artists']])}")
            artist_label.setFont(QFont("Arial", 12))
            artist_label.setWordWrap(True)
            artist_label.setStyleSheet("background-color: transparent;")
            artist_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

            song_info.addWidget(title_label)
            song_info.addWidget(artist_label)
            song_info.addStretch()

            song_layout.addLayout(song_info)
            song_frame.setLayout(song_layout)

            # Style the frame
            song_frame.setStyleSheet("""
                QFrame {
                    background-color: #333;
                    color: white;
                }
                QFrame:hover {
                    background-color: #444;
                }
            """)

            # Add the frame to the scroll content
            self.scroll_content.addWidget(song_frame)

    def song_clicked(self, song):
        track_id = song['id']
        if track_id not in self.selected_songs:
            self.selected_songs[track_id] = song
            self.refresh_selected_tracks()

    def refresh_selected_tracks(self):
        # Clear previous selected tracks
        for i in reversed(range(self.selected_tracks.count())):
            widget_to_remove = self.selected_tracks.itemAt(i).widget()
            widget_to_remove.setParent(None)

        # Number of columns (3 tracks per row)
        columns = 3
        total_songs = len(self.selected_songs)
        num_rows = (total_songs + columns - 1) // columns  # Calculate the number of rows needed

        # Ensure at least one row
        if num_rows == 0:
            num_rows = 1

        # Set equal stretch factors for rows and columns
        for c in range(columns):
            self.selected_tracks.setColumnStretch(c, 1)

        for r in range(num_rows):
            self.selected_tracks.setRowStretch(r, 1)

        row = 0
        col = 0
        for song in self.selected_songs.values():
            track_frame = SelectedTrackFrame(song, self.unselect_song)
            track_layout = QVBoxLayout()
            track_layout.setContentsMargins(5, 5, 5, 5)  # Padding for consistent spacing
            track_layout.setSpacing(5)

            # Album image
            album_cover_url = song['album']['images'][0]['url']
            response = requests.get(album_cover_url)
            img_data = response.content
            img = Image.open(BytesIO(img_data))
            qt_img = ImageQt(img)
            pixmap = QPixmap.fromImage(qt_img)

            img_label = QLabel(self)
            img_label.setPixmap(pixmap.scaled(
                130, 130, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            img_label.setStyleSheet("background-color: transparent;")
            track_layout.addWidget(img_label, alignment=Qt.AlignmentFlag.AlignCenter)

            # Song title
            title_label = QLabel(f"{song['name']}")
            title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            title_label.setWordWrap(True)
            title_label.setStyleSheet("background-color: transparent;")
            title_label.setFont(QFont("Arial", 12))  # Reduced font size for long titles
            title_label.setMinimumHeight(50)  # Ensure enough height for longer titles
            track_layout.addWidget(title_label, alignment=Qt.AlignmentFlag.AlignCenter)

            # Artist names
            artist_label = QLabel(f"{', '.join([artist['name'] for artist in song['artists']])}")
            artist_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            artist_label.setWordWrap(True)
            artist_label.setStyleSheet("background-color: transparent;")
            artist_label.setFont(QFont("Arial", 10))  # Slightly reduced font size
            artist_label.setMinimumHeight(40)  # Ensure enough height for artists
            track_layout.addWidget(artist_label, alignment=Qt.AlignmentFlag.AlignCenter)

            track_frame.setLayout(track_layout)

            # Apply the stylesheet directly to the frame
            track_frame.setStyleSheet("""
                QFrame {
                    background-color: #555;
                    color: white;
                    border-radius: 5px;
                    padding: 1px;
                    margin: 1px;
                }
                QFrame:hover {
                    background-color: #666;
                }
            """)

            # Add the frame to the grid layout
            self.selected_tracks.addWidget(track_frame, row, col)

            # Move to the next grid cell
            col += 1
            if col >= columns:
                col = 0
                row += 1

        # Ensure the selected_tracks_widget expands to fill the scroll area
        self.selected_tracks_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.selected_scroll_area.setWidgetResizable(True)

    def unselect_song(self, track_id):
        if track_id in self.selected_songs:
            del self.selected_songs[track_id]
            self.refresh_selected_tracks()

    def save_selected_tracks_and_exit(self):
        # Get the directory where the Python file is located
        script_dir = os.path.dirname(os.path.abspath(__file__))

        # Define the path where the file will be saved
        file_path = os.path.join(script_dir, 'tracks.json')

        # Create a new dictionary with only the required fields
        minimal_tracks = [
            {
                'thumbnail': song['album']['images'][0]['url'],
                'title': song['name'],
                'artist': ', '.join([artist['name'] for artist in song['artists']])
            }
            for song in self.selected_songs.values()
        ]

        # Save the selected tracks to the JSON file
        with open(file_path, 'w') as f:
            json.dump(minimal_tracks, f, indent=4)

        print(f"Selected tracks saved to {file_path}")

        # Exit the application after saving
        QApplication.quit()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.refresh_selected_tracks()

# Main Function to run the PyQt6 app
if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Create and show the main window
    window = SpotifySearchApp()
    window.show()

    # Execute the app
    sys.exit(app.exec())
