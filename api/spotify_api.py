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

def get_top_tracks(artist_id, artist_name, track_limit=5):
    results = sp.artist_top_tracks(artist_id)
    tracks = results['tracks'][:track_limit]
    top_tracks = []
    for track in tracks:
        track_data = {
            'id': track['id'],
            'name': track['name'],
            'artist': artist_name,
            'release_date': track['album']['release_date'],
        }
        track_data.update(get_track_features(track['id']))
        top_tracks.append(track_data)
    
    return top_tracks

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

def get_related_artists(artist_name):
    results = sp.search(q=f'artist:{artist_name}', type='artist')
    if not results['artists']['items']:
        return []
    
    artist_id = results['artists']['items'][0]['id']
    related_artists = sp.artist_related_artists(artist_id)
    return related_artists['artists']

def filter_popular_artists(artists, min_followers=50000):
    popular_artists = [artist for artist in artists if artist['followers']['total'] > min_followers]
    popular_artists_sorted = sorted(popular_artists, key=lambda x: x['followers']['total'], reverse=True)
    return popular_artists_sorted

def get_popular_related_tracks(artist_name, min_followers=50000):
    related_artists = get_related_artists(artist_name)
    print(related_artists)
    popular_artists = filter_popular_artists(related_artists, min_followers)
    print(popular_artists)

    all_tracks = []
    for artist in popular_artists:
        artist_tracks = get_top_tracks(artist['id'], artist['name'])
        all_tracks.extend(artist_tracks)
    return all_tracks

if __name__ == "__main__":
    artist_name = 'Ignomala'  # Replace with your artist name
    popular_tracks = get_popular_related_tracks(artist_name, min_followers=100000)
    for track in popular_tracks:
        print(f"Track: {track['name']} by {track['artist']} (Release Date: {track['release_date']})")
        print(f"Features: {track}")