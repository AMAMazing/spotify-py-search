# Spotify Song Search (spotify-py-search)

![MIT License](https://img.shields.io/badge/License-MIT-yellow.svg)

A simple desktop application built with Python and PyQt6 that allows you to search for songs using the Spotify API, select your favorites, and save them to a local `tracks.json` file.


*(A screenshot of the application in use, showing search results and selected tracks.)*

## Features

-   **Real-time Search**: Automatically searches Spotify as you type.
-   **Rich Display**: Shows search results with album art, song title, and artist name.
-   **Track Selection**: Click on search results to add them to a "Selected Tracks" grid.
-   **Dynamic Layout**: The selected tracks grid responsively arranges itself.
-   **Unselect Tracks**: Simply click on a selected track to remove it from the list.
-   **Save & Exit**: A "Finish" button saves the details of your selected tracks (thumbnail URL, title, artist) to a `tracks.json` file and closes the application.
-   **Secure Credentials**: Uses a `.env.local` file to securely manage your Spotify API credentials.

## Getting Started

Follow these instructions to get a local copy up and running.

### Prerequisites

-   Python 3.6+
-   A Spotify Developer account to get API credentials.

### Installation & Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/spotify-py-search.git
    cd spotify-py-search
    ```

2.  **Create and activate a virtual environment (recommended):**
    ```bash
    # For Unix/macOS
    python3 -m venv venv
    source venv/bin/activate

    # For Windows
    python -m venv venv
    .\venv\Scripts\activate
    ```

3.  **Install the required packages:**
    The application depends on a few Python libraries. You can install them using pip.
    ```bash
    pip install PyQt6 requests python-dotenv Pillow
    ```

4.  **Set up Spotify API Credentials:**
    -   Go to the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/) and log in.
    -   Click "Create App" or select an existing one.
    -   Note down your **Client ID** and **Client Secret**.
    -   In the root of the project directory, create a new file named `.env.local`.
    -   Add your credentials to this file in the following format:
    ```ini
    # .env.local
    SPOTIFY_CLIENT_ID="your_spotify_client_id_here"
    SPOTIFY_CLIENT_SECRET="your_spotify_client_secret_here"
    ```

### Usage

Once the setup is complete, you can run the application with a single command:

```bash
python main.py
```
*(Assuming the provided script is named `main.py`)*

1.  Start typing the name of a song or artist in the search bar.
2.  Results will appear below the search bar.
3.  Click on any song in the results list to add it to the "Selected Tracks" section at the bottom.
4.  To remove a song, click on it in the "Selected Tracks" section.
5.  When you are done, click the "Finish" button.

## Output

After clicking "Finish", the application will close and a `tracks.json` file will be created in the same directory. The file will contain an array of objects, with each object representing a selected track.

### Example `tracks.json`

```json
[
    {
        "thumbnail": "https://i.scdn.co/image/ab67616d0000b273b5a9b9a9b9a9b9a9b9a9b9a9",
        "title": "Bohemian Rhapsody",
        "artist": "Queen"
    },
    {
        "thumbnail": "https://i.scdn.co/image/ab67616d0000b273c1b1b1b1b1b1b1b1b1b1b1b1",
        "title": "Stairway to Heaven",
        "artist": "Led Zeppelin"
    }
]
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE.md) file for details.