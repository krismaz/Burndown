import os
import time
import csv

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

from helpers import stale, profile

class storygraph:
    def __init__(self, credentials):
        self.credentials = credentials
        self.download_dir = os.path.join(os.getcwd(), "data", "storygraph_downloads")
        self.source = "storygraph"

    def download(self):
        driver = webdriver.Firefox(profile(self.download_dir))
        driver.get("https://app.thestorygraph.com/users/sign_in")
        driver.find_element(By.ID, "user_email").send_keys(self.credentials[0])
        driver.find_element(By.ID, "user_password").send_keys(self.credentials[1])
        driver.find_element(By.ID, "sign-in-btn").click()
        time.sleep(3)
        driver.find_element(By.LINK_TEXT, "To-Read Pile").click()
        last_height = -1
        while True:
            # Scroll down to bottom
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            # Wait to load page
            time.sleep(3)

            # Calculate new scroll height and compare with last scroll height
            new_height = driver.execute_script("return document.body.scrollHeight")

            if new_height == last_height:
                break
            last_height = new_height

        posts = driver.find_elements(By.CLASS_NAME, "book-pane-content")
        data = []
        for post in posts:
            name = post.find_element(By.CLASS_NAME, "book-title-author-and-series").find_element(By.TAG_NAME, "h3").find_element(By.TAG_NAME, "a").text
            if not name:
                continue
            pages = post.find_element(By.CLASS_NAME, "toggle-edition-info-link").text.split(" ")[0]
            url = post.find_element(By.CLASS_NAME, "book-title-author-and-series").find_element(By.TAG_NAME, "h3").find_element(By.TAG_NAME, "a").get_attribute("href")
            tags = post.find_element(By.CLASS_NAME, "book-pane-tag-section").find_elements(By.TAG_NAME, "span")
            data.append({
                "name": name,
                "pages": pages,
                "url": url,
                "tags": ",".join([tag.text for tag in tags])
            })
        with open(os.path.join(self.download_dir, "storygraph.csv"), "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["name", "pages", "url", "tags"])
            writer.writeheader()
            writer.writerows(data)

        # Done!
        driver.close()

    def parse(self):
        files = os.listdir(self.download_dir)
        if not files:
            raise Exception("No files found in download directory")
        file_path = os.path.join(self.download_dir, files[0])

        books = []
        with open(file_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                comic = "comic" in row["tags"].lower() or "graphic novel" in row["tags"].lower()
                try:
                    pages = float(row["pages"])
                except:
                    continue
                books.append({
                    "name": row["name"],
                    "source": self.source,
                    "url": row["url"],
                    "type": "comic" if comic else "book",
                    "length": float(row["pages"])/(100 if  comic else 33.3), # Assume about 3 hours poer 100 pages, so 33.3 pages per hour
                })
        
        return books

    def scrape(self):
        if stale(self.download_dir):
            self.download()
        return self.parse()