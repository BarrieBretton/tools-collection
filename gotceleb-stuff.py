# Gotceleb stuff
import os
import re
import bs4
import contextlib
import requests as req
os.chdir(r"D:\OneDrive - Suncity School\Pictures\@cache\gotceleb")

u = "https://www.gotceleb.com/category/mae-whitman/page"
urls = [f"{u}/{i}" for i in range(1, 5)]
page_soups = [bs4._soup(req.get(i).text) for i in urls]
pcount = len(page_soups)

p = '-([^-]*).[^.]*$'

for page_ind, page_soup in enumerate(page_soups):
    with contextlib.suppress(FileExistsError):
        os.mkdir(f"page_{page_ind+1}")
    print(f"Processing page: {page_ind + 1}/{pcount}")

    articles = page_soup.find_all('article')
    article_pages = [a.find('a')['href'] for a in articles]
    acount = len(article_pages)

    article_soups = []
    for api, ap in enumerate(article_pages):
        print(f"  Loading article: {api + 1}/{acount}")
        article_soup = bs4._soup(req.get(ap).text)

        with contextlib.suppress(FileExistsError):
            os.mkdir(f"page_{page_ind+1}/article_{api+1}")

        article_img_links = article_soup.find_all('dt') #, {'class': 'gallery-icon portrait'})
        img_links = [re.sub(p, '', i.a.img['src'])+'.jpg' for i in article_img_links]
        icount = len(img_links)

        for iind, ilink in enumerate(img_links):
            fext = img_links[0].split('.')[-1]
            with open(f"page_{page_ind+1}/article_{api+1}/img_{iind+1}.{fext}", 'wb') as fp:
                fp.write(req.get(ilink).content)
                print(f"    > Saved img: {iind + 1}/{icount}", end = '\r')

