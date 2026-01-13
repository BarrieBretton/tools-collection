#Sound and Spotify imports
import psutil, subprocess, time

from pynput.keyboard import Key, Controller
from SwSpotify import spotify as Sp
from datetime import datetime as dt

#System imports - Tested for Windows Only
import os, sys
import time, ctypes
import subprocess as sp

os.chdir(os.path.dirname(__file__))

if sys.platform == 'win':
    SPOTIFY_PATH = os.path.join(os.environ['userprofile'], r'AppData\Roaming\Spotify\Spotify.exe')
elif sys.platform == 'linux':
    SPOTIFY_PATH = 'spotify'

try:
    from gtts import gTTS
    thanks_enable = True
except ImportError:
    thanks_enable = False
    pass

outFileName = 'spotify_history.log'
thanks_enable = True # set to true during production

if sys.platform == 'win':
    mainDir = 'C:\\Users\\Vivo Jay' # Set to wherever you want to save the log
elif sys.platform == 'linux':
    mainDir = '/home/vivojay' # Set to wherever you want to save the log

look_for = [
    "advertisement",
    "learn more",
    "apply now",
    "listen now",
    "made for mom",
    "SoundOn",
    "a consumer podcast",
    "a better way to get paid"
]

print('Starting Spotify Logging and Ad Restarter')
if thanks_enable:
    os.chdir(mainDir)
    if os.path.isfile('spotify-restarter__thanks.mp3'):
        os.remove('spotify-restarter__thanks.mp3')

    try:
        tts = gTTS(
                    'Thank you for using Spotify Restarter',
                    lang='en',
                    tld='us',
                    slow=False
                )
        tts.save('spotify-restarter__thanks.mp3')
        from playsound import playsound
        playsound('spotify-restarter__thanks.mp3')
    except Exception:
        thanks_enable = False

    if os.path.isfile('spotify-restarter__thanks.mp3'):
        os.remove('spotify-restarter__thanks.mp3')

if not thanks_enable:
    try:
        import winsound as ws
        ws.Beep(1000, 200); ws.Beep(500, 400)
    except ImportError:
        pass
    print("Started")


startupPath = os.path.join(os.path.expanduser('~'), 'AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup')

if sys.platform =='win':
    if os.path.split(__file__)[1] not in os.listdir(startupPath):
        sp.Popen([sys.executable, (os.path.join(os.path.split(__file__)[0], 'Implant and run.pyw'))], shell = True)

def restartSpot():
    for proc in psutil.process_iter():
        if proc.name() == 'Spotify.exe':
            try:
                proc.kill()
            except psutil.NoSuchProcess:
                print('[INFO]: Handled nonfatal glitch')

    while not 'Spotify.exe' in [i.name() for i in psutil.process_iter()]:
        subprocess.Popen('spotify.exe', shell=True)
        subprocess.Popen(SPOTIFY_PATH)

    while not 'Spotify.exe' in [i.name() for i in psutil.process_iter()]: pass

    time.sleep(0.3) # Delay before pressing play/pause button

    keyboard = Controller()
    keyboard.press(Key.media_play_pause)
    keyboard.release(Key.media_play_pause)

if not os.path.isfile(os.path.join(os.path.expanduser('~'), outFileName)):
    with open(os.path.join(os.path.join(os.path.expanduser('~'), outFileName)), 'w') as f:
        f.write('')

try:
    with open(os.path.join(os.path.join(os.path.expanduser('~'), outFileName))) as f:
        try:
            Lines = f.read().splitlines()
            Lines = [i for i in Lines if i.strip() != '']
            lastPlayedSong = Lines[-1]
            lastPlayedSong = tuple(' '.join(lastPlayedSong.split()[:-1]).split(' ~ '))
        except IndexError:
            lastPlayedSong = ''
            #raise
except Exception:
    lastPlayedSong = ''
    #raise

curSong = lastPlayedSong
#print(curSong) #Comment this line
paused = False

ptime = time.time()
playTime = 0.0
TotalPlayTime = 0.0

# Infinite Loop to detect Spot Ads
while True:
    try:
        if Sp.current() != curSong:
            #print(1)
            info = ' ~ '.join(Sp.current())+' '+'_'.join(str(dt.now()).split())
            if Sp.current()[-1] != '':
                with open(os.path.join(os.path.expanduser('~'), outFileName), 'a', encoding='utf8') as f:
                    f.write(info+'\n')
                print('Now Playing:', ' ~ '.join(Sp.current()))
            else:
                pass

        curSong = Sp.current()
        # print(curSong)

        if Sp.song().lower() in look_for or Sp.artist().strip() == '':
            restartSpot()

        if paused == True:
            print('⏵')
            #print(playTime)
            TotalPlayTime += playTime
            #print('  :', TotalPlayTime, sep = '')
            ptime = time.time()
            paused = False
        

    except Sp.SpotifyNotRunning:
        playTime = time.time()-ptime
        if not paused == True:
            print('⏸')
            paused = True

    except Exception:
        print("    Handled internal glitch")

    time.sleep(0.1)


'''
~Vivo Jay
Last Modified: 16 June 2021, 6:42 P.M.
Last Modified: 28 June 2021, 3:03 P.M.
'''
