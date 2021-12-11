import time

import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy_config import my_id, my_secret, scope, pl_id


def check_playlist(sp):
    offset = 0
    song_id = None
    while True:
        response = sp.playlist_items(pl_id,
                                     offset=offset,
                                     fields='items.track.id,total',
                                     additional_types=['track'])

        if len(response['items']) == 0:
            break

        song_id = response['items'][0]["track"]["id"]
        offset = offset + len(response['items'])
    if song_id:
        return song_id
    else:
        return False


def get_song_name():
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=my_id, client_secret=my_secret,
                                                   redirect_uri="https://localhost:6543/callback/", scope=scope))

    song_idy = check_playlist(sp)
    if song_idy:
        song_info = sp.track(song_idy)
        artist_name = song_info["artists"][0]["name"]
        song_name = song_info["name"]
        sp.playlist_remove_specific_occurrences_of_items(pl_id, [{"uri": f"{song_idy}", "positions": [0]}])
        return f"{artist_name} {song_name}"
    else:
        return False

# results = sp.current_user_saved_tracks()
# print(results)
# while results['next']:
#     results = sp.next(results)
#     print(results)

# scope = "playlist-read-private"
# headers = {"Content-Type": "application/x-www-form-urlencoded"}
#
# authOptions = {
#     "client_id": my_id,
#     "response_type": "code",
#     "redirect_uri": "https://localhost:6543/callback/",
#     "scope": "playlist-read-private"
# }

#
#
# def get_current_profile_token(code):
#     auth_header2 = base64.b64encode(str(my_id + ":" + my_secret).encode("ascii"))
#
#     response = requests.post(
#       url='https://accounts.spotify.com/api/token',
#       data={
#         'grant_type': 'authorization_code',
#         'code': code,
#         'redirect_uri': 'https://example.com/callback',
#         'scope': "playlist-read-private",
#       },
#       headers={"Authorization": "Basic %s" % auth_header2.decode("ascii")},
#       verify=True
#     )
#
#     print(response.json())
#     return response.ok





# import spotipy
# from spotipy.oauth2 import SpotifyClientCredentials
# cid = 'c78bdc4d601a426196ab3cc163b544bc'
# secret = 'c000b89c18074c36903f3436b639e84b'
# client_credentials_manager = SpotifyClientCredentials(client_id=cid, client_secret=secret)
# token = client_credentials_manager.get_access_token()
# print(token)
# sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
# res = sp.artist("6XyY86QOPPrYVGvF9ch6wz")
# print(res)
