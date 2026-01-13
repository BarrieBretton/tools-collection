import os
import vlc
import sys
import time
import json
import rich
import random
import threading
import subprocess as sp
import file_securer_vivo_multi_proc as fsv

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"]="hide"
import pygame

from pathlib import Path

#Usage: python3 mae_magic.py ((-c | -a) [<num>] [<path>] | -h)

help_text = """[blue]Usage: [/blue][#34bdeb]python3[/#34bdeb] [yellow]mae_magic.py[/yellow] ( [red]( [/red]( [green]-c[/green] | [green]-a[/green] ) [<num>] [<path>] [red])[/red] | [green]-h[/green] )

[#34eb6e]-h[/#34eb6e]     Display this help and exit
[#34eb6e]-c[/#34eb6e]     Choose background track
[#34eb6e]-a[/#34eb6e]     No Confirm, auto start

If no args are passed, the last added track is selected

<num>  Select <num>th track
<path> Select images only from the provided dir path
"""

settings = [
        {
            "loc": {
                "linux": "/media/vivojay/VIVOSANDISK/VIVAN/personal/__past__/mae/",
                "win32": r"E:/VIVAN/personal/__past__",
                },
            "mus": {
                "linux": "/media/vivojay/VIVOSANDISK/VIVAN/MUSIC/dl-songs/MarianaPlayer/Kari Kimmel - Nothing Left To Lose.mp3",
                "win32": r"E:\VIVAN\MUSIC\dl-songs\MarianaPlayer\Kari Kimmel - Nothing Left To Lose.mp3",
                },
            "bpm": 134,
            "time_mul": 8,
            "init_delay": 0,
            "init_seek": 0,
            },
        {
            "loc": {
                "linux": "/media/vivojay/VIVOSANDISK/VIVAN/personal/__past__/mae/",
                "win32": r"E:/VIVAN/personal/__past__",
                },
            "mus": {
                "linux": "/home/vivojay/Music/MarianaPlayer/Stephen Sanchez - 'Until I Found You' (Piano Version).mp3",
                "win32": "",
                },
            "bpm": 63.5,
            "time_mul": 4,
            "init_delay": 0,
            "init_seek": 0,
            },
        {
            "loc": {
                "linux": "/media/vivojay/VIVOSANDISK/VIVAN/personal/__past__/mae/",
                "win32": r"E:/VIVAN/personal/__past__",
                },
            "mus": {
                "linux": "/home/vivojay/Music/MarianaPlayer/Carlie Hanson - Illusion (Official Music Video).mp3",
                "win32": "",
                },
            "bpm": 142,
            "time_mul": 8,
            "init_delay": 0.8,
            "init_seek": 0,
            },
        {
            "loc": {
                "linux": "/media/vivojay/VIVOSANDISK/VIVAN/personal/__past__/mae/",
                "win32": r"E:/VIVAN/personal/__past__",
                },
            "mus": {
                "linux": "/home/vivojay/Music/MarianaPlayer/Becky Hill - Remember (Acoustic _ Sped Up).mp3",
                "win32": "",
                },
            "bpm": 137,
            "time_mul": 8,
            "init_delay": 0.7,
            "init_seek": 0,
            },
        {
                "loc": {
                    "linux": "/media/vivojay/VIVOSANDISK/VIVAN/personal/__past__/mae/",
                    "win32": r"E:/VIVAN/personal/__past__",
                    },
                "mus": {
                    "linux": "/media/vivojay/DATA/FL Utils/Downloaded Songs/TEST/ONLY SONGS/Lolo Zouaï - Desert Rose (2018).wav",
                    "win32": r"D:\FL Utils\Downloaded Songs\Lolo Zouaï - Desert Rose (2018).wav",
                    },
                "bpm": 90,
                "time_mul": 8,
                "init_delay": 3.8,
                "init_seek": 0,
                },
        {
                "loc": {
                    "linux": "/media/vivojay/VIVOSANDISK/VIVAN/personal/__past__/mae/",
                    "win32": r"E:/VIVAN/personal/__past__",
                    },
                "mus": {
                    "linux": "/home/vivojay/Music/MarianaPlayer/Taylor Edwards - Hard Feelings (Official Video).mp3",
                    "win32": "",
                    },
                "bpm": 105,
                "time_mul": 8,

                #"init_delay": 9,
                #"init_delay": 4.25,
                "init_delay": 6.625,

                "init_seek": 0,
                },
        {
                "loc": {
                    "linux": "/media/vivojay/VIVOSANDISK/VIVAN/personal/__past__/mae/",
                    "win32": r"E:/VIVAN/personal/__past__",
                    },
                "mus": {
                    "linux": "/media/vivojay/VIVOSANDISK/VIVAN/MUSIC/dl-songs/MarianaPlayer/Ella Isaacson - Hard Lessons (Visualizer).mp3",
                    "win32": r"E:\VIVAN\MUSIC\dl-songs\MarianaPlayer\Ella Isaacson - Hard Lessons (Visualizer).mp3",
                    },
                "bpm": 149,
                "time_mul": 8,
                "init_delay": 1.9,
                "init_seek": 0,
                },
        {
                "loc": {
                    "linux": "/media/vivojay/VIVOSANDISK/VIVAN/personal/__past__/mae/",
                    "win32": r"E:/VIVAN/personal/__past__",
                    },
                "mus":{
                    "linux": "/home/vivojay/Music/MarianaPlayer/Julia Wolf – Get Off My [Official Music Video].mp3",
                    "win32": "",
                    },
                "bpm": 106,
                "time_mul": 4,
                "init_delay": 9.05660377358,
                "init_seek": 0,
                },
        {
                "loc": {
                    "linux": "/media/vivojay/VIVOSANDISK/VIVAN/personal/__past__/mae/",
                    "win32": r"E:/VIVAN/personal/__past__",
                    },
                "mus": {
                    "linux": "/media/vivojay/VIVOSANDISK/VIVAN/MUSIC/dl-songs/MarianaPlayer/Emily Burns - Is It Just Me (Lyrics).mp3",
                    "win32": r"E:\VIVAN\MUSIC\dl-songs\MarianaPlayer\Emily Burns - Is It Just Me (Lyrics).mp3",
                    },
                "bpm": 73,
                "time_mul": 8,
                "init_delay": 3.2,
                "init_seek": 0,
                },
        {
                "loc": {
                    "linux": "/media/vivojay/VIVOSANDISK/VIVAN/personal/__past__/mae/",
                    "win32": r"E:/VIVAN/personal/__past__",
                    },
                "mus": {
                    "linux": "/media/vivojay/VIVOSANDISK/VIVAN/MUSIC/dl-songs/MarianaPlayer/Emotional Oranges - Heal My Desires (Audio).mp3",
                    "win32": r"E:\VIVAN\MUSIC\dl-songs\MarianaPlayer\Emotional Oranges - Heal My Desires (Audio).mp3",
                    },
                "bpm": 114,
                "time_mul": 8,
                "init_delay": -0.1,
                "init_seek": 0,
                },
        {
                "loc": {
                    "linux": "/media/vivojay/VIVOSANDISK/VIVAN/personal/__past__/mae/",
                    "win32": r"E:/VIVAN/personal/__past__",
                    },
                "mus": {
                    "linux": "/media/vivojay/VIVOSANDISK/VIVAN/MUSIC/dl-songs/MarianaPlayer/Robinson - Don't Say (Lyrics).mp3",
                    "win32": r"E:\VIVAN\MUSIC\dl-songs\MarianaPlayer\Robinson - Don't Say (Lyrics).mp3",
                    },
                "bpm": 114,
                "time_mul": 8,
                "init_delay": -0.1,
                "init_seek": 0,
                },
        {
                "loc": {
                    "linux": "/media/vivojay/VIVOSANDISK/VIVAN/personal/__past__/mae/",
                    "win32": r"E:/VIVAN/personal/__past__",
                    },
                "mus": {
                    "linux": "/media/vivojay/Windows/Users/Vivo Jay/Music/MarianaPlayer/Chymes - Enemy.mp3",
                    "win32": r"C:\Users\Vivo Jay\Music\MarianaPlayer\Chymes - Enemy.mp3",
                    },
                "bpm": 127,
                "time_mul": 8,
                "init_delay": 0,
                "init_seek": 0,
                },
        {
                "loc": {
                    "linux": "/media/vivojay/VIVOSANDISK/VIVAN/personal/__past__/mae/",
                    "win32": r"E:/VIVAN/personal/__past__",
                    },
                "mus": {
                    "linux": "/media/vivojay/Windows/Users/Vivo Jay/Music/MarianaPlayer/Yeat - Shhhh [Official Audio].mp3",
                    "win32": r"C:\Users\Vivo Jay\Music\MarianaPlayer\Yeat - Shhhh [Official Audio].mp3",
                    },
                "bpm": 142,
                "time_mul": 8,
                "init_delay": 2,
                "init_seek": 0,
                },
        {
                "loc": {
                    "linux": "/media/vivojay/VIVOSANDISK/VIVAN/personal/__past__/mae/",
                    "win32": r"E:/VIVAN/personal/__past__",
                    },
                "mus": {
                    "linux": "/media/vivojay/Windows/Users/Vivo Jay/Music/MarianaPlayer/Heather Sommer - and if I'm being honest (Lyrics).mp3",
                    "win32": r"C:/Users/Vivo Jay/Music/MarianaPlayer/Heather Sommer - and if I'm being honest (Lyrics).mp3 ",
                    },
                "bpm": 118,
                "time_mul": 8,
                "init_delay": 4,
                "init_seek": 0,
                },
]

PWD = "maethebae"

def aborted():
    rich.print("[red]"+"\n"+"-"*21+"[/red]")
    rich.print("[red] \[[/red]x[red]][/red] [red]Program Aborted[/red]")
    rich.print("[red]"+"-"*21+"[/red]")
    os._exit(0)

def play_bgm(music_path):
    global settings

    pygame.mixer.init()
    pygame.mixer.music.load(music_path)
    pygame.mixer.music.play()

def play_gallery(shuffle, override_gallery_loc, override_choice, music_path):
    global choice, settings, mae_pics, j #, bpm, time_mul, delay

    # Wait until path exists
    while 1:
        if os.path.exists(mae_pics_loc) and os.path.exists(music_path):
            break
        else:
            try:
                print("Required data not found", end='\r')
            except KeyboardInterrupt:
                aborted()

    mae_pics = [] 
    for dirpath, subdirs, files in os.walk(mae_pics_loc):
        for x in files:
            if x.lower().endswith(tuple(i+".enc" for i in fsv.EXTS)):
                mae_pics.append(os.path.join(dirpath, x))

    if shuffle:
        random.shuffle(mae_pics)

    prev_time = time.time()
    st_time = time.time()

    cmd = f'ffprobe -i "{music_path.strip()}" -show_entries format=duration -v quiet -of csv="p=0"'

    with sp.Popen(cmd, stdout=sp.PIPE, stderr=None, shell=True) as process:
        song_len = process.communicate()[0].decode("utf-8")

    for j, i in enumerate(mae_pics):
        if j == 0:
            fsv.file_dec(mae_pics[0], PWD)
            print("  first <dec>")

        if time.time() >= st_time + float(song_len):
            fsv.file_enc(i, PWD)
            print("| last <enc> |")
            break

        try:
            i = i.rstrip('.enc')
            i = Path(os.path.join(mae_pics_loc, str(i)))
            print(j, i)
            sp.run(f"kitty +icat '{i}'", shell=1)

            fsv.file_enc(str(i), PWD)
            print("  this <enc>")

            if j != len(mae_pics) - 1:
                fsv.file_dec(str(mae_pics[j+1]), PWD)
                print("  next <dec>")

            while time.time() < prev_time + (60/bpm) * time_mul:
                if time.time() >= st_time + float(song_len): break

            prev_time = time.time()

        except KeyboardInterrupt:
            print(mae_pics[j])
            print(mae_pics[j+1])
            # Re-encrypt the next file before exiting
            fsv.file_enc(mae_pics[j+1], PWD)
            print("  safely exited and encrypted last dec file <exit>")

            # Exit
            rich.print("\n[bold blue]Bye :)[/bold blue]")
            break

    prev_time = time.time()
    st_time = time.time()

    pygame.mixer.music.stop()

def main(shuffle, override_gallery_loc, override_choice):
    global choice, settings, bpm, time_mul, delay, mae_pics_loc

    """
    v = choice
    if sys.platform in "win32".split():
        while v:
            if not settings[choice]['mus'][sys.platform]:
                choice += 1
                v -= 1
    """

    if override_gallery_loc is not None:
        mae_pics_loc = override_gallery_loc
    else:
        mae_pics_loc = settings[choice]["loc"][sys.platform]

    print("mpl:", mae_pics_loc)
    music_path = settings[choice]["mus"][sys.platform]
    bpm = settings[choice]["bpm"]
    time_mul = settings[choice]["time_mul"]
    delay = settings[choice]["init_delay"]

    rich.print(f"[bold yellow]Cued: [/bold yellow]{os.path.split(music_path)[1]}")

    if not no_conf:
        try:
            input('\nPress enter to continue: ')
        except KeyboardInterrupt:
            aborted()

    t1 = threading.Thread(target = play_bgm, args=(music_path,))
    t2 = threading.Thread(target = play_gallery, args=(shuffle, override_gallery_loc, override_choice, music_path))

    if delay < 0:
        # gallery first
        t2.start()

        time.sleep(abs(delay))

        # bgm later
        t1.start()

    else:
        # bgm first
        t1.start()

        st_time = time.time()
        delay = settings[choice]["init_delay"]

        while time.time() <= st_time + delay:
            # Precise look
            # remaining = round(st_time + delay - time.time(), 2)
            # print(f"Shows in: {remaiing}", end='\r')

            # Simple look
            remaining = round(st_time + delay - time.time())+1
            print(f"Shows in: {remaining}  ", end='\r')

        # gallery first
        t2.start()

    # wait until thread 1 is completely executed
    try:
        t1.join()
    except KeyboardInterrupt:
        print(mae_pics[j])
        print(mae_pics[j+1])
        # Re-encrypt the next file before exiting
        fsv.file_enc(mae_pics[j+1].rstrip('.enc'), PWD)
        print("  safely exited and encrypted last dec file <exit>")

        # Exit
        rich.print("\n[bold blue]Bye :)[/bold blue]")

    # wait until thread 2 is completely executed
    try:
        t2.join()
    except KeyboardInterrupt:
        print(mae_pics[j])
        print(mae_pics[j+1])
        # Re-encrypt the next file before exiting
        fsv.file_enc(mae_pics[j+1].rstrip('.enc'), PWD)
        print("  safely exited and encrypted last dec file <exit>")

        # Exit
        rich.print("\n[bold blue]Bye :)[/bold blue]")


if __name__ == "__main__":    
    #-- Enter your prefs here --#
    shuffle = True

    # You may override location here, or set to None to disable override
    override_gallery_loc = None
    if sys.argv[1:] == ['sfw']:
        override_gallery_loc = "/media/vivojay/VIVOSANDISK/VIVAN/personal/Old-Data/VJ IX/Game planes/"

    # You may set a choice to override sys argv choice
    # Or None to re-enable sys argv
    # override_choice = 1
    override_choice = None

    # You may override location here, or set to None to disable override
    # override_mus_loc = "whatever.wav"
    override_mus_loc = None

    argvs = sys.argv

    if '-h' in argvs:
        rich.print(help_text)
        os._exit(0)

    if override_choice is not None:
        choice = override_choice
    else:
        choice = 0
        no_conf = False
        args_valid = False

        if '-a' in argvs:
            no_conf = True
            rich.print("[bold yellow]No confirmation -->[/bold yellow]")
            argvs.remove('-a')

        if len(argvs) > 1:
            if '-c' in argvs and not no_conf:
                for i, j in enumerate(settings):
                    a = j["mus"].get(sys.platform)
                    if a:
                        rich.print(str(i+1)+"[yellow]: [/yellow]", os.path.split(a)[1])

                try:
                    choice = input("Enter choice: ")
                    args_valid = True
                except KeyboardInterrupt:
                    aborted()
                except ValueError:
                    print("Enter a choice blud, whatchu doin' fr?")

            if '-c' in argvs: argvs.remove('-c')

            if len(argvs) == 2:
                if argvs[1].isnumeric():
                    rich.print(f'[bold yellow]choice:[/bold yellow] sel {argvs[1]}')
                    choice = argvs[1]
                else:
                    if override_gallery_loc is None:
                        rich.print(f'[bold yellow]loc:[/bold yellow] sel {argvs[1]}')
                        override_gallery_loc = argvs[1]
                    else:
                        rich.print(f'[bold yellow]loc:[/bold yellow] sel {override_gallery_loc}')

                args_valid = True

            elif len(argvs) == 3:
                if argvs[1].isnumeric() and not argvs[2].isnumeric():
                    print(f'choice sel: {argvs[1]}\nloc sel: {argvs[2]}')
                    choice = argvs[1]
                    override_gallery_loc = argvs[2]
                elif not argvs[1].isnumeric() and argvs[2].isnumeric():
                    print(f'loc sel: {argvs[1]}\nchoice sel: {argvs[2]}')
                    choice = argvs[2]
                    override_gallery_loc = argvs[1]

                args_valid = True

            if not args_valid:
                print("Invalid or too many args passed")

    if override_gallery_loc is not None:
        if not os.path.exists(override_gallery_loc):
            print("Entered path is invalid, want to continue?")

    choice = int(choice) - 1

    # Calling main function with required arguments
    prefs = {"shuffle": shuffle,
             "override_gallery_loc": override_gallery_loc,
             "override_choice": override_choice}

    main(**prefs)


