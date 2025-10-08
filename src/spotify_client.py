import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class SpotifyClient:
    def __init__(self):
        self.client_id = os.getenv('SPOTIFY_CLIENT_ID')
        self.client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
        self.redirect_uri = os.getenv('SPOTIFY_REDIRECT_URI')
        
        # Define what permissions we need
        self.scope = [
            "user-top-read",
            "user-library-read", 
            "playlist-modify-private",
            "playlist-modify-public"
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
            
            # Test the connection
            user = self.sp.current_user()
            print(f"Successfully authenticated as: {user['display_name']}")
            return self.sp
            
        except Exception as e:
            print(f"Authentication failed: {e}")
            return None
    
    def get_user_top_tracks(self, limit=50, time_range='medium_term'):
        """Get user's top tracks"""
        # Ensure the client is authenticated
        try:
            self.sp.current_user()
        except spotipy.SpotifyException:
            print("Token expired or invalid. Please re-authenticate.")
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
  
# Test the client
if __name__ == "__main__":
    client = SpotifyClient()
    sp = client.authenticate()
    if sp:
        tracks = client.get_user_top_tracks(limit=10)
        if tracks:
            print(f"\n🎵 Your top tracks:")
            for i, track in enumerate(tracks, 1):
                print(f"{i}. {track['artists'][0]['name']} - {track['name']}")