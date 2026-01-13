
# Import required libraries
import os
import time
import tkinter as tk

from tkinter import *
from PIL import ImageTk, Image
from datetime import datetime as dt

# Only for digital display right now
# Analog will be made later...

time_display_type = 24  # Displays standard 24 hour time
disp_type = 0           # 0 for digital, 1 for analog
seconds_toggle = 0      # 0 means seconds are hidden, 1 means visible

os.chdir(os.path.dirname(os.path.abspath(__file__)))

def update_cur_time(time_display, root):
    global time_display_type, seconds_toggle
    if time_display_type == 24:
        if seconds_toggle:
            cur_time = dt.now().strftime("%H:%M:%S")
        else:
            cur_time = dt.now().strftime("%H:%M")

    elif time_display_type == 12:
        if seconds_toggle:
            cur_time = dt.now().strftime("%I:%M:%S %p")
        else:
            cur_time = dt.now().strftime("%I:%M %p")

    time_display.configure(text = cur_time)
    root.after(10, lambda : update_cur_time(time_display, root))
    time_display.pack()

def update_cur_date(date_display, root):
    cur_date = dt.now().strftime("%d %b %Y")
    date_display.configure(text = cur_date)
    root.after(10, lambda : update_cur_date(date_display, root))
    date_display.pack()

def toggle_12_24(event):
    global time_display_type
    if time_display_type == 24:
        time_display_type = 12
    else:
        time_display_type = 24

def toggle_seconds_on_off(event):
    global seconds_toggle
    seconds_toggle = 1 - seconds_toggle

def get_wifi_status(hostname='one.one.one.one'):
    import socket, contextlib

    with contextlib.suppress(Exception):
        # see if we can resolve the host name -- tells us if there is
        # a DNS listening
        host = socket.gethostbyname(hostname)
        # connect to the host -- tells us if the host is actually
        # reachable
        s = socket.create_connection((host, 80), 2)
        s.close()
        return 1

    return 0

def update_wifi_status(wifi_status_display, root):
    wifi_stats = ["./assets/no-wifi.png", "./assets/wifi-hi-speed.png", "./assets/wifi-low-speed.png"]

    wifi_status = get_wifi_status()

    # Create an object of tkinter ImageTk
    wifi_img = ImageTk.PhotoImage(Image.open(wifi_stats[wifi_status]))
    wifi_status_display.configure(image = wifi_img)

    root.after(2000, lambda : update_wifi_status(wifi_status_display, root))
    wifi_status_display.pack()

def main():
    # Create root window
    root = tk.Tk()

    # Set root window configurations
    root.title("DATE & TIME")
    root.geometry("200x80")
    root.config(bg="black")
    root.attributes('-topmost', True)
    root.resizable(width=False, height=False)
    #root.overrideredirect(True)

    # Create Labels for Window
    date_display = tk.Label(root,
                            text = "", # Text is gonna be changed anyways...
                            font = "Helvetica 24 bold",
                            bg = "black",
                            fg = "#ff4df9")

    time_display = tk.Label(root,
                            text = "", # Text is gonna be changed anyways...
                            font = "Helvetica 24",
                            bg = "black",
                            fg = "#ad7dff")

    # Create an object of tkinter ImageTk
    wifi_img = ImageTk.PhotoImage(Image.open("./assets/no-wifi.png"))
    wifi_status_display = tk.Label(root,
                                   image = wifi_img) # Display Image will update in realtime...

    # Set Control Bindings
    time_display.bind("<Button-1>", toggle_12_24)
    time_display.bind("<Button-2>", toggle_seconds_on_off)
    time_display.bind("<Button-3>", toggle_seconds_on_off)

    # wifi_status_display.pack()
    date_display.pack()
    time_display.pack()

    # Set Update Routines
    update_cur_date(date_display, root)
    update_cur_time(time_display, root)
    #update_wifi_status(wifi_status_display, root)

    root.mainloop()

if __name__ == "__main__":
    main()


