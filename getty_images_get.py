import os
import requests
import bs4
import sys
import string

def get_pics_list(url):
    headers ={
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'
            }
    r = requests.get(url, headers=headers)
    soup = bs4.BeautifulSoup(r.content, "html.parser")
    return soup

def format_filename(s):
    """Take a string and return a valid filename constructed from the string.
Uses a whitelist approach: any characters not present in valid_chars are
removed. Also spaces are replaced with underscores.

Note: this method may produce invalid filenames such as ``, `.` or `..`
When I use this method I prepend a date string like '2009_01_15_19_46_32_'
and append a file extension like '.txt', so I avoid the potential of using
an invalid filename.

"""
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    filename = ''.join(c for c in s if c in valid_chars)
    filename = filename.replace(' ','_') # I don't like spaces in filenames.
    return filename

def main():
    url = "https://www.gettyimages.in/photos/mae-whitman"
    url = "https://www.gettyimages.in/photos/annie-mae"
    url = "https://www.gettyimages.in/search/2/image?family=editorial&phrase=hitler"
    return get_pics_list(url)

if __name__ == "__main__":
    a = main()
    b = a.find("div", {"data-testid": "gallery-items-container"})
    c = b.findAll("div")[0]

    caption = c.find("meta", {"itemprop": "caption"})["content"].rstrip("--")
    up_date = c.find("meta", {"itemprop": "uploadDate"})["content"]
    provider = c.find("meta", {"itemprop": "creditText"})["content"]
    getty_id = c.find("meta", {"itemprop": "contentUrl"})["content"].lstrip("https://media.gettyimages.com/id/").split('/')[0]

    getty_rel_link = c.find("a")["href"]
    getty_link = f'https://www.gettyimages.in{getty_rel_link}'
    getty_file_name = format_filename(f"{getty_id}__{up_date}_{provider}_{caption}")

    # Make another file with same specifics (id, name, date, etc..) corr to each pic and save caption in it as plaintext.


# Review and Assess daily Dhrumil and Mine Progress for GATE
# Asses resubmit (Including RDBMS)
# Send to self on telegram -> Higher sem PYQs
# ETE Study
# 

