import os
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# Load environment variables from .env file
load_dotenv()

# Get Spotify API credentials from environment variables
client_id = os.getenv('SPOTIPY_CLIENT_ID')
client_secret = os.getenv('SPOTIPY_CLIENT_SECRET')

# Initialize Spotify client
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=client_id, client_secret=client_secret))

def get_track_features(track_id):
    """
    Fetches the audio features for a given track ID.

    :param track_id: Spotify track ID
    :return: Dictionary containing track features
    """
    features = sp.audio_features(track_id)[0]
    return features
    
if __name__ == "__main__":
    # Test track ID for demonstration
    test_track_id = '3n3Ppam7vgaVa1iaRUc9Lp'  # Replace with your track ID

    # Fetch track features
    track_features = get_track_features(test_track_id)
    
    # Print the track features to see what you get from the API
    print(track_features)