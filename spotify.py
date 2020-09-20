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

    def parameters(self, acc, dance, instrument):
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
        if response.status_code == 400:
            raise ResponseException(response.status_code, message = response.text)
        response_json = response.json()
        return response_json["id"]

    def currentPlaylist(self, playlist_name):
        query = "https://api.spotify.com/v1/users/{}/playlists?offset=0&limit=50".format(self.user_id)
        response = requests.get(
            query,
            headers={
                "Authorization": "Bearer {}".format(self.token)
            }
        )
        result = response.json()

        if response.status_code == 400:
            raise ResponseException(response.status_code, message = response.text)

        for i in result["items"]:
            if i["name"] == playlist_name:
                return i["id"]

        print("Playlist Not Found!")
        return None

    def tracks(self, playlist_ID, playlist_id_new):
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
        self.addItems(ids[:-1], playlist_id_new)
        offset = 100
        while offset < result["total"]:
            response = requests.get(
                result["next"],
                headers={
                    "Authorization": "Bearer {}".format(self.token)
                }
            )
            result = response.json()
            if response.status_code == 400:
                raise ResponseException(response.status_code, message=response.text)
            ids = ""
            for i in result["items"]:
                ids += i["track"]["id"] + ","

            offset += 100
            self.addItems(ids[:-1], playlist_id_new)

    def addItems(self, ids, playlist_id_new):
        query = "https://api.spotify.com/v1/audio-features?ids={}".format(ids)
        response = requests.get(
            query,
            headers={
                "Authorization": "Bearer {}".format(self.token)
            }
        )
        result = response.json()
        if response.status_code == 400:
            raise ResponseException(response.status_code)
        uris = []
        for i in result["audio_features"]:
            if i["danceability"] >= self.danceability and i["acousticness"] >= self.accousticness and i["instrumentalness"] >= self.instrumentalness:
                uris.append(i["uri"])
        request_data = json.dumps(uris)
        query = "https://api.spotify.com/v1/playlists/{}/tracks".format(playlist_id_new)
        response = requests.post(
            query,
            data=request_data,
            headers={
                "Authorization": "Bearer {}".format(self.token)
            }
        )
        # check for valid response status
        if response.status_code == 400:
            raise ResponseException(response.status_code)



c = CreatePlaylist()
playlist_id_new = c.createPlaylist(input("New Playlist Name = "), input("PLaylist Description = "))
Playlist_ID = c.currentPlaylist(input("Playlist Name = "))
if Playlist_ID != None:
    c.parameters(float(input("accoustics 0 - 1.0 = ")), float(input("danceable 0 - 1.0 = ")), float(input("instrumental 0 - 1.0 = ")))
    c.tracks(Playlist_ID, playlist_id_new)
