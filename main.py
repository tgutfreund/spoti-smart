#!/usr/bin/env python3

 
import argparse
import sys
from src.spotify_client import SpotifyClient

def main():
    # Set up argument parsing
    parser = argparse.ArgumentParser(description="SpotiSmart: Smart Playlist Generator")
    parser.add_argument('command', choices=['login', 'test'], 
                       help='Command to execute')
    args = parser.parse_args()

    # Initialize Spotify client
    client = SpotifyClient()
    
    if args.command == 'login':
        sp = client.authenticate()
        if sp:
            print("✅ Login successful!")
        else:
            print("❌ Login failed.")
            sys.exit(1)

    elif args.command == 'test':
        sp = client.authenticate()
        if sp:
            print("✅ Authentication successful!")
            tracks = client.get_user_top_tracks(limit=10)
            if tracks:
                print(f"\n🎵 Your top tracks:")
                for i, track in enumerate(tracks, 1):
                    artists = ', '.join([artist['name'] for artist in track['artists']])
                    print(f"{i}. {track['name']} by {artists}")
            else:
                print("❌ Failed to fetch top tracks.")
        else:
            print("❌ Authentication failed.")
            sys.exit(1)

if __name__ == "__main__":
    main()
