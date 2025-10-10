import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import seaborn as sns
import os

class MusicAnalyzer:
    def __init__(self, spotify_client):
        self.spotify_client = spotify_client
        self.audio_features = None
        self.user_profile = None
    
    def get_audio_features(self, track_ids):
        """Fetch audio features for a list of track IDs"""
        for i in range(0, len(track_ids), 100):
            features = []
            batch = track_ids[i:i+100]
            batch_features = self.spotify_client.audio_features(batch)
            features.extend([f for f in batch_features if f is not None])
        self.audio_features = features
        print(features)

if __name__ == "__main__":
    # Example usage
    from spotify_client import SpotifyClient
    client = SpotifyClient()
    sp = client.authenticate()
    if sp:
        analyzer = MusicAnalyzer(sp)
        top_tracks = client.get_user_top_tracks(limit=50)
        track_ids = [track['id'] for track in top_tracks]
        analyzer.get_audio_features(track_ids)
        print(analyzer.audio_features)
