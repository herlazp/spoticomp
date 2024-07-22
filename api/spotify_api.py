import os
import csv
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

# Get Spotify API credentials from environment variables
client_id = os.getenv('SPOTIPY_CLIENT_ID')
client_secret = os.getenv('SPOTIPY_CLIENT_SECRET')

# Initialize Spotify client
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=client_id, client_secret=client_secret))

# Define the CSV columns
csv_columns = ['id', 'name', 'danceability', 'energy', 'key', 'loudness', 'mode', 'speechiness',
                'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo', 'duration_ms',
                'time_signature', 'release_date']

def get_track_features(track_id):
    """
    Fetches the audio features for a given track ID.

    :param track_id: Spotify track ID
    :return: Dictionary containing track features
    """
    features = sp.audio_features(track_id)[0]
    # Select only the required features
    selected_features = {key: features[key] for key in csv_columns[:-1] if key != 'name'}
    return selected_features
    
def get_all_tracks_by_artist(artist_name):
    """
    Fetches all tracks by a given artist.

    :param artist_name: Name of the artist
    :return: List of track dictionaries
    """
    results = sp.search(q=f'artist:{artist_name}', type='track', limit=50)
    tracks = results['tracks']['items']
    return tracks

def save_track_features_to_csv(artist_name):
    """
    Saves the audio features of all tracks by a given artist to a CSV file.

    :param artist_name: Name of the artist
    """
    tracks = get_all_tracks_by_artist(artist_name)
    features_dict = {}

    # Load existing features if file exists
    filename = f"{artist_name}_features.csv"
    existing_track_ids = set()
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                existing_track_ids.add(row['id'])

    # Fetch track features, iterate over all tracks and select the latest version of each song
    for track in tracks:
        track_id = track['id']
        track_name = track['name']
        album_release_date = track['album']['release_date']

        if track_id not in existing_track_ids:
            features = get_track_features(track_id)
            features['name'] = track_name
            features['release_date'] = album_release_date

            # Convert release date to datetime object for comparison
            release_date_dt = datetime.strptime(album_release_date, '%Y-%m-%d')

            # Check if this song is already in the dictionary and if the current one is newer
            if track_name not in features_dict or release_date_dt < features_dict[track_name]['release_date']:
                features_dict[track_name] = {
                    **features,
                    'release_date': release_date_dt
                }

    # Write features to CSV file
    with open(filename, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=csv_columns)
        writer.writeheader()
        for track in features_dict.values():
            # Convert release_date back to string format for CSV
            track['release_date'] = track['release_date'].strftime('%Y-%m-%d')
            writer.writerow(track)

if __name__ == "__main__":
    artist_name = 'Ignomala'  # Replace with your artist name
    save_track_features_to_csv(artist_name)