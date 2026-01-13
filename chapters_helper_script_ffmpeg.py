"""
Need to create a file named chapters.txt and feed its path as arg1
Now, feed the path of media file as arg2
"""

import re
import os
import sys

def create_metadata(chapters_file, media_file):
    chapters = list()

    with open(chapters_file, 'r') as f:
       for line in f:
          x = re.match(r"(\d):(\d{2}):(\d{2}) (.*)", line)
          hrs = int(x.group(1))
          mins = int(x.group(2))
          secs = int(x.group(3))
          title = x.group(4)

          minutes = (hrs * 60) + mins
          seconds = secs + (minutes * 60)
          timestamp = (seconds * 1000)
          chap = {
             "title": title,
             "startTime": timestamp
          }
          chapters.append(chap)

    text = ""

    for i in range(len(chapters)-1):
       chap = chapters[i]
       title = chap['title']
       start = chap['startTime']
       end = chapters[i+1]['startTime']-1
       text += f"""
    [CHAPTER]
    TIMEBASE=1/1000
    START={start}
    END={end}
    title={title}
    """

    FFMETADATAFILE_path = os.path.dirname(media_file)

    with open(FFMETADATAFILE_path, "a") as myfile:
        myfile.write(text)
        

if __name__ == "__main__":
    chapters_file = sys.argv[1]
    media_file = sys.argv[2]
    
    create_metadata(chapters_file, media_file)

