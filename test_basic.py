"""
Unit tests for SpotiSmart application components
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add src to path
sys.path.append('src')

from spotify_client import SpotifyClient


class TestSpotifyClient(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        self.client = SpotifyClient()
    
    def test_initialization(self):
        """Test SpotifyClient initialization"""
        self.assertIsNotNone(self.client)
        self.assertIsNone(self.client.sp)  # Should be None until authenticated
    
    @patch('spotify_client.SpotifyOAuth')
    @patch('spotify_client.spotipy.Spotify')
    def test_authenticate_success(self, mock_spotify, mock_oauth):
        """Test successful authentication"""
        mock_sp = Mock()
        mock_spotify.return_value = mock_sp
        mock_sp.current_user.return_value = {'display_name': 'Test User'}
        
        result = self.client.authenticate()
        
        self.assertEqual(result, mock_sp)
        self.assertEqual(self.client.sp, mock_sp)
    
    @patch('spotify_client.SpotifyOAuth')
    def test_authenticate_failure(self, mock_oauth):
        """Test authentication failure handling"""
        mock_oauth.side_effect = Exception("Auth failed")
        
        result = self.client.authenticate()
        
        self.assertIsNone(result)
        self.assertIsNone(self.client.sp)
    
    def test_search_for_track_success(self):
        """Test successful track search"""
        self.client.sp = Mock()
        self.client.sp.search.return_value = {
            'tracks': {'items': [{'uri': 'spotify:track:abc123'}]}
        }
        
        result = self.client.search_for_track("Bohemian Rhapsody", "Queen")
        
        self.assertEqual(result, 'spotify:track:abc123')
        self.client.sp.search.assert_called_once_with(
            q="track:Bohemian Rhapsody artist:Queen",
            type="track",
            limit=1
        )
    
    def test_search_for_track_no_results(self):
        """Test track search with no results"""
        self.client.sp = Mock()
        self.client.sp.search.return_value = {'tracks': {'items': []}}
        
        result = self.client.search_for_track("Nonexistent Song", "Nobody")
        
        self.assertIsNone(result)
    
    def test_search_for_track_not_authenticated(self):
        """Test track search without authentication"""
        result = self.client.search_for_track("Test Song", "Test Artist")
        
        self.assertIsNone(result)
    
    def test_get_user_top_tracks_success(self):
        """Test retrieving user's top tracks"""
        self.client.sp = Mock()
        mock_tracks = {
            'items': [
                {'name': 'Song 1', 'artists': [{'name': 'Artist 1'}]},
                {'name': 'Song 2', 'artists': [{'name': 'Artist 2'}]}
            ]
        }
        self.client.sp.current_user_top_tracks.return_value = mock_tracks
        
        result = self.client.get_user_top_tracks(limit=2)
        
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['name'], 'Song 1')
        self.client.sp.current_user_top_tracks.assert_called_once_with(
            limit=2, time_range="medium_term"
        )
    
    def test_create_playlist_success(self):
        """Test playlist creation"""
        self.client.sp = Mock()
        self.client.sp.current_user.return_value = {'id': 'test_user'}
        self.client.sp.user_playlist_create.return_value = {'id': 'playlist_123'}
        
        result = self.client.create_playlist("My Test Playlist", "Test description")
        
        self.assertEqual(result, 'playlist_123')
        self.client.sp.user_playlist_create.assert_called_once_with(
            user='test_user',
            name="My Test Playlist",
            public=False,
            description="Test description"
        )
    
    def test_add_tracks_to_playlist(self):
        """Test adding tracks to playlist"""
        self.client.sp = Mock()
        track_uris = ['spotify:track:1', 'spotify:track:2']
        
        self.client.add_tracks_to_playlist('playlist_123', track_uris)
        
        self.client.sp.playlist_add_items.assert_called_once_with('playlist_123', track_uris)


class TestGeminiClient(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        self.api_key_patch = patch.dict(os.environ, {'GEMINI_API_KEY': 'test_key'})
        self.api_key_patch.start()
    
    def tearDown(self):
        """Clean up after tests"""
        self.api_key_patch.stop()
    
    def test_initialization_with_api_key(self):
        """Test GeminiClient initialization with API key"""
        with patch('llm_client.genai') as mock_genai:
            from llm_client import GeminiClient
            
            client = GeminiClient()
            
            self.assertIsNotNone(client)
            mock_genai.configure.assert_called_once_with(api_key='test_key')
            mock_genai.GenerativeModel.assert_called_once_with('gemini-pro')
    
    def test_initialization_without_api_key(self):
        """Test GeminiClient initialization without API key"""
        self.api_key_patch.stop()
        
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ValueError) as context:
                from llm_client import GeminiClient
                GeminiClient()
            
            self.assertIn("GEMINI_API_KEY", str(context.exception))
        
        self.api_key_patch.start()
    
    def test_generate_playlist_songs_success(self):
        """Test successful playlist generation"""
        with patch('llm_client.genai') as mock_genai:
            from llm_client import GeminiClient
            
            # Mock the AI model and response
            mock_model = Mock()
            mock_genai.GenerativeModel.return_value = mock_model
            mock_response = Mock()
            mock_response.text = """1. Thunderstruck - AC/DC
2. Eye of the Tiger - Survivor
3. We Will Rock You - Queen
4. Pump It Up - Elvis Costello
5. Till I Collapse - Eminem"""
            mock_model.generate_content.return_value = mock_response
            
            client = GeminiClient()
            result = client.generate_playlist_songs("workout", 5)
            
            self.assertEqual(len(result), 5)
            self.assertEqual(result[0]['title'], 'Thunderstruck')
            self.assertEqual(result[0]['artist'], 'AC/DC')
            self.assertEqual(result[4]['title'], 'Till I Collapse')
            self.assertEqual(result[4]['artist'], 'Eminem')
    
    def test_generate_playlist_songs_with_top_tracks(self):
        """Test playlist generation using user's top tracks"""
        with patch('llm_client.genai') as mock_genai:
            from llm_client import GeminiClient
            
            mock_model = Mock()
            mock_genai.GenerativeModel.return_value = mock_model
            mock_response = Mock()
            mock_response.text = "1. Similar Song - Similar Artist"
            mock_model.generate_content.return_value = mock_response
            
            client = GeminiClient()
            top_tracks = [
                {'name': 'Favorite Song', 'artists': [{'name': 'Favorite Artist'}]}
            ]
            
            result = client.generate_playlist_songs("chill", 1, user_top_tracks=top_tracks)
            
            # Verify the prompt included top tracks info
            call_args = mock_model.generate_content.call_args[0][0]
            self.assertIn("Favorite Song by Favorite Artist", call_args)
            self.assertIn("chill", call_args)
            
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0]['title'], 'Similar Song')
    
    def test_generate_playlist_songs_api_error(self):
        """Test handling of API errors"""
        with patch('llm_client.genai') as mock_genai:
            from llm_client import GeminiClient
            
            mock_model = Mock()
            mock_genai.GenerativeModel.return_value = mock_model
            mock_model.generate_content.side_effect = Exception("API Error")
            
            client = GeminiClient()
            result = client.generate_playlist_songs("test", 3)
            
            self.assertEqual(result, [])
    
    def test_generate_playlist_songs_malformed_response(self):
        """Test handling of malformed AI response"""
        with patch('llm_client.genai') as mock_genai:
            from llm_client import GeminiClient
            
            mock_model = Mock()
            mock_genai.GenerativeModel.return_value = mock_model
            mock_response = Mock()
            mock_response.text = "This is not a proper song list format"
            mock_model.generate_content.return_value = mock_response
            
            client = GeminiClient()
            result = client.generate_playlist_songs("test", 3)
            
            self.assertEqual(result, [])


class TestAppIntegration(unittest.TestCase):
    """Integration tests for the main application"""
    
    def test_imports_work(self):
        """Test that all main components can be imported"""
        try:
            from src.spotify_client import SpotifyClient
            from src.llm_client import GeminiClient
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"Import failed: {e}")
    
    @patch.dict(os.environ, {
        'SPOTIFY_CLIENT_ID': 'test_id',
        'SPOTIFY_CLIENT_SECRET': 'test_secret',
        'SPOTIFY_REDIRECT_URI': 'http://localhost:8080',
        'GEMINI_API_KEY': 'test_key'
    })
    def test_clients_can_be_initialized_with_env_vars(self):
        """Test that clients initialize properly with environment variables"""
        try:
            from src.spotify_client import SpotifyClient
            with patch('llm_client.genai'):
                from src.llm_client import GeminiClient
                
                spotify_client = SpotifyClient()
                gemini_client = GeminiClient()
                
                self.assertIsNotNone(spotify_client)
                self.assertIsNotNone(gemini_client)
                self.assertEqual(spotify_client.client_id, 'test_id')
        except Exception as e:
            self.fail(f"Client initialization failed: {e}")


if __name__ == '__main__':
    # Run tests with more verbose output
    unittest.main(verbosity=2)