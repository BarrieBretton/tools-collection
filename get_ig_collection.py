import bs4
import os
import re
import requests
import unicodedata

def slugify(value, allow_unicode=False):
    """
    Taken from https://github.com/django/django/blob/master/django/utils/text.py
    Convert to ASCII if 'allow_unicode' is False. Convert spaces or repeated
    dashes to single dashes. Remove characters that aren't alphanumerics,
    underscores, or hyphens. Convert to lowercase. Also strip leading and
    trailing whitespace, dashes, and underscores.
    """
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize('NFKC', value)
    else:
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value.lower())
    return re.sub(r'[-\s]+', '-', value).strip('-_')

def download_collection_pics(pic_infos, dl_dir):
    if not os.path.isdir(dl_dir):
        try:
            os.mkdir(dl_dir)
        except OSError:
            print("Sorry, could not create the provided dir")
            return 1
    total = len(pic_infos)
    for ind, i in enumerate(pic_infos):
        pic_path = os.path.join(dl_dir, slugify(i[0])[:125]+'.jpg')
        with open(pic_path, 'wb') as fp:
            fp.write(requests.get(i[1]).content)
        print(f"Completed download of {ind+1}/{total} pictures")
    return 0


if __name__ == "__main__":
    dl_dir = input("dl dir? > ")
    path = input("html file path? > ")
    with open(path, encoding='utf-8') as fp:
        soup = bs4.BeautifulSoup(fp, 'html.parser')

    pic_divs = soup.find_all('div', {'class': '_aagv'})
    pic_infos = [(i.img['alt'], i.img['src']) for i in pic_divs]

    download_collection_pics(pic_infos, dl_dir)
