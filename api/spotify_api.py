import os
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from scipy.spatial import distance

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
    
def search_track(track_name):
    results = sp.search(q=f'track:{track_name}', type='track', limit=1)
    if results['tracks']['items']:
        return results['tracks']['items'][0]
    else:
        return None

def compare_two_tracks(track_id1, track_id2):
    features1 = get_track_features(track_id1)
    features2 = get_track_features(track_id2)

    comparison = {}
    for feature in csv_columns:
        if feature in features1 and feature in features2:
            comparison[feature] = {
                'track_1': features1[feature],
                'track_2': features2[feature]
            }

    return comparison

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
            'popularity': track['popularity'],
        }
        track_data.update(get_track_features(track['id']))
        top_tracks.append(track_data)
    
    return top_tracks

def get_related_genres(artist_name):
    results = sp.search(q=f'artist:{artist_name}', type='artist')
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

def get_popular_related_tracks_by_related_artist(artist_name, min_followers=50000):
    related_artists = get_related_artists(artist_name)
    popular_artists = filter_popular_artists(related_artists, min_followers)

    all_tracks = []
    for artist in popular_artists:
        artist_tracks = get_top_tracks(artist['id'], artist['name'])
        all_tracks.extend(artist_tracks)
    return all_tracks

def find_similar_tracks_by_recommendations(track_id, max_results=100):
    """
    Finds tracks with similar audio features to the given track ID.
    
    :param track_id: Spotify ID of the track to find similar tracks for.
    :param max_results: Number of similar tracks to find.
    :return: List of similar tracks.
    """
    similar_tracks = sp.recommendations(seed_tracks=[track_id], limit=max_results)
    track_data_list = []
    for track in similar_tracks['tracks']:
        artist_name = ', '.join([artist['name'] for artist in track['artists']])
        track_data = {
            'id': track['id'],
            'name': track['name'],
            'artist': artist_name,
            'release_date': track['album']['release_date'],
            'popularity': track['popularity'],
        }
        track_data.update(get_track_features(track['id']))
        track_data_list.append(track_data)
    return track_data_list

def get_popular_similar_tracks_by_recommendations(artist_name, min_followers=50000, max_results=20):
    """
    Finds popular tracks with similar audio features to a track by the given artist.
    
    :param artist_name: Name of the artist to find a reference track.
    :param min_followers: Minimum number of followers to consider an artist popular.
    :param max_results: Maximum number of similar tracks to retrieve.
    :return: List of popular similar tracks.
    """
    # Step 1: Find the top track of the given artist
    artist_search = sp.search(q=f'artist:{artist_name}', type='artist')
    if not artist_search['artists']['items']:
        print(f"No artist found for {artist_name}")
        return []

    artist_id = artist_search['artists']['items'][0]['id']
    top_tracks = get_top_tracks(artist_id,artist_name)
    if not top_tracks:
        print(f"No tracks found for artist {artist_name}")
        return []
    
    reference_track = top_tracks[0]  # Using the first track as the reference

    # Step 2: Find similar tracks based on audio features
    similar_tracks = find_similar_tracks_by_recommendations(reference_track['id'], max_results)

    # Step 3: Filter the similar tracks for popular artists
    popular_similar_tracks = []
    for track in similar_tracks:
        track_artists = sp.track(track['id'])['artists']
        for artist in track_artists:
            artist_details = sp.artist(artist['id'])
            if artist_details['followers']['total'] > min_followers:
                popular_similar_tracks.append(track)
                break

    return popular_similar_tracks

def calculate_feature_similarity(features1, features2):
    # Extract numeric feature values for similarity calculation
    feature_values1 = [features1[key] for key in features1 if isinstance(features1[key], (int, float))]
    feature_values2 = [features2[key] for key in features2 if isinstance(features2[key], (int, float))]
    return distance.euclidean(feature_values1, feature_values2)

def get_most_similar_tracks(reference_track, similar_tracks, top_n=5):
    reference_features = get_track_features(reference_track['id'])
    track_similarity = []

    for track in similar_tracks:
        track_features = {key: track[key] for key in csv_columns if key in track}
        similarity = calculate_feature_similarity(reference_features, track_features)
        track_similarity.append((track, similarity))

    # Sort tracks by similarity, then by popularity
    track_similarity.sort(key=lambda x: (x[1], -x[0].get('popularity',0)))

    return [track[0] for track in track_similarity[:top_n]]

if __name__ == "__main__":
    # Example: Replace with actual user inputs
    track_name_1 = 'STUCK'
    track_name_2 = 'IF THE SPIRITS COME OVER'

    track_1 = search_track(track_name_1)
    track_2 = search_track(track_name_2)

    if track_1 and track_2:
        track_id_1 = track_1['id']
        track_id_2 = track_2['id']

        comparison = compare_two_tracks(track_id_1, track_id_2)
        print(comparison)
    else:
        print("One or both tracks not found.")