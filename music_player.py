import socket
import json
import os

import spotipy
from dotenv import load_dotenv

HOST = "127.0.0.1"  # Server's hostname or IP address
PORT = 65432        # Port used by the server

load_dotenv()

redirect_uri = f"http://{HOST}:{PORT}/"
client_id = os.getenv('CLIENT_ID')
client_secret = os.getenv('CLIENT_SECRET')
scope = "user-read-playback-state,user-modify-playback-state"


def main():
    # Checks if client_id, client_secret, scope, and redirect_uri are valid
    oauth_object = spotipy.SpotifyOAuth(client_id, client_secret, redirect_uri, scope=scope) 

    # Gets proof of Authentication
    token_dict = oauth_object.get_access_token() 
    token = token_dict['access_token'] 

    sp= spotipy.Spotify(auth=token) 

    # Creating a socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
        client.connect((HOST, PORT))
        print("Connected to the server. Listening for state updates...")

        prev_is_music_playing = None  # Track the previous state

        while True:
            try:
                data = client.recv(1024)
                if not data:   
                    print("Connection closed by the server.")
                    break

                # Decode and parse the state message
                state = json.loads(data.decode())
                is_music_playing = state.get("is_music_playing", False)


                if is_music_playing != prev_is_music_playing:
                    print(f"Is music playing: {is_music_playing}")

                    if prev_is_music_playing is None:
                        sp.start_playback(uris=['spotify:track:0Y95PywucDqkFYWl4cwvwM'])
                    elif prev_is_music_playing:
                        sp.pause_playback()
                    else:
                        sp.start_playback()

                    prev_is_music_playing = is_music_playing
                    

            except json.JSONDecodeError:
                print("Received invalid data.")
            except ConnectionResetError:
                sp.pause_playback()
                print("Connection reset by the server.")
                break
                
                
if __name__ == "__main__":
    main()
