from tkinter import Tk, Button, Label

import os
import sys

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame
import time

os.chdir(os.path.dirname(os.path.abspath(__file__)))

def show_alert(notif_head, notif_body, notif_duration=5000):

    global fadeoutcounter, root_positioning_offset, motion_duration_factor, settings, alert_sound_index

    fadeoutcounter = 80
    root_positioning_offset = (1500, 900) # wrt screen
    fadeoutthreshold = fadeoutcounter
    motion_duration_factor = 1
    settings = {
        "layout": {
            "rootsize": (261, 115), # width, height
        },
        "colorscheme": {
            "rootbg": '#222',
            "headfg": '#63c6cf',
            "bodyfg": 'white',
        }
    }

    root_geometry= 'x'.join(map(lambda x: str(x), settings['layout']['rootsize']))

    def win_slideout():

        # Fadeout
        def fadeout():
            global fadeoutcounter
            fadeoutcounter -= 1

            root.geometry(f"{root_geometry}+{root_positioning_offset[0]+int(settings['layout']['rootsize'][0]/2)-(int(motion_duration_factor*fadeoutcounter))}+{root_positioning_offset[1]}")
            root.attributes('-alpha', fadeoutcounter/fadeoutthreshold)

            if fadeoutcounter:
                root.after(4, fadeout)
            else:
                root.destroy()

        fadeout()

    def window_closed():
        root.iconify()
        root.attributes('-topmost', False)

    root = Tk()

    pygame.mixer.init()
    pygame.mixer.music.load(f'res/alert_sound_0{alert_sound_index}.wav')
    pygame.mixer.music.play()

    root.geometry(f"{root_geometry}+{root_positioning_offset[0]}+{root_positioning_offset[1]}")
    root.configure(background = settings['colorscheme']['rootbg'])
    root.protocol("WM_DELETE_WINDOW", window_closed)
    root.resizable(False, False)
    # root.resizable(True, True) # Only for production
    root.attributes('-topmost', True)
    root.overrideredirect(True)
    root.lift() # Is this even needed?

    heading = Label(
        text = notif_head,
        font = ('Arial', 16, 'bold'),
        foreground = settings['colorscheme']['headfg'],
        background = settings['colorscheme']['rootbg'],
    )
    heading.grid(row=0, column=0, sticky='n', padx = 45)

    body = Label(
        text = notif_body,
        font = ('Arial', 10),
        foreground = settings['colorscheme']['bodyfg'],
        background = settings['colorscheme']['rootbg'],
    )
    body.grid(row=1, column=0, sticky='nw', padx = 5) #, padx = 85)

    root.after(notif_duration, win_slideout)
    root.mainloop()

if __name__ == "__main__":
    alert_sound_index = sys.argv[1]
    show_alert("Heading", "Body")
else:
    alert_sound_index = 1

