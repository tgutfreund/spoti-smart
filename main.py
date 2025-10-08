#!/usr/bin/env python3
 
import argparse
import sys
from src.spotify_client import SpotifyClient

def main():
    # Set up argument parsing
    parser = argparse.ArgumentParser(description="SpotiSmart: Smart Playlist Generator")
    parser.add_argument('command', choices=['login', 'test', 'analyze'], 
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
