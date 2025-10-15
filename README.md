# 🎵 SpotiSmart - AI Playlist Generator

**AI-powered Spotify playlist generation using your music taste and mood descriptions.**

SpotiSmart combines the power of Google Gemini AI with Spotify's extensive music catalog to create personalized playlists that perfectly match your mood, activity, or vibe. Simply describe what you're feeling, and let AI curate the perfect soundtrack!

## ✨ Features

- 🤖 **AI-Powered Recommendations**: Uses Google Gemini to understand your music taste and generate contextual suggestions
- 🎯 **Personalized Playlists**: Analyzes your Spotify listening history for better recommendations
- 🔄 **Intelligent Retry Logic**: Automatically finds alternative songs when tracks aren't available
- 📱 **Dual Interface**: Both web app (Streamlit) and command-line interface
- 🎵 **Direct Spotify Integration**: Creates playlists directly in your Spotify account
- ⚡ **Real-time Progress**: Live updates with cancellation support
- 📋 **Playlist Preview**: Review and approve AI suggestions before creating

## 🚀 Quick Start

### Prerequisites

- **Python 3.9+** (required for Google Gemini AI)
- **Spotify Account** with Developer App
- **Google Gemini AI API Key**

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/tgutfreund/spoti-smart.git
   cd spoti-smart
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   
   Create a `.env` file in the project root:
   ```env
   # Spotify API Credentials
   SPOTIFY_CLIENT_ID=your_spotify_client_id
   SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
   SPOTIFY_REDIRECT_URI=http://localhost:8080
   
   # Google Gemini AI API Key
   GEMINI_API_KEY=your_gemini_api_key
   ```

### Getting API Keys

#### Spotify API Setup
1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Create a new app
3. Add `http://localhost:8080` to Redirect URIs
4. Copy your Client ID and Client Secret

#### Google Gemini AI Setup
1. Visit [Google AI Studio](https://aistudio.google.com/)
2. Create a new API key
3. Copy your API key

## 💻 Usage

### Web Interface (Recommended)

```bash
streamlit run app.py
```

Then open http://localhost:8501 in your browser.

**Web App Workflow:**
1. 🔐 Connect your Spotify account
2. 📝 Enter playlist title and describe your mood
3. ⚙️ Configure settings (playlist length, inspiration tracks)
4. 🤖 Let AI generate recommendations
5. 📋 Review and approve the playlist
6. 🎵 Create directly in your Spotify account

### Command Line Interface

```bash
python main.py create -t "Playlist Title" -p "Mood description" -n 25
```

**CLI Options:**
- `-t, --title`: Playlist title (required)
- `-p, --prompt`: Mood or activity description (required)
- `-n, --num_tracks`: Number of songs to generate (default: 40)

**CLI Examples:**
```bash
# Workout playlist
python main.py create -t "Gym Session" -p "High energy electronic and rock songs for intense workout" -n 30

# Study playlist
python main.py create -t "Focus Flow" -p "Calm instrumental and ambient music for deep concentration" -n 20

# Road trip playlist
python main.py create -t "Highway Vibes" -p "Upbeat classic rock and indie songs for a long drive" -n 50
```

## 🛠️ Development

### Project Structure

```
SpotiSmart/
├── app.py                 # Streamlit web interface
├── main.py               # CLI interface
├── requirements.txt      # Python dependencies
├── .env                  # Environment variables (create this)
├── .gitignore           # Git ignore rules
├── src/
│   ├── spotify_client.py    # Spotify API wrapper
│   └── llm_client.py        # Google Gemini AI client
└── README.md            # This file
```


### Code Quality

```bash
# Format code
black .

# Type checking
mypy src/

# Linting
pylint src/
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required | Example |
|----------|-------------|----------|---------|
| `SPOTIFY_CLIENT_ID` | Spotify app client ID | ✅ | `abc123...` |
| `SPOTIFY_CLIENT_SECRET` | Spotify app client secret | ✅ | `def456...` |
| `SPOTIFY_REDIRECT_URI` | OAuth redirect URI | ✅ | `http://localhost:8080` |
| `GEMINI_API_KEY` | Google Gemini AI API key | ✅ | `ghi789...` |

### Spotify OAuth Scopes

The application requires these Spotify permissions:
- `user-top-read` - Read your top tracks
- `user-library-read` - Read your saved tracks
- `playlist-modify-private` - Create/modify private playlists
- `playlist-modify-public` - Create/modify public playlists
- `user-read-recently-played` - Read recently played tracks

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Ensure tests pass (`python -m pytest`)
6. Commit changes (`git commit -m 'Add amazing feature'`)
7. Push to branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🐛 Troubleshooting

### Common Issues

**Authentication Failed**
- Verify Spotify app credentials in `.env`
- Check redirect URI matches Spotify app settings
- Ensure you're using the correct Spotify account

**AI Generation Failed**
- Verify Google Gemini API key is valid
- Check internet connection
- Try a more specific mood description

**No Songs Found**
- AI recommendations might be too obscure
- Try different mood descriptions
- Check if songs are available in your region

**Import Errors**
- Ensure virtual environment is activated
- Reinstall dependencies: `pip install -r requirements.txt`
- Check Python version (3.9+ required)

### Getting Help

- 📧 **Issues**: [GitHub Issues](https://github.com/tgutfreund/spoti-smart/issues)
- 📖 **Documentation**: Check function docstrings and comments
- 🔍 **Debugging**: Enable verbose logging in CLI mode

## 🙏 Acknowledgments

- **Spotify** for their comprehensive Web API
- **Google** for the powerful Gemini AI model
- **Streamlit** for the intuitive web framework
- **spotipy** for the excellent Spotify API wrapper

---

**Made for music lovers who want AI to understand their vibe** 🎵
