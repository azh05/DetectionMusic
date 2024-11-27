import socket
import json
import os

import spotipy
from dotenv import load_dotenv

from random import sample
import datetime

HOST = "127.0.0.1"  # Server's hostname or IP address
PORT = 65432        # Port used by the server

load_dotenv()

redirect_uri = f"http://{HOST}:{PORT}/"
client_id = os.getenv('CLIENT_ID')
client_secret = os.getenv('CLIENT_SECRET')
scope = "user-read-playback-state,user-modify-playback-state"

# 7464s7OIoUO0k23f1uxzLL
def extract_songs(sp, playlist_uri):
    """
    Exract song uris from a playlist uri
    """
    return [ obj['track']['uri'] 
            for obj in sp.playlist_tracks(playlist_uri)["items"] 
            if obj['track'] is not None ]

def music_controls(song_uri, is_music_playing, prev_is_music_playing, sp):
    """
    Play and pause music using playback. Returns value for prev_is_music_playing
    """

    # Check if the state of the "is_music_playing" has changed
    if is_music_playing != prev_is_music_playing:
        print(f"Is music playing: {is_music_playing}")

        if prev_is_music_playing is None:
            sp.start_playback(uris=[song_uri])
        elif prev_is_music_playing:
            sp.pause_playback()
        else:
            sp.start_playback()

        return is_music_playing
    
    # If the state hasn't changed, return the same prev_is_music_playing
    return prev_is_music_playing

def do_switch_song(is_music_playing, sp, last_switch: datetime.datetime) -> bool:  
    """
    Given the conditions, determine whether current song should be switched (True or False)
    """

    # If person is being detected, but music isn't playing
    # Then the song ended and we want choose next song and start_playback
    return (is_music_playing and sp.current_playback() and not sp.current_playback()['is_playing'] 
            and abs(last_switch - datetime.datetime.now()) > datetime.timedelta(seconds=1))

def pick_song(songs_list):
    return sample(songs_list, 1)[0] 

def main():
    # Checks if client_id, client_secret, scope, and redirect_uri are valid
    oauth_object = spotipy.SpotifyOAuth(client_id, client_secret, redirect_uri, scope=scope) 

    # Gets proof of Authentication
    token_dict = oauth_object.get_access_token() 
    token = token_dict['access_token'] 

    sp = spotipy.Spotify(auth=token) 

    playlist_uri = 'spotify:playlist:37i9dQZF1DZ06evO3HgYWR'

    songs_list = extract_songs(sp, playlist_uri)
    current_song_uri = pick_song(songs_list)

    # Last switch time to fix bug that song switches twice at the end of song  
    last_switch = datetime.datetime.now()

    # Creating a socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
        client.connect((HOST, PORT))
        print("Connected to the server. Listening for state updates...")

        prev_is_music_playing = None  # Track the previous state

        # While the cv window is open
        while True:
            try:
                data = client.recv(1024)
                if not data:   
                    print("Connection closed by the server.")
                    break

                # Decode and parse the state message
                state = json.loads(data.decode())
                is_music_playing = state.get("is_music_playing", False)
                
                prev_is_music_playing = music_controls(current_song_uri, is_music_playing, prev_is_music_playing, sp)

                if do_switch_song(is_music_playing, sp, last_switch):
                    current_song_uri = pick_song(songs_list=songs_list)
                    sp.start_playback(uris=[current_song_uri])

                    last_switch = datetime.datetime.now()
                    
            # Error with sending over information from server client
            except json.JSONDecodeError:
                print(f"Received invalid data: {data}")

            # Connection Closed
            except ConnectionResetError:
                sp.pause_playback()

                print("Connection reset by the server.")
                break
                
                
if __name__ == "__main__":
    main()
