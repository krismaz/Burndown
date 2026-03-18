import os
import time
import csv

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

from helpers import stale, profile


class imdb:
    def __init__(self, credentials):
        self.credentials = credentials
        self.download_dir = os.path.join(os.getcwd(), "data", "imdb_downloads")
        self.source = "imdb"

    def download(self):
        driver = webdriver.Firefox(profile(self.download_dir))
        driver.implicitly_wait(10)
        driver.get("https://www.imdb.com/")

        # Login
        driver.find_element(By.LINK_TEXT, "Sign in").click()
        driver.find_element(By.XPATH, "//button[@aria-label='Sign in to an existing account']").click()
        driver.find_element(By.LINK_TEXT, "Sign in with IMDb").click()
        driver.find_element(By.ID, "ap_email").send_keys(self.credentials[0])
        driver.find_element(By.ID, "ap_password").send_keys(self.credentials[1])
        driver.find_element(By.ID, "signInSubmit").click()

        # Export watchlist
        watchlist = None
        while not watchlist:
            # IMDB be hating
            try:
                watchlist = driver.find_element(
                    By.PARTIAL_LINK_TEXT, "Watchlist")
            except:
                time.sleep(1)

        watchlist.click()
        driver.find_element(
            By.XPATH, "//button[@aria-label='Export']").click()

        time.sleep(5)  # Wait for the export to be ready

        # Download the file
        driver.get("https://www.imdb.com/exports/?status=ready")
        driver.find_element(
            By.XPATH, "//button[starts-with(@aria-label, 'Start')]").click()

        # Done!
        driver.close()

    def parse(self):
        files = os.listdir(self.download_dir)
        if not files:
            raise Exception("No files found in download directory")
        file_path = os.path.join(self.download_dir, files[0])

        movies = []
        with open(file_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if "Title" in row and row["Runtime (mins)"]:
                    movies.append(
                        {
                            "name": row["Title"],
                            "source": "imdb",
                            "length": float(row["Runtime (mins)"]) / 60.0,
                            "type": "movie",
                            "url": row["URL"]
                        }
                    )
        return movies

    def scrape(self):
        if stale(self.download_dir):
            self.download()
        return self.parse()
