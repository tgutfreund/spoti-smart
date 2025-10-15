import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class SpotifyClient:
    """A client to interact with the Spotify API"""
    def __init__(self):
        self.client_id = os.getenv('SPOTIFY_CLIENT_ID')
        self.client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
        self.redirect_uri = os.getenv('SPOTIFY_REDIRECT_URI')
        
        self.scope = [
            "user-top-read",
            "user-library-read", 
            "playlist-modify-private",
            "playlist-modify-public",
            "user-read-recently-played"
        ]
        
        self.sp = None
        
    def authenticate(self):
        """Authenticate and create a Spotify client"""
        try:
            auth_manager = SpotifyOAuth(
                client_id=self.client_id,
                client_secret=self.client_secret,
                redirect_uri=self.redirect_uri,
                scope=self.scope,
                cache_path=".spotify_cache"
            )
            self.sp = spotipy.Spotify(auth_manager=auth_manager)
            user = self.sp.current_user()
            print(f"Successfully authenticated as: {user['display_name']}")
            return self.sp
        except Exception as e:
            print(f"Authentication failed: {e}")
            return None
    
    def get_user_top_tracks(self, limit=10, time_range='medium_term'):
        """Get user's top tracks"""
        if not self.sp:
            print("Client not authenticated. Please run authenticate() first.")
            return None
        try:
            results = self.sp.current_user_top_tracks(
                limit=limit, 
                time_range=time_range
            )
            return results['items']
        except Exception as e:
            print(f"Error fetching top tracks: {e}")
            return None

    def create_playlist(self, name, description=""):
        """Creates a new playlist for the current user."""
        if not self.sp:
            print("Client not authenticated.")
            return None
        try:
            user_id = self.sp.current_user()['id']
            playlist = self.sp.user_playlist_create(
                user=user_id,
                name=name,
                public=True, 
                description=description
            )
            print(f"Successfully created playlist: '{name}'")
            return playlist['id']
        except Exception as e:
            print(f"Error creating playlist: {e}")
            return None

    def add_tracks_to_playlist(self, playlist_id, track_uris):
        """Adds a list of tracks (by URI) to a playlist."""
        if not self.sp or not track_uris:
            print("Client not authenticated or no tracks to add.")
            return
        try:
            self.sp.playlist_add_items(playlist_id, track_uris)
            print(f"Successfully added {len(track_uris)} tracks to the playlist.")
        except Exception as e:
            print(f"Error adding tracks: {e}")
    # In src/spotify_client.py, add this new method to the SpotifyClient class

    def search_for_track(self, song_name, artist_name):
        """Searches for a track on Spotify and returns its URI."""
        if not self.sp:
            return None
        try:
            # Search query combining song name and artist name
            query = f"track:{song_name} artist:{artist_name}"
            results = self.sp.search(q=query, type='track', limit=1)
            
            items = results['tracks']['items']
            if items:
                # If a match is found, return the first track's URI
                return items[0]['uri']
            else:
                print(f"Warning: Could not find '{song_name} by {artist_name}' on Spotify.")
                return None
        except Exception as e:
            print(f"Error searching for track: {e}")
            return None