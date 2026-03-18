#https://anilist.co/api/v2/oauth/authorize?client_id=37470&redirect_uri=https://anilist.co/api/v2/oauth/pin&response_type=code

import json
import os
import time
import csv
import requests
import shutil


from anilist_queries import *


from helpers import stale, profile

class anilist:
    def __init__(self, credentials):
        self.credentials = credentials
        self.download_dir = os.path.join(os.getcwd(), "data", "anilist_downloads")
        self.data_dir = os.path.join(os.getcwd(), "data", "anilist_data")
        self.source = "anilist"

    def authenticate(self):
        data = {
            "grant_type": "authorization_code",
            "client_id": "37470",
            "client_secret": "ev1hjV9GVjryEm2EGddltT6rUFFj3XAM8gfLBmx2",
            "redirect_uri": "https://anilist.co/api/v2/oauth/pin",
            "code": self.credentials[0],
        }
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        response = requests.post(
            "https://anilist.co/api/v2/oauth/token",
            json=data,
            headers=headers
        )
        response.raise_for_status()
        token_data = response.json()
        access_token = token_data["access_token"]
        return access_token

    def download(self):

        url = 'https://graphql.anilist.co'

        if os.path.exists(self.download_dir):
            shutil.rmtree(self.download_dir)
        os.makedirs(self.download_dir)
        os.makedirs(self.data_dir, exist_ok=True)

        if not os.path.exists(os.path.join(self.data_dir, "token.json")):
            token = self.authenticate()
            with open(os.path.join(self.data_dir, "token.json"), "w") as f:
                f.write(token)
        else:
            with open(os.path.join(self.data_dir, "token.json"), "r") as f:
                token = f.read()

        # Make the HTTP Api request
        headers = {
			'Authorization': 'Bearer ' + token,
			'Content-Type': 'application/json',
			'Accept': 'application/json',
		}
        response = requests.post(url, headers=headers, json={'query': user_query, 'variables': {}})
        print(response.json())

        user_id = response.json()["data"]["Viewer"]["id"]
        page = 1
    
        data = []
        while True:
            time.sleep(1)  # Be nice to the API
            response = requests.post(url, headers=headers, json={'query': media_query, 'variables': {"userId": user_id, "page": page}})
            resp_data = response.json()
            data.extend(resp_data["data"]["Page"]["mediaList"])
            if not resp_data["data"]["Page"]["pageInfo"]["hasNextPage"]:
                break
            page += 1
        
        with open(os.path.join(self.download_dir, "anilist.json"), "w") as f:       
            json.dump(data, f)

    def parse(self):
        files = os.listdir(self.download_dir)
        if not files:
            raise Exception("No files found in download directory")
        file_path = os.path.join(self.download_dir, files[0])

        media = []
        with open(file_path, "r", encoding="utf-8") as f:
            reader = json.load(f)
            for row in reader:
                manga = row["media"]["type"] == "MANGA"
                length = 0
                if not manga and row["media"]["episodes"] and row["media"]["duration"]: 
                    length = float(row["media"]["episodes"] * row["media"]["duration"])/60
                elif manga and row["media"]["volumes"]:
                    length = 1.5 * row["media"]["volumes"] # Assume about 3 hours poer 100 pages, so 33.3 pages per hour
                if not length:
                    continue
                
                media.append({
                    "name": row["media"]["title"]["romaji"],
                    "source": self.source,
                    "url": row["media"]["siteUrl"],
                    "type": "comic" if manga else "book",
                    "length": length,
                })
        
        return media

    def scrape(self):
        if stale(self.download_dir):
            self.download()
        return self.parse()