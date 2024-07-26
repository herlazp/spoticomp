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

def get_related_genres(artist_name):
    results = sp.search(q=f'artist:{artist_name}', type='artist')
    print(results)
    artist = results['artists']['items'][0]
    genres = artist['genres']
    return genres

def get_popular_artists(genres):
    popular_artists = []
    for genre in genres:
        results = sp.search(q=f'genre:{genre}', type='artist', limit=50)
        for artist in results['artists']['items']:
            popular_artists.append(artist['name'])
    return popular_artists

def get_popular_tracks(artist_name):
    results = sp.search(q=f'artist:{artist_name}', type='track', limit=10)
    tracks = results['tracks']['items']
    return tracks

def get_popular_playlists(genre):
    results = sp.search(q=f'genre:{genre}', type='playlist', limit=10)
    playlists = results['playlists']['items']
    return playlists

def get_playlist_tracks(playlist_id):
    results = sp.playlist_tracks(playlist_id)
    tracks = results['items']
    return [track['track'] for track in tracks]

def get_related_artists_tracks(artist_name, include_audio_features=False):
    """
    Fetches top tracks of related artists to the specified artist.
    
    Parameters:
    artist_name (str): The name of the artist to find related artists for.
    include_audio_features (bool): If True, include audio features for the tracks.
    
    Returns:
    list: A list of dictionaries containing track details, and optionally audio features.
    """
    # Search for the artist ID
    result = sp.search(q='artist:' + artist_name, type='artist')
    if not result['artists']['items']:
        return f"Artist '{artist_name}' not found."

    artist_id = result['artists']['items'][0]['id']

    # Get related artists
    related_artists = sp.artist_related_artists(artist_id)
    related_artist_ids = [artist['id'] for artist in related_artists['artists']]

    # Get top tracks of related artists
    related_tracks = []
    for artist_id in related_artist_ids:
        top_tracks = sp.artist_top_tracks(artist_id, country='US')
        related_tracks.extend(top_tracks['tracks'])

    # Optionally fetch audio features
    if include_audio_features:
        track_ids = [track['id'] for track in related_tracks]
        audio_features = sp.audio_features(track_ids)
        # Combine track details with audio features
        for track, features in zip(related_tracks, audio_features):
            track['audio_features'] = features

    return related_tracks

if __name__ == "__main__":
    artist_name = 'Ignomala'  # Replace with your artist name
    related_tracks = get_related_artists_tracks(artist_name)
    print (related_tracks)