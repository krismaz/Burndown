import json
import time

from imdb import imdb
from tvtime import tvtime
from storygraph import storygraph
from anilist import anilist
from playnite import playnite

from secrets import IMDB_SECRET, TVTIME_SECRET, STORYGRAPH_SECRET, ANILIST_SECRET

scrapers = [imdb(IMDB_SECRET), tvtime(TVTIME_SECRET), storygraph(STORYGRAPH_SECRET), anilist(ANILIST_SECRET), playnite()]
items = []

for scraper in scrapers:
    print("Scraping %s..." % scraper.source)
    items += scraper.scrape()

print("Done! Here are the items we found:")
for item in items:
    print("- %s (%s, %s, %s hours)" %
          (item["name"], item["source"], item["url"], item["length"]))

with open("output.json", "w", encoding="utf-8") as f:
    json.dump(items, f)

with open("timestamps.json", "r+", encoding="utf-8") as f:
    timestamps = json.load(f)
    timestamps.append({"timestamp": int(time.time()), "total": sum(item["length"] for item in items)})
    f.seek(0)
    json.dump(timestamps, f)
    f.truncate()