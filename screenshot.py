
import os
import sys
import time
import shutil
import pygame
import subprocess as sp

from datetime import datetime as dt

platf = sys.platform

pygame.mixer.init()

if platf == 'win32':
    startup_sound = r"C:\Users\Vivo Jay\Desktop\mplayer-4\test\res\first_boot_startup_sound.mp3"
    sys.exit("Cannot use on windows! Aborting.")

elif platf == 'linux':
    startup_sound = r"/media/vivojay/Windows/Users/Vivo Jay/Desktop/mplayer-4/test/res/first_boot_startup_sound.mp3"
    src_dir = "~/Pictures/flameshot_tmp"
    dest_dir = "~/Pictures/Screenshots"

src_dir = os.path.expanduser(src_dir)
dest_dir = os.path.expanduser(dest_dir)

def screenshot_set_counter(val):
    counterval_file = os.path.join(src_dir, "counter.val")
    if os.path.isfile(counterval_file):
        os.remove(counterval_file)
    # Update counter value in config
    with open(os.path.join(src_dir, "counter.val"), "w") as fp:
        fp.write(str(val))

def screenshot_reset():
    counterval_file = os.path.join(src_dir, "counter.val")
    if os.path.isfile(counterval_file):
        os.remove(counterval_file)

def screenshot_task(src_dir, dest_dir, auto=False, notif_sound=True):

    # Create temp folder if not already present
    if not os.path.isdir(src_dir):
        os.mkdir(src_dir)

    if not os.path.isfile(os.path.join(src_dir, "counter.val")):
        # Create config file with counter value set as 0
        with open(os.path.join(src_dir, "counter.val"), "w") as fp:
            fp.write('0')

    # vars prefixed by 'x_' means they are a "shlex compliant" list of string for a valid command
    x_screenshot_cmd = "flameshot full -p".split() + [f'"{src_dir}"']

    # Update counter value in config
    with open(os.path.join(src_dir, "counter.val"), "r") as fp:
        counter = int(fp.read().strip())

    confirm = False
    if auto:
        confirm = True
        operation = shutil.move
        sp.call(' '.join(x_screenshot_cmd), shell=1)
    else:
        while True:
            perm = input("Dry run only? [*y/n]: ").strip().lower()

            if perm == 'y' or not perm:
                operation = print
                break
            elif perm == 'n':
                operation = shutil.move
                confirm = True
                break
            else:
                print("Invalid perm...")

    print("Start screenshotting")
    sp.call(' '.join(x_screenshot_cmd), shell=1)
    print("End screenshotting")
    if notif_sound and confirm:
        pygame.mixer.music.load(startup_sound)
        pygame.mixer.music.play()

    f = os.listdir(src_dir)
    f.remove('counter.val')

    _f = [time.mktime(dt.strptime(i, '%Y-%m-%d_%H-%M-%S.png').timetuple()) for i in f]

    pairs = sorted(zip(f, _f), key=lambda x: x[1])
    counter += len(f)

    pairs = [(j[0], f"{int(j[1])}_{counter+i+1}.png") for i, j in enumerate(pairs)]

    if not confirm:
        print()
    _ = [operation(os.path.join(src_dir, i), os.path.join(dest_dir, j)) for i, j in pairs]

    if confirm:
        # Update counter value in config
        with open(os.path.join(src_dir, "counter.val"), "w") as fp:
            fp.write(str(counter))
    
        time.sleep(3)

if __name__ == "__main__":
    screenshot_task(src_dir=src_dir, 
                    dest_dir=dest_dir,
                    auto=True)


