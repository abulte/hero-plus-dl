import time
import os
import shutil

from datetime import datetime
from pathlib import Path
import xml.etree.ElementTree as ET

import ffmpeg

from minicli import cli, run
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


@cli
def download(path=None):
    """
    Uses Selenium and Firefox to download media library from GoPro Hero Plus
    """
    dl_path = Path(path or f"{os.environ.get('HOME')}/Downloads")

    browser = webdriver.Firefox()

    login = os.environ["GP_USER"]
    password = os.environ["GP_PASSWORD"]

    browser.get("https://gopro.com/login")
    try:
        browser.find_element(By.NAME, "loginEmail").send_keys(login)
        browser.find_element(By.NAME, "loginPassword").send_keys(password)
        browser.find_element(By.ID, "gptest-login-btn").click()
    except NoSuchElementException:
        pass

    WebDriverWait(browser, 10).until(
        EC.presence_of_element_located(
            (By.CLASS_NAME, "grid-list-container")
        )
    )

    items = browser.find_elements(By.CSS_SELECTOR, ".grid-item-wrapper > a")
    urls = [i.get_attribute("href") for i in items]

    for u in urls:
        browser.get(u)
        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located(
                (By.CLASS_NAME, "kebab-button")
            )
        )

        title = browser.find_element(By.CLASS_NAME, "toolbar-filename").get_attribute('innerHTML').strip()
        v_path = dl_path / title
        if v_path.exists():
            print(f"Skipping {v_path}")
            continue

        print(f"Downloading {v_path}...")
        browser.find_element(By.CLASS_NAME, "kebab-button").click()
        dls = browser.find_elements(By.CLASS_NAME, "download-option")
        # videos
        if dls:
            for d in dls:
                txt = d.get_attribute('innerHTML')
                if "1080p" in txt:
                    d.click()
                    time.sleep(1)
        # photos, not handled
        else:
            print(f"[WARNING] {v_path} looks like a photo, won't download.")
 

@cli
def date_tree(path):
    """
    Convert a bunch of flat videos list to a YYYY-MM-DD folder tree, based
    on ffmpeg metadata.
    """
    path = Path(path)
    assert path.resolve()
    videos = list(path.glob("*.MP4")) + list(path.glob("*.mp4"))
    for video in videos:
        metadata = ffmpeg.probe(str(video)).get("format", {}).get("tags", {})
        creation_time = metadata.get("creation_time")
        if not creation_time:
            print(f"[ERROR] could not find metadata for {video}")
            continue
        creation_time = datetime.strptime(creation_time, "%Y-%m-%dT%H:%M:%S.%fZ")
        folder = creation_time.strftime("%Y-%m-%d")
        folder_path = path / folder
        folder_path.mkdir(parents=True, exist_ok=True)
        print(f"Moving {video.name} to {folder_path}...")
        shutil.move(video, folder_path / video.name)


if __name__ == "__main__":
    run()
