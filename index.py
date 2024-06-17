from flask import Flask, request, jsonify, render_template
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans

app = Flask(__name__)

# Load songs dataset
songs_data_path = r'song.csv FILE DIRECTORY'
mood_data_path = r'mood.csv FILE DIRECTORY'

try:
    songs_data = pd.read_csv(songs_data_path)
    mood_data = pd.read_csv(mood_data_path)
except FileNotFoundError as e:
    print(f"File not found: {e}")
except Exception as e:
    print(f"Error reading files: {e}")

# Assuming 'trackName' is the correct column name for song names
song_options = songs_data['name'].unique().tolist()

# Merge datasets based on a common identifier (e.g., song ID)
df_songs = pd.merge(songs_data, mood_data, left_on='id', right_on='id', how='left')

# K-means clustering to determine centroids for each emotion
features = ['danceability', 'acousticness', 'energy', 'instrumentalness', 'liveness', 'valence', 'loudness', 'speechiness', 'tempo']
emotions = df_songs['mood'].unique()

# Create a dictionary to hold the centroids
centroids = {}

for emotion in emotions:
    subset = df_songs[df_songs['mood'] == emotion][features]
    kmeans = KMeans(n_clusters=1, random_state=42).fit(subset)
    centroids[emotion] = kmeans.cluster_centers_[0]

# Route to render the index.html template with song options
@app.route('/')
def index():
    # Reload song options in case they were not loaded properly
    global song_options
    if not song_options:
        song_options = songs_data['name'].unique().tolist()
    
    return render_template('index.html', song_options=song_options)

# Route to predict mood based on selected song
@app.route('/predict_mood', methods=['POST'])
def predict_mood():
    selected_song = request.form['song']
    
    # Find corresponding song in df_songs
    selected_song_row = df_songs[df_songs['name'] == selected_song].iloc[0]
    
    # Calculate the distance from the song to each centroid
    song_vector = selected_song_row[features].values
    distances = {emotion: np.linalg.norm(song_vector - centroid) for emotion, centroid in centroids.items()}
    
    # Find the closest emotion
    predicted_mood = min(distances, key=distances.get)
    
    # Return the predicted mood as JSON
    return jsonify({'mood': predicted_mood})

if __name__ == '__main__':
    app.run(debug=True)
