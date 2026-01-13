
import os
import bs4
import sys
import string
import requests
import contextlib

url = f"https://fancaps.net/movies/MovieImages.php?name=The_DUFF&movieid=1559&page="

def convert_to_valid_filename(fname):
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    return ' '.join(''.join(c for c in fname if c in valid_chars).split())

def load_page(url, page_number):
    while (True):
        try:
            r = requests.get(url+str(page_number))
            break
        except Exception:
            pass

    soup = bs4.BeautifulSoup(r.text, "html.parser")
    title = soup.title.text.strip()

    return {"soup": soup, "title": convert_to_valid_filename(title)}

def get_stills_at_page(soup, page=1, save_to_disk=False, dir_path=None, disp=False):
    c = soup.find("div", {"class", "clearfix"})
    a = [i.find('img') for i in c.find_next_sibling("div").find_all('div') if i.find('img') is not None]
    image_urls = [i['src'].replace('https://moviethumbs.fancaps.net', 'https://cdni.fancaps.net/file/fancaps-movieimages') for i in a]

    if save_to_disk and dir_path is not None:
        for ind, still in enumerate(image_urls):
    
            with contextlib.suppress(OSError):
                os.mkdir(os.path.join(base_dir_path, f"page_{page}"))

            with open(os.path.join(dir_path, f"page_{page}", os.path.split(still)[1]), 'wb') as fp:
                fp.write(requests.get(still).content)

            if disp:
                print(f"  > Processed item {ind+1}", end='\r')

    return image_urls

def get_all_stills(url, save_to_disk, disp=True, dir_path=None):
    imgs = []
    imgs_at_last_page = []
    i = 0

    while (True):
        i += 1

        if disp:
            print(f"Page {i}")

        soup = load_page(url, i)['soup']
        imgs_at_current_page = get_stills_at_page(soup=soup,
                                                  page=i,
                                                  save_to_disk=save_to_disk,
                                                  dir_path=dir_path,
                                                  disp=disp)

        if imgs_at_current_page == imgs_at_last_page: break

        imgs_at_last_page = imgs_at_current_page
        imgs.extend(imgs_at_current_page)

        if disp: print(f"Processed page {i}")
        print()

    return imgs

def save_all_stills(dir_path, url, page_limit=None, image_limit=None):
    global page, base_dir_path, stills

    page = load_page(url, 1)
    base_dir_path = os.path.join(dir_path, page['title'])

    if not os.path.isdir(dir_path):
        sys.exit(f"Directory {dir_path} does not exist, create it first")
    
    with contextlib.suppress(OSError):
        os.mkdir(base_dir_path)

    if not os.path.isdir(base_dir_path):
        sys.exit(f"Directory {base_dir_path} does not exist, create it first")

    stills = get_all_stills(url, save_to_disk=True, dir_path=base_dir_path)


"""
r = requests.get(url+str(page_number))
soup = bs4.BeautifulSoup(r.text, "html.parser")
    
c = soup.find("div", {"class", "clearfix"})
a = [i.find('img') for i in c.find_next_sibling("div").find_all('div') if i.find('img') is not None]
image_urls = [i['src'].replace('https://moviethumbs.fancaps.net', 'https://cdni.fancaps.net/file/fancaps-movieimages') for i in a]
"""




