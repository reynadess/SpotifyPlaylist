import json
from secrets import spotify_user_id
from secrets import spotify_token
import requests
from exceptions import ResponseException


class CreatePlaylist:
    def __init__(self):
        self.user_id = spotify_user_id
        self.token = spotify_token
        self.accousticness = None
        self.danceability = None
        self.instrumentalness = None
        self.ids = None

    def parameters(self, acc = None, dance = None, instrument = None):
        self.accousticness = acc
        self.danceability = dance
        self.instrumentalness = instrument

    def createPlaylist(self, name, description):
        request_body = json.dumps({
            "name": name,
            "description": description,
            "public": True
        })

        query = "https://api.spotify.com/v1/users/{}/playlists".format(self.user_id)
        response = requests.post(
            query,
            data=request_body,
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer {}".format(self.token)
            }
        )

        response_json = response.json()
        return response_json["external_urls"]["spotify"]

    def currentPlaylist(self, playlist_name):
        query = "https://api.spotify.com/v1/users/{}/playlists?offset=0&limit=50".format(self.user_id)
        response = requests.get(
            query,
            headers={
                "Authorization": "Bearer {}".format(self.token)
            }
        )
        result = response.json()

        if response.status_code != 200:
            raise ResponseException(response.status_code, message = response.text)

        for i in result["items"]:
            if i["name"] == playlist_name:
                return i["id"]

    def tracks(self, playlist_ID):
        query = "https://api.spotify.com/v1/playlists/{}/tracks?offset=0&limit=100".format(playlist_ID)
        response = requests.get(
            query,
            headers={
                "Authorization": "Bearer {}".format(self.token)
            }
        )
        result = response.json()
        ids = ""
        for i in result["items"]:
            ids += i["track"]["id"] + ","
        self.addItems(ids[:-1])
        offset = 100
        while offset < result["total"]:
            response = requests.get(
                result["next"],
                headers={
                    "Authorization": "Bearer {}".format(self.token)
                }
            )
            result = response.json()
            for i in result["items"]:
                ids += i["track"]["id"] + ","

            offset += 100
            self.addItems(ids[:-1])

    def addItems(self, ids):
        query = "https://api.spotify.com/v1/audio-features?ids={}".format(ids)
        response = requests.get(
            query,
            headers={
                "Authorization": "Bearer {}".format(self.token)
            }
        )
        result = response.json()
        for i in result["audio_features"]:
            if i["danceability"] >= 0.65:
                print(i)



c = CreatePlaylist()
# link = c.createPlaylist(input("Playlist Name = "), input("PLaylist Description = "))
Playlist_ID = c.currentPlaylist("Reynadess' Music")
c.tracks(playlist_ID=Playlist_ID)