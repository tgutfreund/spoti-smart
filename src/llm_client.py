import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

class GeminiClient:
    """A client to interact with the Google Gemini API."""
    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in .env file.")
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')

    def generate_playlist_songs(self, mood_prompt, tracks, num_songs=15):
        """
        Sends a curated prompt to the LLM to get a list of recommended songs.
        """
        # Format the track list so the LLM can easily read it
        track_list_str = '", "'.join([f"{track['name']} by {', '.join([a['name'] for a in track['artists']])}" for track in tracks])
        track_list_str = f'"{track_list_str}"'

        # This is the detailed prompt that instructs the LLM
        full_prompt = f"""
        You are a helpful and creative music assistant named SpotiSmart. Your task is to select songs to create a new playlist that perfectly matches their requested mood or activity based on a list of their top tracks tracks.

        Instructions:
        1. I will provide you with a list of tracks in the format "Song Name by Artist Name".
        2. I will also provide a user's request, for example, "a playlist for a rainy day" or "songs for a morning workout".
        3. You must carefully select {num_songs} songs that best fit the user's request. The songs do not necessarily need to be from the provided list, it is more important to match the mood and only get inspiration from the top tracks if relevant for the mood.
        4. Your response MUST be ONLY a comma-separated list of the exact song titles you have chosen ONLY! in the format - 'Song Name by Artist'. Do not add any introductory text, explanations, numbering, or quotation marks.
        5. Ensure that the songs you select are popular and widely recognized tracks that fit the mood or activity described in the user's request.
        6. Do not make up any song titles or artists. Only use real songs. Double check your work to ensure accuracy.
        7. Make sure that the song name and artist name are accurate, correctly spelled, and in the correct language, as they will be used to search for the songs on Spotify through the Spotify API, spotipy.

        User Request: "{mood_prompt}"
        User's Top Track List: {track_list_str}
        """
        
        try:
            print("Sending prompt to the LLM...")
            response = self.model.generate_content(full_prompt)
            # Clean up the response and split it into a list of song names
            song_names = [name.strip() for name in response.text.split(',')]
            return song_names
        except Exception as e:
            print(f"An error occurred with the LLM API: {e}")
            return []

