import os
import platform
import queue
import re
import shutil
import subprocess
import threading
import time
import tkinter as tk
from pathlib import Path

import screen_brightness_control as sbc
from PIL import Image, ImageTk

try:
    from pycaw.pycaw import AudioUtilities
except ImportError:
    AudioUtilities = None

try:
    import alsaaudio
except ImportError:
    alsaaudio = None


APP_W = 280
APP_H = 165
BG = "#111111"
FG = "white"
ACCENT = "#2A52AA"
ACCENT_WARN = "#6b1d1d"
TROUGH = "#000000"
MUTED_BG = "#333333"

BASE_DIR = Path(__file__).resolve().parent
RES_DIR = BASE_DIR / "res"


# ----------------------------
# Volume backends
# ----------------------------
class WindowsVolumeBackend:
    def __init__(self):
        self._endpoint = None

    def _volume(self):
        if self._endpoint is None:
            devices = AudioUtilities.GetSpeakers()
            self._endpoint = devices.EndpointVolume
        return self._endpoint

    def get_volume(self):
        return int(round(self._volume().GetMasterVolumeLevelScalar() * 100))

    def set_volume(self, value):
        value = max(0, min(100, int(value)))
        vol = self._volume()
        vol.SetMasterVolumeLevelScalar(value / 100.0, None)
        vol.SetMute(int(value == 0), None)

    def is_muted(self):
        return bool(self._volume().GetMute())

    def set_muted(self, muted):
        self._volume().SetMute(int(bool(muted)), None)


class AlsaVolumeBackend:
    def __init__(self):
        mixers = ["Master"] + list(alsaaudio.mixers())
        seen = set()
        self._mixer = None
        for name in mixers:
            if name in seen:
                continue
            seen.add(name)
            try:
                self._mixer = alsaaudio.Mixer(name)
                break
            except Exception:
                continue
        if self._mixer is None:
            raise RuntimeError("No ALSA mixer available")

    def get_volume(self):
        levels = self._mixer.getvolume()
        return int(round(sum(levels) / max(len(levels), 1)))

    def set_volume(self, value):
        self._mixer.setvolume(max(0, min(100, int(value))))

    def is_muted(self):
        try:
            mute_state = self._mixer.getmute()
            return bool(mute_state and all(mute_state))
        except Exception:
            return self.get_volume() == 0

    def set_muted(self, muted):
        try:
            self._mixer.setmute(int(bool(muted)))
        except Exception:
            if muted:
                self.set_volume(0)


class CommandVolumeBackend:
    def __init__(self, mode):
        self.mode = mode

    def _run(self, *args):
        return subprocess.run(
            args,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()

    def get_volume(self):
        if self.mode == "wpctl":
            output = self._run("wpctl", "get-volume", "@DEFAULT_AUDIO_SINK@")
            match = re.search(r"([0-9]*\.?[0-9]+)", output)
            if not match:
                raise RuntimeError(output)
            return int(round(float(match.group(1)) * 100))
        if self.mode == "pactl":
            output = self._run("pactl", "get-sink-volume", "@DEFAULT_SINK@")
            match = re.search(r"(\d+)%", output)
            if not match:
                raise RuntimeError(output)
            return int(match.group(1))
        if self.mode == "amixer":
            output = self._run("amixer", "get", "Master")
            match = re.search(r"\[(\d+)%\]", output)
            if not match:
                raise RuntimeError(output)
            return int(match.group(1))
        if self.mode == "osascript":
            return int(self._run("osascript", "-e", "output volume of (get volume settings)"))
        raise RuntimeError(f"Unsupported backend: {self.mode}")

    def set_volume(self, value):
        value = max(0, min(100, int(value)))
        if self.mode == "wpctl":
            self._run("wpctl", "set-volume", "@DEFAULT_AUDIO_SINK@", f"{value}%")
            self._run("wpctl", "set-mute", "@DEFAULT_AUDIO_SINK@", "0" if value else "1")
            return
        if self.mode == "pactl":
            self._run("pactl", "set-sink-volume", "@DEFAULT_SINK@", f"{value}%")
            self._run("pactl", "set-sink-mute", "@DEFAULT_SINK@", "0" if value else "1")
            return
        if self.mode == "amixer":
            self._run("amixer", "set", "Master", f"{value}%")
            self._run("amixer", "set", "Master", "mute" if value == 0 else "unmute")
            return
        if self.mode == "osascript":
            self._run("osascript", "-e", f"set volume output volume {value}")
            self._run("osascript", "-e", f"set volume output muted {'true' if value == 0 else 'false'}")
            return
        raise RuntimeError(f"Unsupported backend: {self.mode}")

    def is_muted(self):
        if self.mode == "wpctl":
            return "[MUTED]" in self._run("wpctl", "get-volume", "@DEFAULT_AUDIO_SINK@")
        if self.mode == "pactl":
            return self._run("pactl", "get-sink-mute", "@DEFAULT_SINK@").endswith("yes")
        if self.mode == "amixer":
            return "[off]" in self._run("amixer", "get", "Master")
        if self.mode == "osascript":
            return self._run("osascript", "-e", "output muted of (get volume settings)") == "true"
        raise RuntimeError(f"Unsupported backend: {self.mode}")

    def set_muted(self, muted):
        muted = bool(muted)
        if self.mode == "wpctl":
            self._run("wpctl", "set-mute", "@DEFAULT_AUDIO_SINK@", "1" if muted else "0")
            return
        if self.mode == "pactl":
            self._run("pactl", "set-sink-mute", "@DEFAULT_SINK@", "1" if muted else "0")
            return
        if self.mode == "amixer":
            self._run("amixer", "set", "Master", "mute" if muted else "unmute")
            return
        if self.mode == "osascript":
            self._run("osascript", "-e", f"set volume output muted {'true' if muted else 'false'}")
            return
        raise RuntimeError(f"Unsupported backend: {self.mode}")


def create_volume_backend():
    system_name = platform.system()
    if system_name == "Windows" and AudioUtilities is not None:
        return WindowsVolumeBackend()
    if alsaaudio is not None:
        return AlsaVolumeBackend()

    command_backends = {
        "Linux": ("wpctl", "pactl", "amixer"),
        "Darwin": ("osascript",),
        "Windows": (),
    }
    for command in command_backends.get(system_name, ()):
        if shutil.which(command):
            return CommandVolumeBackend(command)

    raise RuntimeError(
        f"Master volume control is unsupported on {system_name}: "
        "no compatible audio backend was found."
    )


# ----------------------------
# Optimized app
# ----------------------------
class ControlHub:
    def __init__(self, root):
        self.root = root
        self.root.title("Master Control Hub")
        self.root.geometry(f"{APP_W}x{APP_H}")
        self.root.configure(bg=BG)
        self.root.attributes("-topmost", True)
        self.root.resizable(False, False)

        self.volume_backend = create_volume_backend()

        self.system_is_muted = False
        self.cached_vol = 50

        self.last_brightness = None
        self.last_volume = None
        self.last_mute = None

        self.pending_volume = None
        self.pending_brightness = None

        self.volume_debounce_job = None
        self.brightness_debounce_job = None

        self.ui_queue = queue.Queue()
        self.stop_event = threading.Event()

        self.monitors = self._get_monitors_cached()
        self.icon_cache = self._load_icons()

        self._build_ui()
        self._start_worker()

        self.root.after(100, self._process_ui_queue)
        self.root.after(750, self._schedule_state_refresh)
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

        self._enqueue_refresh()

    # ---------- Setup ----------
    def _get_monitors_cached(self):
        try:
            monitors = sbc.list_monitors()
            return list(dict.fromkeys(monitors))
        except Exception:
            return []

    def _load_icon(self, filename, target_h=30):
        path = RES_DIR / filename
        img = Image.open(path)
        w, h = img.size
        target_w = int(w / h * target_h)
        img = img.resize((target_w, target_h), Image.LANCZOS)
        return ImageTk.PhotoImage(img)

    def _load_icons(self):
        return {
            "volume_hi": self._load_icon("volume-hi-icon.png"),
            "volume_lo": self._load_icon("volume-lo-icon.png"),
            "volume_too_hi": self._load_icon("volume-too-hi-icon.png"),
            "volume_mute": self._load_icon("volume-mute-icon.png"),
            "volume_disabled": self._load_icon("volume-disabled-icon.png"),
            "brightness": self._load_icon("brightness-icon.png"),
        }

    def _build_ui(self):
        self.mv_icon_label = tk.Label(
            self.root,
            image=self.icon_cache["volume_hi"],
            bg=BG,
        )
        self.mv_icon_label.grid(row=0, column=0, padx=(28, 10), pady=(18, 10))

        self.brightness_icon_label = tk.Label(
            self.root,
            image=self.icon_cache["brightness"],
            bg=BG,
        )
        self.brightness_icon_label.grid(row=2, column=0, padx=(28, 10), pady=(8, 10))

        self.volume_scale = tk.Scale(
            self.root,
            from_=0,
            to=100,
            orient=tk.HORIZONTAL,
            length=170,
            bg=ACCENT,
            fg=FG,
            font=("Tahoma", 11),
            troughcolor=TROUGH,
            sliderlength=24,
            sliderrelief="flat",
            relief="flat",
            highlightthickness=0,
            command=self._on_volume_slider,
        )
        self.volume_scale.grid(row=0, column=1, pady=(18, 10))

        self.brightness_scale = tk.Scale(
            self.root,
            from_=0,
            to=100,
            orient=tk.HORIZONTAL,
            length=170,
            bg=ACCENT,
            fg=FG,
            font=("Tahoma", 11),
            troughcolor=TROUGH,
            sliderlength=24,
            sliderrelief="flat",
            relief="flat",
            highlightthickness=0,
            command=self._on_brightness_slider,
        )
        self.brightness_scale.grid(row=2, column=1, pady=(8, 10))

        self.cached_vol_label = tk.Label(
            self.root,
            text="",
            fg="#00FFFF",
            bg=BG,
            font=("Tahoma", 11, "bold"),
        )
        self.cached_vol_label.grid(row=1, column=0, columnspan=2, pady=(0, 2))
        self.cached_vol_label.grid_remove()

        self.mv_icon_label.bind("<Button-3>", self._toggle_mute)
        self.mv_icon_label.bind("<Button-1>", self._toggle_mute)

        self.volume_scale.bind("<Button-1>", self._jump_to_click)
        self.brightness_scale.bind("<Button-1>", self._jump_to_click)

    # ---------- Worker ----------
    def _start_worker(self):
        self.worker = threading.Thread(target=self._worker_loop, daemon=True)
        self.worker.start()

    def _worker_loop(self):
        while not self.stop_event.is_set():
            try:
                task = self.ui_queue.get(timeout=0.2)
            except queue.Empty:
                continue

            action = task.get("action")
            try:
                if action == "refresh":
                    self._worker_refresh_state()
                elif action == "set_volume":
                    self._worker_set_volume(task["value"])
                elif action == "set_brightness":
                    self._worker_set_brightness(task["value"])
                elif action == "set_mute":
                    self._worker_set_mute(task["muted"])
            except Exception:
                pass
            finally:
                self.ui_queue.task_done()

    def _enqueue_refresh(self):
        self.ui_queue.put({"action": "refresh"})

    def _worker_refresh_state(self):
        try:
            current_brightness = sbc.get_brightness()
            if isinstance(current_brightness, (list, tuple)):
                current_brightness = current_brightness[0]
            current_brightness = int(round(current_brightness))
        except Exception:
            current_brightness = None

        try:
            current_volume = int(round(self.volume_backend.get_volume()))
        except Exception:
            current_volume = None

        try:
            current_mute = bool(self.volume_backend.is_muted())
        except Exception:
            current_mute = None

        self.root.after(
            0,
            lambda: self._apply_state_from_worker(
                current_brightness,
                current_volume,
                current_mute,
            ),
        )

    def _worker_set_volume(self, value):
        value = max(0, min(100, int(value)))
        self.volume_backend.set_volume(value)
        try:
            muted = bool(self.volume_backend.is_muted())
        except Exception:
            muted = (value == 0)

        self.root.after(0, lambda: self._apply_volume_feedback(value, muted))

    def _worker_set_brightness(self, value):
        value = max(0, min(100, int(value)))
        for monitor in self.monitors:
            try:
                sbc.set_brightness(value, display=monitor)
            except Exception:
                continue
        self.root.after(0, lambda: self._apply_brightness_feedback(value))

    def _worker_set_mute(self, muted):
        self.volume_backend.set_muted(muted)
        try:
            current_volume = int(round(self.volume_backend.get_volume()))
        except Exception:
            current_volume = None
        self.root.after(0, lambda: self._apply_mute_feedback(bool(muted), current_volume))

    # ---------- UI updates ----------
    def _apply_state_from_worker(self, brightness, volume, mute):
        if brightness is not None and self.pending_brightness is None:
            if self.last_brightness != brightness:
                self.last_brightness = brightness
                self.brightness_scale.set(brightness)

        if volume is not None and self.pending_volume is None:
            if self.last_volume != volume:
                self.last_volume = volume
                self.volume_scale.set(volume)

        if mute is not None:
            self.system_is_muted = mute
            self.last_mute = mute

        self._refresh_volume_icon_and_style()

    def _apply_volume_feedback(self, volume, muted):
        self.pending_volume = None
        self.last_volume = volume
        self.system_is_muted = muted
        self.last_mute = muted
        if self.volume_scale.get() != volume:
            self.volume_scale.set(volume)
        self._refresh_volume_icon_and_style()

    def _apply_brightness_feedback(self, brightness):
        self.pending_brightness = None
        self.last_brightness = brightness
        if self.brightness_scale.get() != brightness:
            self.brightness_scale.set(brightness)

    def _apply_mute_feedback(self, muted, volume):
        self.system_is_muted = muted
        self.last_mute = muted
        if volume is not None:
            self.last_volume = volume
            if self.volume_scale.get() != volume:
                self.volume_scale.set(volume)
        self._refresh_volume_icon_and_style()

    def _refresh_volume_icon_and_style(self):
        value = self.volume_scale.get()

        if self.system_is_muted:
            self.mv_icon_label.configure(image=self.icon_cache["volume_disabled"])
            self.volume_scale.configure(bg=MUTED_BG)
            self.cached_vol_label.configure(text=str(self.cached_vol))
            self.cached_vol_label.grid()
            return

        self.cached_vol_label.grid_remove()

        if value == 0:
            icon = self.icon_cache["volume_mute"]
            color = ACCENT
        elif value < 50:
            icon = self.icon_cache["volume_lo"]
            color = ACCENT
        elif value > 75:
            icon = self.icon_cache["volume_too_hi"]
            color = ACCENT_WARN
        else:
            icon = self.icon_cache["volume_hi"]
            color = ACCENT

        self.mv_icon_label.configure(image=icon)
        self.volume_scale.configure(bg=color)

    # ---------- Slider handling ----------
    def _on_volume_slider(self, value):
        value = int(float(value))
        self.pending_volume = value

        if self.volume_debounce_job is not None:
            self.root.after_cancel(self.volume_debounce_job)

        self._refresh_volume_icon_and_style()
        self.volume_debounce_job = self.root.after(35, lambda: self.ui_queue.put({
            "action": "set_volume",
            "value": value,
        }))

    def _on_brightness_slider(self, value):
        value = int(float(value))
        self.pending_brightness = value

        if self.brightness_debounce_job is not None:
            self.root.after_cancel(self.brightness_debounce_job)

        self.brightness_debounce_job = self.root.after(50, lambda: self.ui_queue.put({
            "action": "set_brightness",
            "value": value,
        }))

    def _jump_to_click(self, event):
        slider = event.widget
        length = int(slider.cget("length"))
        minv = int(slider.cget("from"))
        maxv = int(slider.cget("to"))

        x = max(0, min(length, event.x))
        value = round(minv + (x / length) * (maxv - minv))
        slider.set(value)
        return "break"

    # ---------- Polling ----------
    def _schedule_state_refresh(self):
        if self.stop_event.is_set():
            return
        if self.pending_volume is None and self.pending_brightness is None:
            self._enqueue_refresh()
        self.root.after(900, self._schedule_state_refresh)

    # ---------- Mute ----------
    def _toggle_mute(self, event=None):
        current_volume = self.volume_scale.get()

        if not self.system_is_muted:
            self.cached_vol = current_volume if current_volume > 0 else (self.last_volume or 50)
            self.system_is_muted = True
            self._refresh_volume_icon_and_style()
            self.ui_queue.put({"action": "set_mute", "muted": True})
        else:
            self.system_is_muted = False
            restore = self.cached_vol if self.cached_vol > 0 else 50
            self.pending_volume = restore
            self.volume_scale.set(restore)
            self._refresh_volume_icon_and_style()
            self.ui_queue.put({"action": "set_mute", "muted": False})
            self.ui_queue.put({"action": "set_volume", "value": restore})

    # ---------- Shutdown ----------
    def _process_ui_queue(self):
        if self.stop_event.is_set():
            return
        self.root.after(50, self._process_ui_queue)

    def _on_close(self):
        self.stop_event.set()
        self.root.destroy()


def main():
    root = tk.Tk()
    ControlHub(root)
    root.mainloop()


if __name__ == "__main__":
    main()