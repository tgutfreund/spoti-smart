import streamlit as st
import sys
import os

# Add src to path so we can import our modules
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from spotify_client import SpotifyClient
from llm_client import GeminiClient

# Page configuration
st.set_page_config(
    page_title="🎵 SpotiSmart - AI Playlist Generator",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 2rem;
        background: linear-gradient(90deg, #1DB954, #1ed760);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    
    .track-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #1DB954;
        margin: 0.5rem 0;
    }
    
    .success-message {
        background: linear-gradient(90deg, #00C851, #1DB954);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        font-weight: bold;
    }
    
    .sidebar .stSelectbox label {
        font-weight: bold;
        color: #1DB954;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'spotify_client' not in st.session_state:
    st.session_state.spotify_client = None
if 'user_profile' not in st.session_state:
    st.session_state.user_profile = None
if 'top_tracks' not in st.session_state:
    st.session_state.top_tracks = None
if 'generating_playlist' not in st.session_state:
    st.session_state.generating_playlist = False
if 'cancel_generation' not in st.session_state:
    st.session_state.cancel_generation = False
if 'pending_playlist' not in st.session_state:
    st.session_state.pending_playlist = None
if 'playlist_data' not in st.session_state:
    st.session_state.playlist_data = None

def authenticate_spotify():
    """Handle Spotify authentication"""
    try:
        client = SpotifyClient()
        sp = client.authenticate()
        if sp:
            st.session_state.spotify_client = client
            st.session_state.authenticated = True
            
            # Get user profile
            user = sp.current_user()
            st.session_state.user_profile = user
            
            return True
        return False
    except Exception as e:
        st.error(f"Authentication failed: {e}")
        return False

def get_user_top_tracks(limit=50):
    """Fetch user's top tracks"""
    if st.session_state.spotify_client:
        tracks = st.session_state.spotify_client.get_user_top_tracks(limit=limit)
        st.session_state.top_tracks = tracks
        return tracks
    return None

def show_playlist_approval():
    """Show the generated playlist for user approval"""
    if not st.session_state.playlist_data:
        return
    
    data = st.session_state.playlist_data
    
    st.markdown("## 🎧 Review Your Generated Playlist")
    
    # Show playlist info
    st.markdown(f"""
    <div style="background: #f0f8ff; padding: 1rem; border-radius: 8px; border-left: 4px solid #1DB954; margin: 1rem 0;">
        <h4>📝 {data['title']}</h4>
        <p><strong>Found:</strong> {len(data['found_tracks'])} out of {data['total_recommendations']} recommended tracks</p>
        <p><strong>Description:</strong> {data['description']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Show tracks in columns
    st.markdown("### 🎵 Tracks to be added:")
    cols = st.columns(2)
    for i, track in enumerate(data['found_tracks']):
        with cols[i % 2]:
            st.markdown(f"""
            <div class="track-card">
                <strong>♪ {track}</strong>
            </div>
            """, unsafe_allow_html=True)
    
    # Action buttons
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("✅ Create Playlist", type="primary", use_container_width=True):
            # Create the playlist
            with st.spinner("📝 Creating playlist on Spotify..."):
                playlist_id = st.session_state.spotify_client.create_playlist(
                    data['title'],
                    data['description']
                )
                
                if playlist_id:
                    st.session_state.spotify_client.add_tracks_to_playlist(playlist_id, data['track_uris'])
                    
                    # Clear pending playlist
                    st.session_state.pending_playlist = None
                    st.session_state.playlist_data = None
                    
                    # Success message
                    st.markdown(f"""
                    <div class="success-message">
                        🎉 Playlist "{data['title']}" created successfully on Spotify!
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Spotify link
                    spotify_playlist_url = f"https://open.spotify.com/playlist/{playlist_id}"
                    st.markdown(f"""
                    ### 🔗 [Open Playlist in Spotify]({spotify_playlist_url})
                    """)
                    
                    st.rerun()
                else:
                    st.error("Failed to create playlist on Spotify.")
    
    with col2:
        if st.button("🔄 Generate New", type="secondary", use_container_width=True):
            # Clear pending playlist and go back to generation
            st.session_state.pending_playlist = None
            st.session_state.playlist_data = None
            st.rerun()
    
    with col3:
        if st.button("❌ Cancel", use_container_width=True):
            # Clear pending playlist
            st.session_state.pending_playlist = None
            st.session_state.playlist_data = None
            st.rerun()

def generate_playlist_interface():
    """Interface for generating playlists"""
    st.markdown("## 🎵 Generate Your AI Playlist")
    
    # Show pending playlist approval if exists
    if st.session_state.pending_playlist:
        show_playlist_approval()
        return
    
    col1, col2 = st.columns([2, 1])
    
    # Input fields on left column
    with col1:
        playlist_title = st.text_input(
            "📝 Playlist Title",
            value="My AI Generated Playlist",
            help="Give your playlist a catchy name!"
        )
        
        mood_prompt = st.text_area(
            "🎭 Describe your mood or activity",
            value="Upbeat songs for a morning workout",
            height=100,
            help="Be specific! Example: 'Chill indie songs for studying' or 'High energy electronic music for running'"
        )
    
    # Input fields on right column
    with col2:
        num_inspiration_tracks = st.slider(
            "🎯 Number of inspiration tracks",
            min_value=10,
            max_value=50,
            value=50,
            help="How many of your top tracks should inspire the AI?"
        )
        
        playlist_length = st.selectbox(
            "⏱️ Playlist Length",
            options=[10, 15, 20, 25, 30, 35, 40, 45, 50],
            index=3,
            help="Number of songs to generate"
        )
    
    # Generate button
    if st.button("🚀 Generate AI Playlist", type="primary", use_container_width=True, disabled=st.session_state.generating_playlist):
        if not playlist_title.strip():
            st.error("Please enter a playlist title!")
            return
        
        if not mood_prompt.strip():
            st.error("Please describe your mood or activity!")
            return
        
        # Set generating state
        st.session_state.generating_playlist = True
        st.session_state.cancel_generation = False
        st.rerun()
    
    # Show cancel button and progress when generating
    if st.session_state.generating_playlist:
        # Cancel button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("❌ Cancel Generation", type="secondary", use_container_width=True):
                st.session_state.generating_playlist = False
                st.session_state.cancel_generation = True
                st.warning("🛑 Playlist generation cancelled!")
                st.rerun()
        
        # Show loading with progress
        with st.spinner("🤖 AI is analyzing your taste and generating playlist..."):
            progress_bar = st.progress(0)
            
            # Get inspiration tracks
            if not st.session_state.cancel_generation:
                progress_bar.progress(20)
                st.write("📊 Fetching your top tracks...")
                inspiration_tracks = get_user_top_tracks(num_inspiration_tracks)
                
                if not inspiration_tracks:
                    st.error("Could not fetch your top tracks. Please try again.")
                    st.session_state.generating_playlist = False
                    return
            
            # Generate with LLM
            if not st.session_state.cancel_generation:
                progress_bar.progress(50)
                st.write("🧠 AI is analyzing your music taste...")
                try:
                    gemini_client = GeminiClient()
                    recommendations = gemini_client.generate_playlist_songs(
                        mood_prompt, 
                        inspiration_tracks, 
                        playlist_length
                    )
                    
                    if not recommendations:
                        st.error("AI could not generate recommendations. Please try a different prompt.")
                        st.session_state.generating_playlist = False
                        return
                    
                except Exception as e:
                    st.error(f"Error generating recommendations: {e}")
                    st.session_state.generating_playlist = False
                    return
            
            # Search for tracks on Spotify
            if not st.session_state.cancel_generation:
                progress_bar.progress(70)
                st.write("🔍 Searching for tracks on Spotify...")
                track_uris = []
                found_tracks = []
                
                for i, recommendation in enumerate(recommendations):
                    # Check for cancellation during search
                    if st.session_state.cancel_generation:
                        break
                        
                    try:
                        if ' by ' in recommendation:
                            song_name, artist_name = recommendation.split(' by ', 1)
                            track_uri = st.session_state.spotify_client.search_for_track(
                                song_name.strip(), 
                                artist_name.strip()
                            )
                            if track_uri:
                                track_uris.append(track_uri)
                                found_tracks.append(recommendation)
                        
                        # Update progress
                        progress_bar.progress(70 + (i / len(recommendations)) * 30)
                        
                    except Exception as e:
                        continue
                
                progress_bar.progress(100)
                
                if not track_uris:
                    st.error("Could not find any of the recommended songs on Spotify.")
                    st.session_state.generating_playlist = False
                    return
                
                # Store playlist data for approval
                st.session_state.playlist_data = {
                    'title': playlist_title,
                    'description': f"{mood_prompt} - Generated by SpotiSmart AI",
                    'track_uris': track_uris,
                    'found_tracks': found_tracks,
                    'total_recommendations': len(recommendations)
                }
                st.session_state.pending_playlist = True
                st.session_state.generating_playlist = False
                st.rerun()
            
            # Handle cancellation
            if st.session_state.cancel_generation:
                st.session_state.generating_playlist = False
                st.session_state.cancel_generation = False

def main():
    """Main application"""
    # Header
    st.markdown('<h1 class="main-header">🎵 SpotiSmart</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #666;">AI-Powered Playlist Generation Tool</p>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        
        if not st.session_state.authenticated:
            st.markdown("#### 🔐 Authentication")
            if st.button("🎵 Connect to Spotify", type="primary", use_container_width=True):
                with st.spinner("Connecting to Spotify..."):
                    if authenticate_spotify():
                        st.success("✅ Connected to Spotify!")
                        st.rerun()
                    else:
                        st.error("❌ Connection failed")
        else:
            # User info
            if st.session_state.user_profile:
                st.markdown("#### 👤 Connected User")
                st.success(f"🎵 {st.session_state.user_profile.get('display_name', 'User')}")
                
                if st.button("🔄 Refresh Data", use_container_width=True):
                    st.session_state.top_tracks = None
                    st.rerun()
                
                if st.button("🚪 Disconnect", use_container_width=True):
                    st.session_state.authenticated = False
                    st.session_state.spotify_client = None
                    st.session_state.user_profile = None
                    st.session_state.top_tracks = None
                    st.rerun()
    
    # Main content
    if not st.session_state.authenticated:
        # Welcome screen
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("""
            ## Welcome to SpotiSmart!
            
            ### What can SpotiSmart do?
            - 🤖 **AI-Powered Recommendations**: Uses advanced AI to understand your music taste
            - 🎯 **Personalized Playlists**: Creates playlists tailored to your specific mood and activity
            - 🎵 **Spotify Integration**: Creates real playlists directly in your Spotify account
            
            ### How it works:
            1. **Connect** your Spotify account
            2. **Analyze** your music taste using your top tracks
            3. **Describe** your mood or activity
            4. **Generate** a personalized playlist with AI
            
            Ready to discover your perfect playlist? Connect to Spotify to get started! 👆
            """)
    
    else:
        # Main app interface
        generate_playlist_interface()

if __name__ == "__main__":
    main()