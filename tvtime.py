import os
import time
import json
import requests

from helpers import profile, profile, stale
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains

class tvtime:
    def __init__(self, credentials):
        self.credentials = credentials
        self.download_dir = os.path.join(os.getcwd(), "data", "tvtime_downloads")
        self.source = "tvtime"

    def download(self):
        # Fucking flutter man
        driver = webdriver.Firefox(profile(self.download_dir))
        driver.get("https://app.tvtime.com/welcome")

        time.sleep(5)  # Wait for the page to load
        ActionChains(driver).send_keys(Keys.TAB*3).send_keys(Keys.RETURN).send_keys(Keys.TAB*6).send_keys(Keys.RETURN).perform()
        
        element = None
        while not element:
            try:
                element = driver.find_element(By.ID, "username")
            except:
                None
            time.sleep(1)
        
        element.send_keys(self.credentials[0])
        driver.find_element(By.CLASS_NAME, "submitBtn").send_keys(Keys.RETURN)

        element = None
        while not element:
            try:
                element = driver.find_element(By.ID, "current-password")
            except:
                None
            time.sleep(1)
        
        element.send_keys(self.credentials[1])
        driver.find_element(By.CLASS_NAME, "submitBtn").send_keys(Keys.RETURN)
        time.sleep(2)  # Wait for the login to complete

        test = driver.execute_script('return localStorage.getItem("flutter.jwtToken");').strip('"')
        # Dump the test variable as JSON to the download directory
        data = []
        while True:
            url = f"https://app.tvtime.com/sidecar?o_b64=aHR0cHM6Ly9hcGkyLnRvemVsYWJzLmNvbS92Mi91c2VyLzQ3OTU3Mzc&fields=shows.fields(id,runtime,name,watched_episode_count,aired_episode_count,status,is_up_to_date,is_archived,is_for_later).offset({len(data)}).limit(500)"
            get = requests.get(url, headers={"Authorization": f"Bearer {test}"})
            response = get.json()
            if not response["shows"]:
                break
            data.extend(response["shows"])
        with open(os.path.join(self.download_dir, "tvtime.json"), "w") as f:
            json.dump(data, f)

    def parse(self):
        files = os.listdir(self.download_dir)
        if not files:
            raise Exception("No files found in download directory")
        file_path = os.path.join(self.download_dir, files[0])

        movies = []
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            for row in data:
                if not row["is_up_to_date"] and not row["is_archived"]:
                    movies.append(
                        {
                            "name": row["name"],
                            "source": "tvtime",
                            "length": (row["aired_episode_count"] - row["watched_episode_count"]) * float(row["runtime"]) / 60.0,
                            "type": "tvshow",
                            "url": f"https://app.tvtime.com/series/{row['id']}"
                        }
                    )
        return movies

    def scrape(self):
        if stale(self.download_dir):
            self.download()
        return self.parse()
