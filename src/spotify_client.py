"""
Spotify API Client for SpotiSmart

This module provides a wrapper around the Spotify Web API using spotipy.
Handles authentication, user data retrieval, playlist creation, and track searching.

Features:
- OAuth2 authentication with proper scopes
- User top tracks retrieval for AI inspiration
- Playlist creation and track addition
- Intelligent track searching with error handling

Dependencies:
- spotipy: Spotify Web API wrapper
- python-dotenv: Environment variable management

Environment Variables Required:
- SPOTIFY_CLIENT_ID: Spotify app client ID
- SPOTIFY_CLIENT_SECRET: Spotify app client secret
- SPOTIFY_REDIRECT_URI: OAuth redirect URI (usually http://localhost:8080)
"""

import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class SpotifyClient:
    """
    A client to interact with the Spotify Web API.

    This class handles:
    - OAuth2 authentication with proper scopes
    - User profile and listening data retrieval
    - Playlist creation and management
    - Track searching and URI resolution
    """

    def __init__(self):
        """
        Initialize the Spotify client with credentials from environment variables.

        Sets up OAuth configuration with required scopes for playlist management
        and user data access.
        """
        # Load Spotify app credentials from environment
        self.client_id = os.getenv("SPOTIFY_CLIENT_ID")
        self.client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
        self.redirect_uri = os.getenv("SPOTIFY_REDIRECT_URI")

        # Define required OAuth scopes for application functionality
        self.scope = [
            "user-top-read",
            "user-library-read",
            "playlist-modify-private",
            "playlist-modify-public",
            "user-read-recently-played",
        ]

        self.sp = None  # Will store authenticated Spotify client

    def authenticate(self):
        """
        Authenticate user with Spotify using OAuth2 flow.

        Creates an authenticated Spotify client using OAuth2 with PKCE.
        Handles token caching for seamless re-authentication.

        Returns:
            spotipy.Spotify: Authenticated Spotify client, or None if failed
        """
        try:
            # Set up OAuth2 authentication manager
            auth_manager = SpotifyOAuth(
                client_id=self.client_id,
                client_secret=self.client_secret,
                redirect_uri=self.redirect_uri,
                scope=self.scope,
                cache_path=".spotify_cache",
            )

            # Create authenticated Spotify client
            self.sp = spotipy.Spotify(auth_manager=auth_manager)

            # Verify authentication by getting user profile
            user = self.sp.current_user()
            print(f"Successfully authenticated as: {user['display_name']}")
            return self.sp
        except Exception as e:
            print(f"Authentication failed: {e}")
            return None

    def get_user_top_tracks(self, limit=10, time_range="medium_term"):
        """
        Get user's top tracks for AI inspiration.

        Retrieves the user's most listened-to tracks over a specified time range.
        This data is used to understand the user's music taste for AI recommendations.

        Args:
            limit (int): Maximum number of tracks to retrieve (default: 10, max: 50)
            time_range (str): Time period for top tracks:
                - 'short_term': ~4 weeks
                - 'medium_term': ~6 months (default)
                - 'long_term': calculated from several years

        Returns:
            list: List of track objects from Spotify API, or None if failed
        """
        if not self.sp:
            print("Client not authenticated. Please run authenticate() first.")
            return None
        try:
            results = self.sp.current_user_top_tracks(
                limit=limit, time_range=time_range
            )
            return results["items"]
        except Exception as e:
            print(f"Error fetching top tracks: {e}")
            return None

    def create_playlist(self, name, description=""):
        """
        Create a new playlist for the current user.

        Creates a public playlist in the user's Spotify account with the specified
        name and description.

        Args:
            name (str): Playlist name
            description (str): Playlist description (optional)

        Returns:
            str: Playlist ID if successful, None if failed
        """
        if not self.sp:
            print("Client not authenticated.")
            return None
        try:
            user_id = self.sp.current_user()["id"]
            playlist = self.sp.user_playlist_create(
                user=user_id,
                name=name,
                public=False,  # Set to True if you want public playlists
                description=description,
            )
            print(f"Successfully created playlist: '{name}'")
            return playlist["id"]
        except Exception as e:
            print(f"Error creating playlist: {e}")
            return None

    def add_tracks_to_playlist(self, playlist_id, track_uris):
        """
        Add tracks to an existing playlist.

        Adds a list of tracks (specified by their Spotify URIs) to the given playlist.
        Handles batch addition and provides error handling.

        Args:
            playlist_id (str): Spotify playlist ID
            track_uris (list): List of Spotify track URIs to add

        Returns:
            None
        """
        if not self.sp or not track_uris:
            print("Client not authenticated or no tracks to add.")
            return
        try:
            # Add all tracks in a single batch operation
            self.sp.playlist_add_items(playlist_id, track_uris)
            print(f"Successfully added {len(track_uris)} tracks to the playlist.")
        except Exception as e:
            print(f"Error adding tracks: {e}")

    def search_for_track(self, song_name, artist_name):
        """
        Search for a track on Spotify and return its URI.

        Performs an intelligent search combining song name and artist name
        to find the best match on Spotify.

        Args:
            song_name (str): Name of the song
            artist_name (str): Name of the artist

        Returns:
            str: Spotify track URI if found, None if not found
        """
        if not self.sp:
            return None
        try:
            # Construct search query with track and artist fields
            query = f"track:{song_name} artist:{artist_name}"
            results = self.sp.search(q=query, type="track", limit=1)

            items = results["tracks"]["items"]
            if items:
                # Return the URI of the first (best) match
                return items[0]["uri"]
            else:
                print(
                    f"Warning: Could not find '{song_name} by {artist_name}' on Spotify."
                )
                return None
        except Exception as e:
            print(f"Error searching for track: {e}")
            return None
