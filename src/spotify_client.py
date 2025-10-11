import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from dotenv import load_dotenv
import requests

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
    
    def get_user_top_tracks(self, limit=10, time_range='short_term'):
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

    def get_audio_features(self, tracks):
        """
        Gets track data from ReccoBeats using the correct URL and ID format, with no API key.
        """
        print("Fetching track data from ReccoBeats...")
        all_features = []
        
        # This header is from the documentation examples
        headers = {
            'Accept': 'application/json'
        }
        
        for track in tracks:
            if not track or 'id' not in track:
                continue
            
            spotify_track_id = track['id']
            
            # --- ID conversion from the link you sent ---
            resource_id = f"spotify:track:{spotify_track_id}"
            
            # --- Corrected URL from the link you sent ---
            url = f"https://api.reccobeats.com/v1/track/:{resource_id}"
            
            try:
                # Making the request with NO API key.
                response = requests.request("GET", url, headers=headers)
                response.raise_for_status()
                
                track_data = response.json()
                # The audio features are nested inside the main track object
                if 'audio_features' in track_data:
                    all_features.append(track_data['audio_features'])
                else:
                     print(f"Warning: 'audio_features' key not found in response for track {spotify_track_id}")

            except requests.exceptions.HTTPError as http_err:
                print(f"HTTP error for track {spotify_track_id} (URL: {url}): {http_err}")
                continue 
            except Exception as err:
                print(f"An error occurred for track {spotify_track_id} (URL: {url}): {err}")
                continue

        print(f"Successfully processed {len(all_features)} tracks from ReccoBeats.")
        return all_features
    
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

            print("\n🔬 Fetching audio features for these tracks...")
            features = client.get_audio_features(tracks)
            
            if features:
                print(f"\n✅ Successfully received {len(features)} feature sets from ReccoBeats:")
                for i, feature_set in enumerate(features):
                    track_name = tracks[i]['name']
                    danceability = feature_set.get('danceability', 'N/A')
                    energy = feature_set.get('energy', 'N/A')
                    valence = feature_set.get('valence', 'N/A')
                    
                    print(f"\n--- Features for: {track_name} ---")
                    print(f"  Danceability: {danceability}")
                    print(f"  Energy:       {energy}")
                    print(f"  Valence (Positivity): {valence}")