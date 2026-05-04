import json
import os
import threading
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"

import pygame
import requests
import tkinter as tk


# -----------------------------
# Positioning
# -----------------------------
TIME_BASELINE_Y = 36
FRAC_BASELINE_OFFSET = 0
AMPM_BASELINE_OFFSET = 0


# -----------------------------
# Window sizing (smaller / tighter)
# -----------------------------
WIDTH = 232
HEIGHT = 76
TITLEBAR_HEIGHT = 18


# -----------------------------
# Theme
# -----------------------------
BG_TOP = "#1f2933"
BG_BOTTOM = "#323f4b"
BG_LINE = "#3e4c59"
TITLE_BG = "#16202a"
TITLE_TEXT = "#d9e2ec"

TEXT_TIME = "#f0f4f8"
TEXT_DATE = "#9aa5b1"
TEXT_MUTED = "#7b8794"

DOT_ON = "#2bb673"
DOT_OFF = "#d64545"

TEXT_CODEX_OK = "#2bb673"
TEXT_CODEX_WAIT = "#f0b429"
TEXT_CODEX_ERR = "#d64545"

BTN_ON = "#2d3748"
BTN_OFF = "#52606d"
BTN_HOVER = "#3e4c59"

# -----------------------------
# Codex config
# -----------------------------
CODEX_AUTH_PATH = Path(os.environ.get("CODEX_AUTH_FILE", "~/.codex/auth.json")).expanduser()
CODEX_USAGE_URL = "https://chatgpt.com/backend-api/codex/usage"
CODEX_BUFFER_PERCENT = 5.0

ALARM_SOUND_PATH = Path(
    r"C:\Users\Vivan.Jaiswal\Documents\ffmpeg-2025-12-18-git-78c75d546a-essentials_build\bin\Yumi Zouma - In Camera [Q7BytPT-jYU].opus"
)


def hex_to_rgb(value: str):
    value = value.lstrip("#")
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))


def check_internet() -> bool:
    url = "https://clients3.google.com/generate_204"
    headers = {"User-Agent": "Mozilla/5.0"}
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=1.5) as resp:
            return resp.status == 204
    except Exception:
        return False


def first_nonempty(*values):
    for value in values:
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def load_codex_token(auth_path: Path) -> str:
    if not auth_path.exists():
        raise FileNotFoundError(f"Auth file not found: {auth_path}")

    data = json.loads(auth_path.read_text(encoding="utf-8"))

    token = first_nonempty(
        data.get("access_token"),
        data.get("id_token"),
        data.get("token"),
    )
    if token:
        return token

    tokens = data.get("tokens", {})
    if isinstance(tokens, dict):
        token = first_nonempty(
            tokens.get("access_token"),
            tokens.get("id_token"),
        )
        if token:
            return token

    raise RuntimeError("No usable token found in Codex auth file.")


def fetch_codex_usage(token: str) -> dict:
    resp = requests.get(
        CODEX_USAGE_URL,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
            "User-Agent": "codex-mini-widget/1.0",
        },
        timeout=15,
    )
    if resp.status_code == 401:
        raise RuntimeError("Unauthorized. Run `codex login` again.")
    resp.raise_for_status()
    return resp.json()


def remaining_percent(window: dict) -> float:
    return max(0.0, 100.0 - float(window.get("used_percent", 0)))


def is_effectively_empty(window: dict, buffer_percent: float = CODEX_BUFFER_PERCENT) -> bool:
    return remaining_percent(window) <= buffer_percent


def get_next_usable_reset(primary: dict, secondary: dict) -> int | None:
    blocked_reset_times: list[int] = []

    if is_effectively_empty(primary):
        blocked_reset_times.append(primary["reset_at"])

    if is_effectively_empty(secondary):
        blocked_reset_times.append(secondary["reset_at"])

    if not blocked_reset_times:
        return None

    return min(blocked_reset_times)


def get_codex_status() -> tuple[bool | None, datetime | None, str]:
    try:
        token = load_codex_token(CODEX_AUTH_PATH)
        data = fetch_codex_usage(token)

        rate_limit = data["rate_limit"]
        primary = rate_limit["primary_window"]
        secondary = rate_limit["secondary_window"]

        next_reset_ts = get_next_usable_reset(primary, secondary)

        if next_reset_ts is None:
            return True, None, "AVAILABLE"

        next_dt = datetime.fromtimestamp(next_reset_ts, tz=timezone.utc).astimezone()
        return False, next_dt, f"NEXT {next_dt.strftime('%a %I:%M %p')}"

    except Exception:
        return None, None, "CODEX ERR"


class CompactTitleBar(tk.Frame):
    def __init__(self, master, title: str, on_close):
        super().__init__(master, bg=TITLE_BG, height=TITLEBAR_HEIGHT)
        self.pack_propagate(False)
        self._on_close = on_close

        self.title_label = tk.Label(
            self,
            text=title,
            bg=TITLE_BG,
            fg=TITLE_TEXT,
            font=("Segoe UI", 7, "bold"),
            anchor="w",
            padx=5,
        )
        self.title_label.pack(side="left", fill="y")

        self.close_btn = tk.Label(
            self,
            text=" × ",
            bg=TITLE_BG,
            fg=TITLE_TEXT,
            font=("Segoe UI", 8, "bold"),
            padx=5,
            cursor="hand2",
        )
        self.close_btn.pack(side="right", fill="y")

        self.close_btn.bind("<Button-1>", lambda e: self._on_close())
        self.close_btn.bind("<Enter>", lambda e: self.close_btn.config(bg="#7b1f1f"))
        self.close_btn.bind("<Leave>", lambda e: self.close_btn.config(bg=TITLE_BG))

        for widget in (self, self.title_label):
            widget.bind("<ButtonPress-1>", self._start_move)
            widget.bind("<B1-Motion>", self._do_move)

        self._drag_start_x = 0
        self._drag_start_y = 0

    def _start_move(self, event):
        self._drag_start_x = event.x_root
        self._drag_start_y = event.y_root

    def _do_move(self, event):
        dx = event.x_root - self._drag_start_x
        dy = event.y_root - self._drag_start_y
        root = self.winfo_toplevel()
        x = root.winfo_x() + dx
        y = root.winfo_y() + dy
        root.geometry(f"+{x}+{y}")
        self._drag_start_x = event.x_root
        self._drag_start_y = event.y_root


class DateTimeCodexWidget:
    def __init__(self, root, fraction_digits=1):
        self.root = root
        self.root.overrideredirect(True)
        self.root.geometry(f"{WIDTH}x{HEIGHT + TITLEBAR_HEIGHT}+20+20")
        self.root.resizable(False, False)
        self.root.attributes("-topmost", True)
        self.root.configure(bg=BG_BOTTOM)

        # Default view: 12-hour, seconds on, fractional seconds on
        self.time_display_type = 12
        self.seconds_toggle = True
        self.fraction_digits = max(0, int(fraction_digits))

        self._connected = False
        self._codex_available: bool | None = None
        self._codex_next_dt = None
        self._codex_status_text = "CODEX ..."
        self._codex_state_known = False
        self._previous_known_codex_available: bool | None = None

        self.codex_alarm_enabled = True

        self._lock = threading.Lock()
        self._codex_lock = threading.Lock()
        self._audio_lock = threading.Lock()
        self._stop_event = threading.Event()
        self._codex_stop_event = threading.Event()

        self._time_after_id = None
        self._status_after_id = None
        self._codex_after_id = None
        self._closed = False
        self._last_time_text = None
        self._last_date_text = None
        self._alarm_playing = False

        self.titlebar = CompactTitleBar(root, "DT • Codex", self._on_close)
        self.titlebar.pack(fill="x")

        self.canvas = tk.Canvas(
            root,
            width=WIDTH,
            height=HEIGHT,
            highlightthickness=0,
            bd=0,
            bg=BG_TOP,
        )
        self.canvas.pack(fill="both", expand=True)

        self._draw_background()

        self.date_item = self.canvas.create_text(
            8, 10,
            anchor="w",
            fill=TEXT_DATE,
            font=("Segoe UI", 7),
            text="---, -- --- ----",
        )

        self.time_item = self.canvas.create_text(
            8, 30,
            anchor="w",
            fill=TEXT_TIME,
            font=("Segoe UI", 15, "bold"),
            text="--:--:--",
        )

        # decisecond placed lower than main text = subscript feel
        self.time_frac_item = self.canvas.create_text(
            8, 30,
            anchor="w",
            fill=TEXT_TIME,
            font=("Segoe UI", 8, "bold"),
            text="",
        )

        self.time_ampm_item = self.canvas.create_text(
            8, 30,
            anchor="w",
            fill=TEXT_TIME,
            font=("Segoe UI", 11, "bold"),
            text="",
        )

        self.dot_item = self.canvas.create_oval(
            8, 46, 13, 51,
            fill=DOT_OFF,
            outline=""
        )

        self.status_item = self.canvas.create_text(
            17, 49,
            anchor="w",
            fill=DOT_OFF,
            font=("Segoe UI", 7, "bold"),
            text="OFFLINE",
        )

        self.codex_item = self.canvas.create_text(
            WIDTH - 8, 49,
            anchor="e",
            fill=TEXT_CODEX_WAIT,
            font=("Segoe UI", 7, "bold"),
            text="CODEX ...",
        )

        self.hint_item = self.canvas.create_text(
            8, 65,
            anchor="w",
            fill=TEXT_MUTED,
            font=("Segoe UI", 6),
            text="L:12/24  R:Sec",
        )

        self.alarm_toggle_bg = self.canvas.create_rectangle(
            WIDTH - 74, 58, WIDTH - 8, 69,
            fill=BTN_ON,
            outline=""
        )

        self.alarm_toggle_item = self.canvas.create_text(
            WIDTH - 41, 63.5,
            anchor="center",
            fill=TEXT_TIME,
            font=("Segoe UI", 6, "bold"),
            text="ALARM ON",
        )

        for item in (self.time_item, self.time_frac_item, self.time_ampm_item):
            self.canvas.tag_bind(item, "<Button-1>", self.toggle_12_24)
            self.canvas.tag_bind(item, "<Button-3>", self.toggle_seconds)
            self.canvas.tag_bind(item, "<Button-2>", self.toggle_seconds)

        for item in (self.alarm_toggle_bg, self.alarm_toggle_item):
            self.canvas.tag_bind(item, "<Button-1>", self.toggle_codex_alarm)
            self.canvas.tag_bind(item, "<Enter>", self._alarm_hover_on)
            self.canvas.tag_bind(item, "<Leave>", self._alarm_hover_off)

        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

        self._start_connectivity_thread()
        self._start_codex_thread()
        self.update_datetime()
        self.update_status()
        self.update_codex_status()

    def _draw_background(self):
        r1, g1, b1 = hex_to_rgb(BG_TOP)
        r2, g2, b2 = hex_to_rgb(BG_BOTTOM)

        for i in range(HEIGHT):
            ratio = i / max(HEIGHT - 1, 1)
            r = int(r1 + (r2 - r1) * ratio)
            g = int(g1 + (g2 - g1) * ratio)
            b = int(b1 + (b2 - b1) * ratio)
            color = f"#{r:02x}{g:02x}{b:02x}"
            self.canvas.create_line(0, i, WIDTH, i, fill=color)

        for x in range(-30, WIDTH, 56):
            self.canvas.create_line(x, 0, x + 46, HEIGHT, fill=BG_LINE)

        self.canvas.create_rectangle(0, 0, WIDTH, 1, fill="#bcccdc", outline="")

    def _alarm_hover_on(self, event=None):
        self.canvas.itemconfig(self.alarm_toggle_bg, fill=BTN_HOVER)

    def _alarm_hover_off(self, event=None):
        self.canvas.itemconfig(
            self.alarm_toggle_bg,
            fill=BTN_ON if self.codex_alarm_enabled else BTN_OFF,
        )

    def toggle_12_24(self, event=None):
        self.time_display_type = 12 if self.time_display_type == 24 else 24
        self._last_time_text = None
        self.update_datetime()

    def toggle_seconds(self, event=None):
        self.seconds_toggle = not self.seconds_toggle
        self._last_time_text = None
        self.update_datetime()

    def toggle_codex_alarm(self, event=None):
        self.codex_alarm_enabled = not self.codex_alarm_enabled
        if not self.codex_alarm_enabled:
            self._stop_codex_alarm()
        self.update_codex_status()

    def _get_wall_clock_parts(self):
        now_ns = time.time_ns()
        sec = now_ns // 1_000_000_000
        frac_ns = now_ns % 1_000_000_000
        now_dt = datetime.fromtimestamp(sec + frac_ns / 1_000_000_000)
        return now_dt, frac_ns

    def _fraction_value(self, frac_ns):
        if self.fraction_digits <= 0:
            return None

        scale = 10 ** self.fraction_digits
        value = (frac_ns * scale) // 1_000_000_000
        if value >= scale:
            value = scale - 1
        return value

    def _format_time(self, now_dt, frac_ns):
        if not self.seconds_toggle:
            if self.time_display_type == 24:
                return now_dt.strftime("%H:%M"), "", ""
            return now_dt.strftime("%I:%M"), "", now_dt.strftime("%p")

        if self.time_display_type == 24:
            base = now_dt.strftime("%H:%M:%S")
            ampm = ""
        else:
            base = now_dt.strftime("%I:%M:%S")
            ampm = now_dt.strftime("%p")

        frac_part = ""
        if self.fraction_digits > 0:
            frac_value = self._fraction_value(frac_ns)
            frac_text = f"{frac_value:0{self.fraction_digits}d}"
            frac_part = f".{frac_text}"

        return base, frac_part, ampm

    def _ns_until_next_boundary(self):
        now_ns = time.time_ns()

        if self.seconds_toggle:
            if self.fraction_digits <= 0:
                step_ns = 1_000_000_000
            else:
                step_ns = 1_000_000_000 // (10 ** self.fraction_digits)
        else:
            step_ns = 60_000_000_000

        if step_ns <= 0:
            step_ns = 1

        next_ns = ((now_ns // step_ns) + 1) * step_ns
        return next_ns - now_ns

    def _ms_until_next_boundary(self):
        remaining_ns = self._ns_until_next_boundary()
        return max(1, int((remaining_ns + 999_999) // 1_000_000))

    def update_datetime(self):
        if self._closed:
            return

        now_dt, frac_ns = self._get_wall_clock_parts()
        date_text = now_dt.strftime("%a, %d %b %Y")
        main_text, frac_text, ampm_text = self._format_time(now_dt, frac_ns)

        if date_text != self._last_date_text:
            self.canvas.itemconfig(self.date_item, text=date_text)
            self._last_date_text = date_text

        if (main_text, frac_text, ampm_text) != self._last_time_text:
            self.canvas.itemconfig(self.time_item, text=main_text)
            self.canvas.itemconfig(self.time_frac_item, text=frac_text)
            self.canvas.itemconfig(self.time_ampm_item, text=ampm_text)

            main_bbox = self.canvas.bbox(self.time_item)

            if main_bbox:
                main_center_y = (main_bbox[1] + main_bbox[3]) / 2

                frac_x = main_bbox[2]
                frac_y = main_center_y + 3

                self.canvas.coords(self.time_frac_item, frac_x, frac_y)

                frac_bbox = self.canvas.bbox(self.time_frac_item)

                if frac_text and frac_bbox:
                    ampm_x = frac_bbox[2] + 2
                else:
                    ampm_x = main_bbox[2] + 3

                ampm_y = main_center_y + 1

                self.canvas.coords(self.time_ampm_item, ampm_x, ampm_y)

            self._last_time_text = (main_text, frac_text, ampm_text)

        if self._time_after_id is not None:
            try:
                self.root.after_cancel(self._time_after_id)
            except tk.TclError:
                pass

        self._time_after_id = self.root.after(self._ms_until_next_boundary(), self.update_datetime)

    def _start_connectivity_thread(self):
        threading.Thread(target=self._connectivity_loop, daemon=True).start()

    def _connectivity_loop(self):
        while not self._stop_event.is_set():
            connected = check_internet()
            with self._lock:
                self._connected = connected
            self._stop_event.wait(2.0)

    def _start_codex_thread(self):
        threading.Thread(target=self._codex_loop, daemon=True).start()

    def _codex_loop(self):
        while not self._codex_stop_event.is_set():
            available, next_dt, status_text = get_codex_status()
            with self._codex_lock:
                self._codex_available = available
                self._codex_next_dt = next_dt
                self._codex_status_text = status_text
            self._codex_stop_event.wait(30.0)

    def update_status(self):
        if self._closed:
            return

        with self._lock:
            connected = self._connected

        color = DOT_ON if connected else DOT_OFF
        label = "ONLINE" if connected else "OFFLINE"

        self.canvas.itemconfig(self.dot_item, fill=color)
        self.canvas.itemconfig(self.status_item, text=label, fill=color)

        self._status_after_id = self.root.after(250, self.update_status)

    def _ensure_audio(self):
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
        except Exception:
            pass

    def _is_alarm_playing(self) -> bool:
        with self._audio_lock:
            return self._alarm_playing

    def _set_alarm_playing(self, value: bool):
        with self._audio_lock:
            self._alarm_playing = value

    def _stop_codex_alarm(self):
        try:
            if pygame.mixer.get_init():
                pygame.mixer.music.stop()
        except Exception:
            pass
        self._set_alarm_playing(False)

    def _play_codex_alarm_worker(self):
        try:
            if not ALARM_SOUND_PATH.is_file():
                self._set_alarm_playing(False)
                return

            self._ensure_audio()
            if not pygame.mixer.get_init():
                self._set_alarm_playing(False)
                return

            pygame.mixer.music.load(str(ALARM_SOUND_PATH))
            pygame.mixer.music.play()
            self._set_alarm_playing(True)

            while pygame.mixer.music.get_busy():
                time.sleep(0.15)

        except Exception:
            pass
        finally:
            self._set_alarm_playing(False)

    def _trigger_codex_alarm(self):
        if self._is_alarm_playing():
            return
        threading.Thread(target=self._play_codex_alarm_worker, daemon=True).start()

    def update_codex_status(self):
        if self._closed:
            return

        with self._codex_lock:
            available = self._codex_available
            next_dt = self._codex_next_dt
            status_text = self._codex_status_text

        if available is True:
            color = TEXT_CODEX_OK
            text = "AVAILABLE"
        elif available is False and next_dt is not None:
            color = TEXT_CODEX_WAIT
            text = f"NEXT {next_dt.strftime('%a %I:%M %p')}"
        else:
            color = TEXT_CODEX_ERR if status_text == "CODEX ERR" else TEXT_CODEX_WAIT
            text = status_text

        self.canvas.itemconfig(self.codex_item, text=text, fill=color)
        self.canvas.itemconfig(
            self.alarm_toggle_item,
            text="ALARM ON" if self.codex_alarm_enabled else "ALARM OFF",
            fill=TEXT_TIME,
        )
        self.canvas.itemconfig(
            self.alarm_toggle_bg,
            fill=BTN_ON if self.codex_alarm_enabled else BTN_OFF,
        )

        if available is not None:
            if self._codex_state_known:
                if (
                    self._previous_known_codex_available is False
                    and available is True
                    and self.codex_alarm_enabled
                ):
                    self._trigger_codex_alarm()
            else:
                self._codex_state_known = True

            self._previous_known_codex_available = available

        if self._codex_after_id is not None:
            try:
                self.root.after_cancel(self._codex_after_id)
            except tk.TclError:
                pass

        self._codex_after_id = self.root.after(1000, self.update_codex_status)

    def _on_close(self):
        self._closed = True
        self._stop_event.set()
        self._codex_stop_event.set()
        self._stop_codex_alarm()

        if self._time_after_id is not None:
            try:
                self.root.after_cancel(self._time_after_id)
            except tk.TclError:
                pass

        if self._status_after_id is not None:
            try:
                self.root.after_cancel(self._status_after_id)
            except tk.TclError:
                pass

        if self._codex_after_id is not None:
            try:
                self.root.after_cancel(self._codex_after_id)
            except tk.TclError:
                pass

        self.root.destroy()


def main():
    root = tk.Tk()
    DateTimeCodexWidget(root, fraction_digits=1)
    root.mainloop()


if __name__ == "__main__":
    main()