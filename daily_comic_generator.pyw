#from urllib.request import urlopen, urlretrieve
#from bs4 import BeautifulSoup
#import re

import random
import sys
import requests
from PIL import Image
from io import BytesIO

latest_comic = "https://xkcd.com/info.0.json"
latest_comic = requests.get(latest_comic)

if not latest_comic.ok:
    sys.exit("Could not fetch image")


def main():
    latest_comic_index = latest_comic.json().get('num')

    random_comic_index = random.randint(0, latest_comic_index)
    random_comic_url = f"https://xkcd.com/{random_comic_index}/info.0.json"
    random_comic = requests.get(random_comic_url)

    if not random_comic.ok:
        sys.exit("Could not fetch image")

    rand_comic_image_url = random_comic.json().get('img')
    response = requests.get(rand_comic_image_url)
    img = Image.open(BytesIO(response.content))
    img.show() #Show the comic on screen!

if __name__ == "__main__":
    main()

