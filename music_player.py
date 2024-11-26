import socket
import json

HOST = "127.0.0.1"  # Server's hostname or IP address
PORT = 65432        # Port used by the server

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
        client.connect((HOST, PORT))
        print("Connected to the server. Listening for state updates...")

        while True:
            try:
                data = client.recv(1024)
                if not data:
                    print("Connection closed by the server.")
                    break

                # Decode and parse the state message
                state = json.loads(data.decode())
                is_music_playing = state.get("is_music_playing", False)
                print(f"Is music playing: {is_music_playing}")

            except json.JSONDecodeError:
                print("Received invalid data.")
            except ConnectionResetError:
                print("Connection reset by the server.")
                break

if __name__ == "__main__":
    main()
