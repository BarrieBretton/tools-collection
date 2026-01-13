import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import sys
import time
import pygame
# import winsound
import contextlib

from datetime import datetime as dt

pygame.mixer.init()

if sys.platform == "linux":
    alarm_sound_path = r'/media/vivojay/VIVOSANDISK/VIVAN/MUSIC/dl-songs/MarianaPlayer/alayna - Sugar [Official Audio].mp3'
elif sys.platform == "win32":
    alarm_sound_path = r'C:\Users\Vivo Jay\Music\MarianaPlayer\Chymes - Enemy.mp3'
description = ""

with contextlib.suppress(Exception):
    if not sys.argv[-1].isnumeric():
        alarm_sound_path = sys.argv[-1]

def print_help():
    help_text = """Usage: py alarm.py (HH [MM] [SS]) [alarm sound path] [alarm-description-text]"""
    sys.exit(help_text)

def set_alarm_music(sound=None):
    invalid_path = True
    if sound:
        if os.path.exists(sound):
            invalid_path = False

    if invalid_path:
        if sound:
            print(f'ERROR: Alarm sound is set to invalid path --> {sound}\nPlease reset the path... Aborting')
        else:
            print('ERROR: Alarm sound has not been set. Please set it and restart alarm... Aborting')
        return invalid_path

def ring(sound):
    print()
    print("Alarm Activated")
    print(f'Playing: {sound}')
    pygame.mixer.music.load(sound)
    pygame.mixer.music.play()

def set_alarm(timeobject, description, alarm_sound_path):
    if not all(i.isnumeric() for i in timeobject):
        print('ERROR: Alarm time object is INVALID. Please reset... Aborting')
        return

    timeobject = [int(i) for i in timeobject]
    
    if len(timeobject) > 3:
        print('ERROR: Alarm time object has more than 3 terms and is therefore INVALID. Please reset... Aborting')
        return

    if len(timeobject) == 0:
        print('ERROR: Alarm time object is EMPTY. Please reset... Aborting')
        return

    while len(timeobject) != 3:
        timeobject.append(0)

    if [dt.now().hour, dt.now().minute, dt.now().second] > timeobject:
        print('ERROR: Alarm time object has already passed. Please reset... Aborting')
        return

    if set_alarm_music(alarm_sound_path):
        return

    tdiff = dt(1900, 1, 1, *[int(i) for i in timeobj]) - dt(1900, 1, 1, dt.now().hour, dt.now().minute, dt.now().second)
    tdiff_string = time.strftime("%Hh %Mm %Ss", time.gmtime(tdiff.seconds))

    print(f'Alarm loaded for {str(timeobject[0]).zfill(2)}{timeobject[1]}{timeobject[2]} hours --> i.e.({dt.strftime(dt.strptime(":".join([str(i) for i in timeobject]), "%H:%M:%S"), "%I:%M:%S %p")})')
    print(f"Alarm goes off in: {tdiff_string} ")

    if description.strip(): print(f"Label: {description}")
    else: print("[NO LABEL]")
    
    print()

    skipped = False
    try:
        while [dt.now().hour, dt.now().minute] < timeobject[:2]: pass
    except KeyboardInterrupt:
        skipped = True
        print('Skipped Alarm')

    try:
        with contextlib.suppress(KeyboardInterrupt):
            while dt.now().second < timeobject[2]: pass
    except KeyboardInterrupt:
        if not skipped:
            print('Skipped Alarm')

    if not skipped:
        print(description)
        ring(alarm_sound_path)

    try:
        while pygame.mixer.music.get_busy(): pass
    except KeyboardInterrupt:
        if not skipped:
            print('Stopped Alarm')

if __name__ == "__main__":
    timeobj = [i for i in sys.argv[1:] if i.isnumeric()]

    if len(sys.argv) == 2 and sys.argv[1] in "-h --help".split():
        print_help()

    if os.path.isfile(sys.argv[-1]) and not sys.argv[-2].isnumeric():
        alarm_sound_path = sys.argv[-1]
        description = sys.argv[-2]

    elif os.path.isfile(sys.argv[-2]) and not sys.argv[-1].isnumeric():
        alarm_sound_path = sys.argv[-2]
        description = sys.argv[-1]

    elif os.path.isfile(sys.argv[-1]):
        alarm_sound_path = sys.argv[-1]

    elif not sys.argv[-1].isnumeric():
        description = sys.argv[-1]
    
    set_alarm(timeobject=timeobj,
              description=description,
              alarm_sound_path=alarm_sound_path)

