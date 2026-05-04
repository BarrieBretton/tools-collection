"""
Simple alarm module with importable API and CLI support.

Examples:
    python alarm.py 07 30
    python alarm.py 07 30 15 --sound "/path/to/file.mp3" --label "Standup"

Import usage:
    from pathlib import Path
    from datetime import datetime
    from alarm import AlarmConfig, set_alarm, set_alarm_at

    set_alarm(AlarmConfig(hour=7, minute=30, label="Wake up"))

    set_alarm_at(
        target=datetime(2026, 5, 8, 13, 42, 35),
        sound_path=Path("/path/to/file.mp3"),
        label="Codex reset",
    )
"""

from __future__ import annotations

import argparse
import os
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"

import pygame


DEFAULT_SOUND_PATHS = {
    "linux": Path("/media/vivojay/VIVOSANDISK/VIVAN/MUSIC/dl-songs/MarianaPlayer/alayna - Sugar [Official Audio].mp3"),
    "win32": Path(r"C:\Users\Vivo Jay\Music\MarianaPlayer\Chymes - Enemy.mp3"),
}


class AlarmError(RuntimeError):
    """Raised when alarm configuration is invalid."""


@dataclass(slots=True)
class AlarmConfig:
    hour: int
    minute: int = 0
    second: int = 0
    sound_path: Optional[Path] = None
    label: str = ""

    def validate(self) -> None:
        if not (0 <= self.hour <= 23):
            raise AlarmError("Hour must be between 0 and 23.")
        if not (0 <= self.minute <= 59):
            raise AlarmError("Minute must be between 0 and 59.")
        if not (0 <= self.second <= 59):
            raise AlarmError("Second must be between 0 and 59.")

        if self.sound_path is not None and not self.sound_path.is_file():
            raise AlarmError(f"Invalid alarm sound path: {self.sound_path}")

    @property
    def target_today(self) -> datetime:
        now = datetime.now().astimezone()
        return now.replace(
            hour=self.hour,
            minute=self.minute,
            second=self.second,
            microsecond=0,
        )


def get_default_sound_path() -> Optional[Path]:
    return DEFAULT_SOUND_PATHS.get(sys.platform)


def initialize_audio() -> None:
    if not pygame.mixer.get_init():
        pygame.mixer.init()


def format_timedelta(delta: timedelta) -> str:
    total_seconds = max(0, int(delta.total_seconds()))
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02d}h {minutes:02d}m {seconds:02d}s"


def play_sound(sound_path: Path) -> None:
    initialize_audio()

    print("\nAlarm Activated")
    print(f"Playing: {sound_path}")

    pygame.mixer.music.load(str(sound_path))
    pygame.mixer.music.play()

    try:
        while pygame.mixer.music.get_busy():
            time.sleep(0.2)
    except KeyboardInterrupt:
        pygame.mixer.music.stop()
        print("Stopped Alarm")


def wait_until(target: datetime) -> None:
    now = datetime.now(target.tzinfo) if target.tzinfo else datetime.now()

    if target <= now:
        raise AlarmError(f"Alarm time has already passed: {target}")

    wait_duration = target - now

    print(
        f"Alarm set for {target.strftime('%Y-%m-%d %H:%M:%S %Z')} "
        f"({target.strftime('%I:%M:%S %p')})"
    )
    print(f"Alarm goes off in: {format_timedelta(wait_duration)}")
    print()

    try:
        while True:
            now = datetime.now(target.tzinfo) if target.tzinfo else datetime.now()
            remaining = (target - now).total_seconds()
            if remaining <= 0:
                break
            time.sleep(min(0.5, max(0.1, remaining)))
    except KeyboardInterrupt:
        raise AlarmError("Skipped Alarm") from None


def set_alarm(config: AlarmConfig) -> None:
    if config.sound_path is None:
        config.sound_path = get_default_sound_path()

    config.validate()

    target = config.target_today

    print(f"Label: {config.label}" if config.label.strip() else "[NO LABEL]")
    wait_until(target)

    if config.label.strip():
        print(config.label)

    play_sound(config.sound_path)


def set_alarm_at(target: datetime, sound_path: Path | str | None = None, label: str = "") -> None:
    if sound_path is None:
        resolved_sound_path = get_default_sound_path()
    else:
        resolved_sound_path = Path(sound_path)

    if resolved_sound_path is None:
        raise AlarmError("Alarm sound has not been set.")

    if not resolved_sound_path.is_file():
        raise AlarmError(f"Invalid alarm sound path: {resolved_sound_path}")

    print(f"Label: {label}" if label.strip() else "[NO LABEL]")
    wait_until(target)

    if label.strip():
        print(label)

    play_sound(resolved_sound_path)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="alarm",
        description="Set an alarm for today using hour, minute, and optional second.",
    )
    parser.add_argument("hour", type=int, help="Hour in 24-hour format (0-23)")
    parser.add_argument("minute", nargs="?", type=int, default=0, help="Minute (0-59)")
    parser.add_argument("second", nargs="?", type=int, default=0, help="Second (0-59)")
    parser.add_argument("--sound", type=Path, default=None, help="Path to the alarm sound file")
    parser.add_argument("--label", default="", help="Optional alarm label/description")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    config = AlarmConfig(
        hour=args.hour,
        minute=args.minute,
        second=args.second,
        sound_path=args.sound,
        label=args.label,
    )

    try:
        set_alarm(config)
    except AlarmError as exc:
        parser.exit(status=1, message=f"Error: {exc}\n")
    except pygame.error as exc:
        parser.exit(status=1, message=f"Audio error: {exc}\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())