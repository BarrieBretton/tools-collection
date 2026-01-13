# importing the module
import screen_brightness_control as sbc
import tkinter as tk
import time
import os
import PIL
import PIL.Image
import PIL.ImageTk

from tkinter import ttk

os.chdir(os.path.dirname(__file__))

win_style = 1
cached_vol = 0

try:
    from ctypes import cast, POINTER
    from comtypes import CLSCTX_ALL
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume, ISimpleAudioVolume

except ImportError:
    try:
        import alsaaudio
        win_style = 0
    except Exception:
        # TODO: Add Master Vol Ctrl Support for all OSes with all sound drivers
        print("WARN: Master Volume Control cannot be supported using either pycaw for Windows or ALSAMixer for Linux")
        print("      Support for macOS Master Vol Control is coming soon...")
        raise

system_is_muted = 0

def device_refresh():
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))
    return volume

def get_master_volume():
    if win_style:
        volume = device_refresh()
        return int(round(volume.GetMasterVolumeLevelScalar() * 100))
    else:
        mixer = alsaaudio.Mixer()
        vol = mixer.getvolume()
        if isinstance(vol, list):
            if vol[0] == vol[1]:
                vol = vol[0]
        return vol

def set_master_volume(scalarVolume):
    if win_style:
        # Using Windows OS
        volume = device_refresh()
        if scalarVolume >= 0:
            volume.SetMasterVolumeLevelScalar(scalarVolume/100, None)
            volume.SetMute(not bool(scalarVolume), None)
    else:
        # Using ALSA for Linux
        mixer = alsaaudio.Mixer()
        mixer.setvolume(scalarVolume)

def update_values(root, mv_icon, v, b):
    global system_is_muted

    try:
        current_brightness = sbc.get_brightness()
    except sbc.ScreenBrightnessError:
        try:
            current_brightness = sbc.get_brightness(display=0)
        except sbc.ScreenBrightnessError:
            current_brightness = 0

    if b.get() != current_brightness:
        b.set(current_brightness)

    current_master_volume = get_master_volume()
    if v.get() != current_master_volume:
        v.set(current_master_volume)

    volume = device_refresh()
    if system_is_muted != volume.GetMute():
        toggle_system_mute(root, mv_icon, v)

    root.after(100, lambda: update_values(root, mv_icon, v, b))


def set_b(value):
    sbc.set_brightness(int(value))

def set_mv(root, mv_icon, value, v):
    global system_is_muted

    value = int(value)
    mv_icon = './res/volume-hi-icon.png'

    too_high_volume_slider_color = 'maroon'

    if v['bg'] == too_high_volume_slider_color:
        v.configure(bg='#2A52AA')

    if value > 75:
        mv_icon = './res/volume-too-hi-icon.png'
        v.configure(bg=too_high_volume_slider_color)
    if value < 50:
        mv_icon = './res/volume-lo-icon.png'
    if value == 0:
        if system_is_muted:
            mv_icon = './res/volume-disabled-icon.png'
        else:
            mv_icon = './res/volume-mute-icon.png'

    set_master_volume(value)

    im = PIL.Image.open(mv_icon)
    im_size = im.size
    scaled_height = 30
    scaled_width = int(im_size[0]/im_size[1]*scaled_height)
    im = im.resize((scaled_width, scaled_height))
    photo = PIL.ImageTk.PhotoImage(im)

    mv_icon = tk.Label(root, image=photo, bg=root['bg'])
    # mv_icon.configure(bg="red")
    mv_icon.image = photo  # keep a reference!
    mv_icon.grid(row=0, column=0, padx=(40, 10), pady=(10, 20))

    # mv_icon.bind("<Button-1>", lambda e: mute_system(v))
    mv_icon.bind("<Button-3>", lambda e: toggle_system_mute(root, mv_icon, v))
    mv_icon.bind("<Button-3>", lambda e: toggle_system_mute(root, mv_icon, v))

    return mv_icon

def sleep(delay):
    for _ in range(delay):
        delay -= 1

def glide_to_click_position(root, event, mv_icon, slider, v, delay=10):
    """
    delay: given in ms
    """

    scale_width = slider['length']
    scale_min = slider['from']
    scale_max = slider['to']

    mouse_x = event.x
    scale_value = (mouse_x / scale_width) * (scale_max - scale_min) + scale_min    
    cur_value = slider.get()

    if cur_value != scale_value:
        if slider.kind == 0:
            # Master Volume Related
            set_mv(root, mv_icon, scale_value, v)
        else:
            # Brightness Related
            set_b(scale_value)
        slider.set(scale_value)

    return

    if cur_value != scale_value:
        dist = scale_value - cur_value
        _dist = dist
        while dist > 0:
            cur_value = slider.get()
            dist = scale_value - cur_value
            if slider.kind == 0:
                # Master Volume Related
                set_mv(root, mv_icon, cur_value+1)
            else:
                # Brightness Related
                set_b(cur_value+1)
                # if slider.get() != sbc.get_brightness():
                #     pass
            slider.set(cur_value+1)
            sleep(int(delay/_dist)*100)

        while dist < 0:
            cur_value = slider.get()
            dist = scale_value - cur_value
            if slider.kind == 0:
                # Master Volume Related
                set_mv(root, mv_icon, cur_value-1)
            else:
                # Brightness Related
                set_b(cur_value-1)
            slider.set(cur_value-1)
            sleep(int(delay/_dist)*100)

def show_cached_volume(root, mv_icon, v, cached_vol):
    global cached_vol_label

    # mv_icon.grid_forget()
    # mv_icon.grid(row=0, column=0, padx=(15, 10), pady=(20, 0))
    v.grid(row=0, column=1, pady=(20, 20))

    cached_vol_label = tk.Label(root,
                                text=cached_vol,
                                fg='#00FFFF',
                                bg='black',
                                font='Tahoma 12 bold')
    cached_vol_label.grid(row=1, column=0)

def hide_cached_volume(root, mv_icon, v, cached_vol_label):
    # mv_icon.grid_forget()
    # mv_icon.configure(padx=(15, 10), pady=(20, 0))
    # mv_icon.grid(row=0, column=0, padx=(15, 10), pady=(20, 0))
    v.grid(row=0, column=1, pady=(20, 40))

    cached_vol_label.grid_forget()


def toggle_system_mute(root, mv_icon, v):
    global system_is_muted, cached_vol, win_style, cached_vol_label

    # Toggle flag first
    system_is_muted = 1 - system_is_muted

    if system_is_muted:
        cached_vol = get_master_volume()
        set_master_volume(0)
        v.configure(bg="#333")
        # v.set(0)
        show_cached_volume(root, mv_icon, v, cached_vol)
    else:
        set_master_volume(cached_vol)
        v.configure(bg="#2A52AA")
        hide_cached_volume(root, mv_icon, v, cached_vol_label)

    if win_style:
        volume = device_refresh()

        volume.SetMute(system_is_muted, None)


    # # Master Volume Icon Init
    # im = PIL.Image.open("./res/volume-disabled-icon.png")
    # im_size = im.size
    # scaled_height = 30
    # scaled_width = int(im_size[0]/im_size[1]*scaled_height)
    # im = im.resize((scaled_width, scaled_height))
    # photo = PIL.ImageTk.PhotoImage(im)

    # mv_icon = tk.Label(root, image=photo, bg=root['bg'])
    # mv_icon.grid(row=0, column=0)



def main():
    root = tk.Tk()
    root.geometry('240x160')
    root.configure(bg="black")
    root.attributes('-topmost', True)
    root.resizable(0,0)
    root.title("Master Control Hub")
    # root.wm_attributes('-transparentcolor', 'red')

    # Master Volume Icon Init
    im = PIL.Image.open("./res/volume-hi-icon.png")
    im_size = im.size
    scaled_height = 30
    scaled_width = int(im_size[0]/im_size[1]*scaled_height)
    im = im.resize((scaled_width, scaled_height))
    photo = PIL.ImageTk.PhotoImage(im)

    mv_icon = tk.Label(root, image=photo, bg=root['bg'])
    mv_icon.grid(row=0, column=0, padx=(40, 10), pady=(20))

    # Brightness Icon Init
    im = PIL.Image.open("./res/brightness-icon.png")
    im_size = im.size
    scaled_height = 30
    scaled_width = int(im_size[0]/im_size[1]*scaled_height)
    im = im.resize((scaled_width, scaled_height))
    photo = PIL.ImageTk.PhotoImage(im)

    brightness_icon = tk.Label(root, image=photo, bg=root['bg'])
    brightness_icon.grid(row=2, column=0, padx=(20, 0))

    v = tk.Scale(root,
                 from_=0,
                 to=100,
                 orient=tk.HORIZONTAL,
                 bg='#2A52AA',
                 fg='white',
                 font='Tahoma 12',
                 troughcolor='#000',
                 sliderlength=25,
                 sliderrelief='flat',
                 relief='flat',
                 highlightthickness=0,
                 command=lambda value: set_mv(root, brightness_icon, value, v))
    v.grid(row=0, column=1, pady=(20, 40))

    b = tk.Scale(root,
                 from_=0,
                 to=100,
                 orient=tk.HORIZONTAL,
                 bg='#2A52AA',
                 fg='white',
                 font='Tahoma 12',
                 troughcolor='#000',
                 sliderlength=25,
                 sliderrelief='flat',
                 relief='flat',
                 highlightthickness=0,
                 command=set_b)
    b.grid(row=2, column=1)

    update_values(root, mv_icon, v, b)

    # Can help distinguish the kind of slider when `glide_to_click_position` is called
    v.kind = 0
    b.kind = 1

    v.bind("<Button-1>", lambda e: glide_to_click_position(root, e, mv_icon, v, v))
    b.bind("<Button-1>", lambda e: glide_to_click_position(root, e, mv_icon, b, v))

    root.mainloop()


if __name__ == "__main__":
    main()

