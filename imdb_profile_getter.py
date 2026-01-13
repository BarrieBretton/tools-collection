import os
import bs4
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

def get_actor_pics_by_id(actor_id, dl_folder, headers={'user-agent': 'my-app/0.0.1'}, disp=True, save_to_device=True):
    page = f"https://www.imdb.com/name/nm{actor_id}/mediaindex?page=1"
    pageResponse = requests.get(page).text
    soup = bs4.BeautifulSoup(pageResponse, "html.parser")
    max_page_count = int(soup.find('span', {'class': 'page_list'}).findAll('a')[-1].text)
    # soup.findAll('div', {'class': 'media_index_thumb_list'})[0].findAll('img')[0]

    global final_links # TODO: Rm this line
    final_links = []

    for page_no in range(1, max_page_count+1):
        if page != 1:
            page = f"https://www.imdb.com/name/nm{actor_id}/mediaindex?page={page_no}"
            pageResponse = requests.get(page).text
            soup = bs4.BeautifulSoup(pageResponse, "html.parser")

        img_links = soup.findAll('div', {'class': 'media_index_thumb_list'})[0].findAll('a')
        img_links_count = len(img_links)

        if disp: print(f"Page {page_no} of {max_page_count}")
        for index, img_link in enumerate(img_links):
            link = "https://www.imdb.com"+img_link['href']

            pageResponse = requests.get(link, headers=headers).text
            soup = bs4.BeautifulSoup(pageResponse, "html.parser")

            src_link = soup.findAll('img')[1]['src']
            alt_text = soup.findAll('img')[1]['alt']

            alt_count = [i[1] for i in final_links].count(alt_text)

            if disp:
                print(f"  {index+1} / {img_links_count}: {src_link}")
                print(f"  {alt_text} {'#'+str(alt_count+1) if alt_count!=0 else ''}\n")
            final_links.append((src_link, alt_text))

            if save_to_device:
                save_path = alt_text
                if alt_count != 0:
                    save_path += f"_{alt_count+1}"
                if save_image(src_link, save_path, dl_folder):
                    print(f" Could not save: {save_path} {'#'+str(alt_count+1) if alt_count!=0 else ''}: [{src_link}]")
                    return 1

    return list(set(final_links))

def save_image(img_link, image_title, dl_folder_path):
    raw_img_contents = requests.get(img_link).content
    file_path = os.path.join(dl_folder_path, slugify(image_title)) + '.jpg'

    try:
        with open(file_path, 'wb') as fp:
            fp.write(raw_img_contents)
    except Exception:
        raise
        return 1

    return 0

