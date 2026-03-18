import os
import time
from selenium import webdriver


def profile(download_dir):
    fp = webdriver.FirefoxOptions()
    fp.set_preference("browser.download.folderList", 2)
    if os.path.exists(download_dir):
        import shutil
        shutil.rmtree(download_dir)
    os.makedirs(download_dir)
    fp.set_preference("browser.download.dir", download_dir)
    fp.set_preference("browser.download.manager.showWhenStarting", False)
    fp.set_preference(
        "browser.helperApps.neverAsk.saveToDisk", "text/csv")
    return fp


def stale(download_dir):
    # If the download directory is empty, it's stale
    if not os.path.exists(download_dir):
        return True

    now = time.time()
    for filename in os.listdir(download_dir):
        file_path = os.path.join(download_dir, filename)
        if os.path.isfile(file_path):
            if now - os.path.getmtime(file_path) < 24 * 60 * 60:
                return False
    return True
