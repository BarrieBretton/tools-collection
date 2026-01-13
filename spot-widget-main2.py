
#Note for later: try to allow modification of:
# current song and/or
# seek position and/or 
# Volume and/or 
# Next/Prev

# A Note about the versions
"""
===================================================
(v1.0)
ABSOULTELY REQUIRED:
    > Icon$
    > Dark Bg Color$
    > Equalizer#
    > Song name$
    > Artist name$
    > Display Seek Position [Dynamic]$
    > Song Cover$
    > Release Year [Possibly, exact date]#

===================================================
(v2.0)
Implemeneted features are marked with a dolla sign ($)

"settings.json" for toggleable settings/features

# Features:
    > Basic:
        - Artist Name
        - Song Name
        - Track Cover Image/Art
        - Playback Progress Display

    > Appearance:
        - Background Blur
        - Gradient Background
        - Toggleable Dynamic BgColor
            (Inherits Color theme of Current Track Cover Art)
        - TextColor = Complement of Current [So that it is clearly visible]

    > Performance:
        - Quicker Image Load [How ?]

    > New Features:
        - Double-Click/Play-Pause Button on window = play/pause
        - Volume Control
        - Like/Unlike
        - Open Spotify App
        - Play/Pause/Next/Prev
        - Playback Seek Position
        - Song/Album/Playlist On Repeat
        - Release Year/Date
        - Shows Playback Time

    > BTS:
        - Start only if OS == Windows, else show some nice error :D
        - Listening Habits from Scrobbled songs/artist [Get from both lastFM and Spotify...]
"""


# For Keepsake
def openSpotifyAppPowershellCommand(_shell = False): # Unhidden by default, can change later
    powershellCommand = r'start "shell:AppsFolder\$(Get-StartApps "Spotify" | select -ExpandProperty AppId)"'
    subprocess.call(powershellCommand, shell=_shell)













# IMPORTS

# Required [Misc.]
import platform
if platform.system().lower() != "windows":
    sys.exit('Sorry, this application is only supported on Windows platform')
import requests
import configparser as cfgp
import urllib.parse
import base64
import sys
import os

from matplotlib import colors
# import time

# Change directory to Work Directory
import subprocess
os.chdir(
    os.path.split(__file__)[0]
)

sys.path.insert(
    1,
    os.path.join(
        os.path.split(__file__)[0],
        'creds'
    )
)

# Imports from py files in directory
from url_encode import refresh_code
from dom_img_cols import get_dom_color as gdc

# [CLI Only] -- Remove Later
# from pprint import pprint

# GUI and Images
from PIL import *
from tkinter.ttk import Progressbar #, Style
from PIL import ImageTk, Image
from io import BytesIO

# import tkhtmlview
import tkinter as tk
import os
import json

# Spotify API
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials #To access authorised Spotify data

def encountered_error(error_type=1, error_msg=None):
    if error_type:
        print("FATAL ERROR:", error_msg)
        sys.exit((error_type, error_msg))
    else:
        print("error:", error_msg)

# Load settings from "settings.json"
with open('settings.json') as f:
    _allSettings = json.load(f)

# Load themes from json file
with open(_allSettings[0]['colorSchemeFile']) as f:
    _allThemes = json.load(f)



try:
    if bool(_allSettings[0]['classicColorSchemeOnly']):
        _curTheme = "Classic"
        curThemeInfo = [i for i in _allThemes if i['themeName'] == _curTheme][0]

    else:
        _curTheme = _allSettings[0]['colorScheme']
        curThemeInfo = [i for i in _allThemes if i['themeName'] == _curTheme]
        if not any(curThemeInfo):
            _curTheme = "Classic"
            curThemeInfo = [i for i in _allThemes if i['themeName'] == _curTheme][0]
            encountered_error(0, 'Invalid color scheme selected [Case Sensitive], defaulting to Classic color scheme')

        else:
            curThemeInfo = curThemeInfo[0]

except Exception:
    encountered_error(0, "Invalid value for \"classicColorSchemeOnly\" in settings file, defaulting to False")

try:
    reqGeometry = [int(i) for i in _allSettings[1]['windowDimensions'].split('x')]
except Exception:
    reqGeometry = [204, 350]
    encountered_error(0, "Invalid value for \"windowDimensions\" in settings file, defaulting to 204x350")



#------------Credentials------------#
# Load spotify api credentials
auth_data = cfgp.ConfigParser()
auth_data.read('.\creds\config.cfg')
#
client_id = auth_data['client_details']['client_id']
client_secret = auth_data['client_details']['client_secret']
#
raw_redirect_uri = auth_data['client_details']['raw_redirect_uri']
redirect_uri = urllib.parse.quote(raw_redirect_uri, safe = '')
#
client_info_to_encode = f'{client_id}:{client_secret}'
base64_encoded_client_info = base64.b64encode(client_info_to_encode.encode('ascii')).decode('ascii')
#
SPOTIFY_GET_CURRENT_TRACK_INFO = 'https://api.spotify.com/v1/me/player/currently-playing'
SPOTIFY_GET_PLAYBACK_INFO = 'https://api.spotify.com/v1/me/player'

# Refresh, select all 7 options and paste it below
# ACCESS_TOKEN = 'BQCyS6lt0x-O4dtN-62faRAlcBkPWIxnt7kywlRJgWA_p5m75Dt7OJSGrh8pHi9CNKiRN7E6L047m2vx0-HfwcpqLLLqotcf2BGN9j5JX58p0wkAgRv-tkDZ_VT8uvy9tRWg1g4Rqm_uKI0swoJ_U8XwiWD-5VZuRrvakx5jN_s8SNzlnKzE2kLnBA'

ACCESS_TOKEN = refresh_code()

client_credentials_manager = SpotifyClientCredentials(
    client_id = client_id,
    client_secret = client_secret
)

sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager) #spotify object to access API

# Extra Spacing to increase visibility and decrease chances of accidental screen-edge problems
rPadding = 15
bPadding = 40


def startOnBootProcedures():
    print('Working on it...')

startOnBoot = _allSettings[1]['windowDimensions']
if startOnBoot:
    startOnBootProcedures()

# Image dimensions
size = (_allSettings[1]['imageSize'], _allSettings[1]['imageSize'])


def lum(hexColor):
    R, G, B = colors.to_rgb(hexColor);
    lum = (0.2126*R + 0.7152*G + 0.0722*B)**(1/2)
    return (lum, lum >= 0.5) # Return Luminance and check if it is above 50%

if lum(curThemeInfo['themeScheme']['bgColor'])[1]: # Bg Lum is high
    adImgPath = 'resources/AdNoBgDark.png' # Add Dark Ad Img for better visibility
else: # Bg Lum is low
    adImgPath = 'resources/AdNoBgLight.png' # Add Light Ad Img for better visibility

def convertMillis(millis):
    seconds=(millis/1000)%60
    minutes=(millis/(1000*60))%60
    hours=(millis/(1000*60*60))%24
    return seconds, minutes, hours

def formatMillis(millis):
    con_sec, con_min, con_hour = convertMillis(int(millis))
    if round(con_hour) != 0:
        print("{0}:{1}:{2}".format(round(con_hour), round(con_min), round(con_sec)))
    else:
        print("{0}:{1}".format(round(con_min), round(con_sec)))

#####################################################
lastClickX = 0
lastClickY = 0

def SaveLastClickPos(event):
    global lastClickX, lastClickY
    lastClickX = event.x
    lastClickY = event.y

def Dragging(event):
    x, y = event.x - lastClickX + root.winfo_x(), event.y - lastClickY + root.winfo_y()
    root.geometry("+%s+%s" % (x , y))
#####################################################

def get_current_track(access_token):
    global response, json_resp

    print('[!] Current Track API called')

    try:
        response = requests.get(
            SPOTIFY_GET_CURRENT_TRACK_INFO,
            headers={
                "Authorization": f"Bearer {access_token}"
            }
        )

        # dt.datetime.now().strftime('%a, %d %b %Y; %H:%M:%S')

        json_resp = response.json()

        track_id = json_resp['item']['id']
        track_name = json_resp['item']['name']
        artists = [artist for artist in json_resp['item']['artists']]

        link = json_resp['item']['external_urls']['spotify']

        artist_names = ', '.join([artist['name'] for artist in artists])
        song_art = sp.track(track_id)['album']['images'][0]['url']

        current_track_info = {
            "id": track_id,
            "track_name": track_name,
            "artists": artist_names,
            "link": link,
            'song_art': song_art
        }

        return current_track_info

    except Exception:
        # raise
        return None

def get_current_progress(access_token):

    print('[!] Current Track Progress API called')

    try:
        global response
        response = requests.get(
                SPOTIFY_GET_PLAYBACK_INFO,
                headers={
                    "Authorization": f"Bearer {access_token}"
                }
            )    

        return response.json()['progress_ms']
    
    except Exception:
        return 0

songChangeFlag = False
adFlag = False
# print(get_current_track(ACCESS_TOKEN))

# Start App
def show():
    global disp_name, artist_names, panel, img, img_url, ACCESS_TOKEN, song_dur_ms, sp, songChangeFlag, curSong, song_progress, adFlag, size

    # Song change and ad detection
    try:
        if not get_current_track(ACCESS_TOKEN) is None:
            curSong = get_current_track(ACCESS_TOKEN)['track_name'] #For detecting song change
            song_dur_ms = sp.track(get_current_track(ACCESS_TOKEN)['id'])['duration_ms']
            adFlag = False
        else:
            adFlag = True
            # print('YAY')
            curSong = 'Advertisement'
            song_dur_ms = 100000 #Initialise to 10**5 milliseconds for Advertisements and stuff
            # print('AD on show')

    except Exception:
        raise

    # Appearance

    #Static header: Top Banner
    header_label = tk.Label(
        root,
        text = 'Spotify Mini Display',
        background=curThemeInfo['themeScheme']['bgColor'],
        foreground=curThemeInfo['themeScheme']['topBannerColor'],
        font = 'Calibri 10 italic'
    )
    
    header_label.grid(row=0, column=0)

    #Static header: "Now Playing" Banner
    now_playing_label = tk.Label(
        root,
        text = 'Now Playing',
        background=curThemeInfo['themeScheme']['bgColor'],
        foreground=curThemeInfo['themeScheme']['nowPlayingColor'],
        font = 'Helvetica 18 bold'
    )

    now_playing_label.grid(row=1, column=0)

    #Dynamic prog bar
    song_progress = Progressbar(
        root,
        orient = tk.HORIZONTAL,
        length = 100,
        mode = 'determinate'
    )

    song_progress.grid(
        row=5,
        column=0
    )

    # Image loading
    try:
        if not adFlag:
            img_url = get_current_track(ACCESS_TOKEN)['song_art']
            response = requests.get(img_url)
            img_data = response.content
            img = ImageTk.PhotoImage(Image.open(BytesIO(img_data)).resize(size, Image.ANTIALIAS))
            #Image loaded

            panel = tk.Label(
                root,
                image=img,
                background=curThemeInfo['themeScheme']['bgColor']
            )

            panel.grid(
                row=2,
                column=0
            )

            adFlag = False

            disp_name = tk.Label(root,
                text = get_current_track(ACCESS_TOKEN)['track_name'],
                background=curThemeInfo['themeScheme']['bgColor'],
                foreground=curThemeInfo['themeScheme']['trackTitleColor'],
                font='Calibri 10'
            )

            disp_name.grid(
                row=3,
                column=0
            )

            artist_names = tk.Label(
                root,
                text = get_current_track(ACCESS_TOKEN)['artists'],
                background=curThemeInfo['themeScheme']['bgColor'],
                foreground=curThemeInfo['themeScheme']['trackArtistColor'],
                font='Calibri 10 italic'
            )

            artist_names.grid(
                row=4,
                column=0
            )

        else:
            adFlag = True

            img = Image.open(adImgPath)
            img = img.resize(size)
            tkimage = ImageTk.PhotoImage(img)

            panel = tk.Label(root, image=tkimage, background=curThemeInfo['themeScheme']['bgColor'])
            panel.grid(row=2, column=0)

            disp_name = tk.Label(root, text = 'Advertisement', background=curThemeInfo['themeScheme']['bgColor'], foreground=curThemeInfo['themeScheme']['trackTitleColor'], font='Calibri 10')
            disp_name.grid(row=3, column=0)

            artist_names = tk.Label(root, text = 'Advertisement', background=curThemeInfo['themeScheme']['bgColor'], foreground=curThemeInfo['themeScheme']['trackArtistColor'], font='Calibri 10')
            artist_names.grid(row=4, column=0)
    
    except Exception:
        #Restart App
        root.destroy()
        subprocess.Popen(__file__, shell=True)


# Refresh App
def refresh():
    global disp_name, artist_names, panel, img, img_url, ACCESS_TOKEN, song_dur_ms, sp, songChangeFlag, curSong, song_progress, adFlag, size, tkimage

    # Check if song changed and/or ad is playing
    try:
        if not get_current_track(ACCESS_TOKEN) is None:
            if curSong != get_current_track(ACCESS_TOKEN)['track_name']:
                songChangeFlag = True
                curSong = get_current_track(ACCESS_TOKEN)['track_name']
        else:
            adFlag = True
            pass


    except Exception:
        # print(0)
        if get_current_track(ACCESS_TOKEN) is None:
            adFlag = True
        else:
            adFlag = False

    # print(adFlag)

    # print(
    #         adFlag,
    #         json.dumps(
    #                 get_current_track(ACCESS_TOKEN)['artists'],
    #                 indent=2
    #             ),

    #         json.dumps(
    #             get_current_track(ACCESS_TOKEN)['track_name'],
    #             indent=2
    #             )
    #     ) # Don't need this print statement, please comment later

    '''
    # Image URL from unsplash
    testImgURL = r'https://images.unsplash.com/photo-1621868225045-b6401dcea159?ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&ixlib=rb-1.2.1&auto=format&fit=crop&w=334&q=80'

    response = requests.get(testImgURL)
    img_data = response.content
    img = ImageTk.PhotoImage(Image.open(BytesIO(img_data)).resize(size, Image.ANTIALIAS))
    panel.config(image=img, background='red')

    print(5)
    '''

    # print(os.getcwd())

    # img = Image.open("resources/Kaitlyn Velez - FOMO.jpeg")
    # img_ = img.resize(size, Image.ANTIALIAS)
    # tkimage = ImageTk.PhotoImage(img_)
    # panel.config(image=tkimage, background=curThemeInfo['themeScheme']['bgColor'])

    # time.sleep(1)
    # os._exit(0)

    print(get_current_track(ACCESS_TOKEN))

    try:
        if not adFlag:
            # print(1)
            cur_prog_ms = get_current_progress(ACCESS_TOKEN)
            # print(formatMillis(cur_prog_ms))
            # print(cur_prog_ms/song_dur_ms*100)
            song_progress['value'] = cur_prog_ms/song_dur_ms*100 #Percentage completion => ratio*100

            song_dur_ms = sp.track(get_current_track(ACCESS_TOKEN)['id'])['duration_ms'] #Update song duration

            r'''
            img_url = get_current_track(ACCESS_TOKEN)['song_art']
            response = requests.get(img_url)
            img_data = response.content
            img = ImageTk.PhotoImage(Image.open(BytesIO(img_data)).resize(size, Image.ANTIALIAS))
            panel.config(image=img, background=curThemeInfo['themeScheme']['bgColor'])
            '''

            disp_name.config(text = get_current_track(ACCESS_TOKEN)['track_name'], background=curThemeInfo['themeScheme']['bgColor'], foreground=curThemeInfo['themeScheme']['trackTitleColor'])
            artist_names.config(text = get_current_track(ACCESS_TOKEN)['artists'], background=curThemeInfo['themeScheme']['bgColor'], foreground=curThemeInfo['themeScheme']['trackArtistColor'])
            
            adFlag = False

        else:
            # print('000')
            cur_prog_ms = 0

            img = Image.open(adImgPath)
            img = img.resize(size)
            tkimage = ImageTk.PhotoImage(img)

            panel.config(image=tkimage, background=curThemeInfo['themeScheme']['bgColor'])
            disp_name.config(text = 'Advertisement', background=curThemeInfo['themeScheme']['bgColor'], foreground=curThemeInfo['themeScheme']['trackTitleColor'])
            artist_names.config(text = 'Advertisement', background=curThemeInfo['themeScheme']['bgColor'], foreground=curThemeInfo['themeScheme']['trackArtistColor'])

            adFlag = False

    except Exception:
        pass

    # time.sleep(10)

    try:
        if songChangeFlag:
            print('Image refreshed')
            #This is to refresh the image
            if not adFlag:
                # print(1)
                cur_prog_ms = get_current_progress(ACCESS_TOKEN)
                # print(cur_prog_ms/song_dur_ms*100)
                song_progress['value'] = cur_prog_ms/song_dur_ms*100 #Percentage completion => ratio*100

                song_dur_ms = sp.track(get_current_track(ACCESS_TOKEN)['id'])['duration_ms'] #Update song duration

                img_url = get_current_track(ACCESS_TOKEN)['song_art']
                # theme_col = gdc(img_url) #TO DO
                # print(theme_col[0])

                response = requests.get(img_url)
                img_data = response.content
                img = ImageTk.PhotoImage(Image.open(BytesIO(img_data)).resize(size, Image.ANTIALIAS))
                panel.config(image=img, background=curThemeInfo['themeScheme']['bgColor'])

                disp_name.config(text = get_current_track(ACCESS_TOKEN)['track_name'], background=curThemeInfo['themeScheme']['bgColor'], foreground=curThemeInfo['themeScheme']['trackTitleColor'])
                artist_names.config(text = get_current_track(ACCESS_TOKEN)['artists'], background=curThemeInfo['themeScheme']['bgColor'], foreground=curThemeInfo['themeScheme']['trackArtistColor'])

                adFlag = False

            else:
                print(2)
                cur_prog_ms = 0

                img = Image.open('resources/Kaitlyn Velez - FOMO.jpeg')
                img = img.resize(size)
                tkimage = ImageTk.PhotoImage(img)

                panel.config(image=tkimage, background=curThemeInfo['themeScheme']['bgColor'])
                disp_name.config(text = 'Advertisement', background=curThemeInfo['themeScheme']['bgColor'], foreground=curThemeInfo['themeScheme']['trackTitleColor'])
                artist_names.config(text = 'Advertisement', background=curThemeInfo['themeScheme']['bgColor'], foreground=curThemeInfo['themeScheme']['trackArtistColor'])

                adFlag = False

            # print(get_current_track(ACCESS_TOKEN), adFlag) #Hide this

            songChangeFlag = False #Reset song change flag to False

        #disp_name.config(text = get_current_track(ACCESS_TOKEN)['track_name'], background=curThemeInfo['themeScheme']['bgColor'], foreground=curThemeInfo['themeScheme']['trackTitleColor'])
        #artist_names.config(text = get_current_track(ACCESS_TOKEN)['artists'], background=curThemeInfo['themeScheme']['bgColor'], foreground=curThemeInfo['themeScheme']['trackArtistColor'])

        ACCESS_TOKEN = refresh_code() #Very bad line of code! But, keeping it anyways

    except Exception:
        pass

    
    # time.sleep(10)

    root.after(100, refresh) #100 ms gap


#--------Making/running the window--------#
root = tk.Tk()


#----Window placement and sizing
windowWidth = root.winfo_reqwidth()
windowHeight = root.winfo_reqheight()
#print("Width",windowWidth,"Height",windowHeight)

# Gets both half the screen width/height and window width/height
positionRight = int(root.winfo_screenwidth() - reqGeometry[0] - rPadding) # Width
positionDown = int(root.winfo_screenheight() - reqGeometry[1] - bPadding) # Height

root.geometry('x'.join([str(i) for i in reqGeometry])+"+{}+{}".format(positionRight, positionDown))
# root.geometry('1400x620'+"+{}+{}".format(positionRight, positionDown))
# root.geometry('200x320')
# print((root.winfo_screenheight(), root.winfo_screenwidth()))
# root.geometry("+{}+{}".format(0, 0))

root.bind('<Button-1>', SaveLastClickPos)
root.bind('<B1-Motion>', Dragging)


#----Window Looks/Style
if _allSettings[0]['overrideOpacity']['allow']:
    # print(True)
    # print('overrideOpacity allow:', _allSettings[0]['overrideOpacity']['value']/100)
    root.attributes('-alpha', _allSettings[0]['overrideOpacity']['value']/100)
else:
    # print(False)
    # print('overrideOpacity allow:', curThemeInfo['themeScheme']['opacity']/100)
    root.attributes('-alpha', curThemeInfo['themeScheme']['opacity']/100)
root.attributes('-topmost', True)

# root.attributes('-toolwindow', True)
if bool(_allSettings[0]['classicColorSchemeOnly']):
    root.overrideredirect(True) # classic color scheme ALWAYS has "On Top"
else:
    root.overrideredirect(bool(_allSettings[0]['alwaysOnTop']))

root.resizable(1, 0)
root.configure(background=curThemeInfo['themeScheme']['bgColor'])
root.protocol("WM_DELETE_WINDOW", root.iconify)
root.title('Spotify Mini Display')

# root.wm_attributes("-transparentcolor", curThemeInfo['themeScheme']['bgColor'])

#----Win Icon
# root.iconbitmap('resources/play_icon.png')
img = tk.PhotoImage(file='resources/play_icon.png')
root.tk.call('wm', 'iconphoto', root._w, img)
# root.wm_state('normal')

#RUN

r'''
#Temporary block of code down here
root.destroy()
raise SystemExit
'''

#Things start here
show()
refresh()
root.mainloop()
