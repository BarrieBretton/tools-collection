import os
import sys
import time
import webbrowser
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo  # Python 3.9+

WORKDAY_URL = "https://wd5.myworkday.com/cvent/d/task/2997$18982.htmld"

IST = ZoneInfo("Asia/Kolkata")
PACIFIC = ZoneInfo("America/Los_Angeles")  # change if your "DST" reference isn't US Pacific


def pacific_is_in_dst(now_ist: datetime) -> bool:
    # Convert "now" into Pacific time and check DST offset
    now_pacific = now_ist.astimezone(PACIFIC)
    return bool(now_pacific.dst() and now_pacific.dst() != timedelta(0))


def next_run_time_ist(now_ist: datetime) -> datetime:
    # Your rule:
    # - 21:30 IST during DST
    # - 21:00 IST otherwise
    if pacific_is_in_dst(now_ist):
        hour, minute = 21, 30
    else:
        hour, minute = 21, 0

    target = now_ist.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if target <= now_ist:
        target += timedelta(days=1)
    return target


def main():
    while True:
        now = datetime.now(IST)
        target = next_run_time_ist(now)
        sleep_seconds = (target - now).total_seconds()

        # Sleep in chunks so it recovers gracefully after laptop sleep/wake
        while sleep_seconds > 0:
            time.sleep(min(300, sleep_seconds))  # 5-min chunks
            now = datetime.now(IST)
            sleep_seconds = (target - now).total_seconds()

        webbrowser.open(WORKDAY_URL, new=2)
        time.sleep(2)  # tiny guard so it doesn't double-fire on edge timing


if __name__ == "__main__":
    main()
