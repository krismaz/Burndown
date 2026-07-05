from email.mime import application
import json
import os
import requests

from helpers import stale


# https://trakt.tv/pin/217672
class trakt:
    def __init__(self, credentials):
        self.download_dir = os.path.join(os.getcwd(), "data", "trakt_downloads")
        self.data_dir = os.path.join(os.getcwd(), "data", "trakt_data")

        self.source = "trakt"
        self.credentials = credentials
        self.headers = {'Content-Type': 'application/json', 'trakt-api-version': '2', 'Accept': 'application/json', 'User-Agent': 'Burndown/0.0.1', 'trakt-api-key': self.credentials[0]}

    def authenticate(self):
        data = {
            'code': self.credentials[2],
            'redirect_uri': 'urn:ietf:wg:oauth:2.0:oob',
            'grant_type': 'authorization_code',
            'client_id': self.credentials[0],
            'client_secret': self.credentials[1],
        }
        response = requests.post('https://api.trakt.tv/oauth/token', json=data, headers=self.headers)
        if response.status_code == 200:
            token_data = response.json()
            return token_data['access_token']
        else:
            raise Exception(f"Failed to authenticate with Trakt API: {response.status_code} - {response.text}")
        

    def download(self):
        os.makedirs(self.download_dir, exist_ok=True)
        os.makedirs(self.data_dir, exist_ok=True)

        if not os.path.exists(os.path.join(self.data_dir, "token.json")):
            token = self.authenticate()
            with open(os.path.join(self.data_dir, "token.json"), "w") as f:
                f.write(token)
        else:
            with open(os.path.join(self.data_dir, "token.json"), "r") as f:
                token = f.read()

        self.headers['Authorization'] = f'Bearer {token}'
        user = requests.get('https://api.trakt.tv/users/settings', headers=self.headers)
        print(user.json()["user"]["username"])
        buffer = []
        page = 1
        while True:
            shows = requests.get(f'https://api.trakt.tv/users/me/watchlist/shows?page={page}&extended=full&limit=250', headers=self.headers).json()
            if not shows:
                break
            buffer.extend(shows)
            page += 1

        page = 1

        while True:
            shows = requests.get(f'https://api.trakt.tv/users/me/watched/shows?page={page}&extended=full&limit=250', headers=self.headers).json()
            if not shows:
                break
            buffer.extend(shows)
            page += 1

        hidden = requests.get(f'https://api.trakt.tv/users/hidden/dropped?limit=250', headers=self.headers).json()

        with open(os.path.join(self.download_dir, "trakt.json"), "w", encoding="utf-8") as f:
            json.dump({"shows": buffer, "hidden": hidden}, f)

    def parse(self):
        files = os.listdir(self.download_dir)
        if not files:
            raise Exception("No files found in download directory")
        file_path = os.path.join(self.download_dir, files[0])

        items = []
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        shows = data["shows"]
        hidden = data["hidden"]
        hidden_ids = {show["show"]["ids"]["trakt"] for show in hidden}

        for show in shows:
            watched = show.get("plays", 0)
            show = show["show"]
            if show["ids"]["trakt"] in hidden_ids:
                continue
            runtime = show["runtime"]
            aired_episodes = show["aired_episodes"]
            slug = show["ids"]["slug"]
            if not runtime or not aired_episodes or not slug or watched >= aired_episodes:
                continue
            items.append(
                {
                    "name": show["title"],
                    "source": self.source,
                    "url": f"https://trakt.tv/shows/{slug}",
                    "type": "tvshow",
                    "length": max(0, float(runtime * (aired_episodes - watched) / 60.0)),
                }
            )

        return items

    def scrape(self):
        if True or stale(self.download_dir):
            self.download()
        return self.parse()
