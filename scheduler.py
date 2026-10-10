import os
import sys
import time
import urllib.parse
from datetime import datetime, timedelta, time as dtime
import ctypes
import pyautogui
from dotenv import load_dotenv

load_dotenv()

PHONE_NUMBER = os.getenv("TARGET_PHONE_NUMBER")
MESSAGE = os.getenv("MESSAGE_TEXT", "Hello! This is a scheduled message.")
SCHEDULE_MODE = os.getenv("SCHEDULE_MODE", "once").strip().lower()

if not PHONE_NUMBER:
    raise ValueError("TARGET_PHONE_NUMBER is missing in .env.")

user32 = ctypes.windll.user32


def is_whatsapp_running() -> bool:
    hwnd = user32.FindWindowW(None, "WhatsApp")
    return hwnd != 0


def send_whatsapp_message(phone: str, text: str):
    prev_hwnd = user32.GetForegroundWindow()
    was_open = is_whatsapp_running()

    encoded_text = urllib.parse.quote(text)
    clean_phone = phone.replace("+", "").replace(" ", "").replace("-", "")
    os.system(f'start whatsapp://send?phone={clean_phone}^&text={encoded_text}')

    # Wait for the chat to load and text box to focus
    time.sleep(2.5)

    # Dispatch message
    pyautogui.press("enter")
    time.sleep(0.3)

    # Restore prior window state
    if not was_open:
        pyautogui.hotkey("win", "down")
    else:
        if prev_hwnd and prev_hwnd != user32.GetForegroundWindow():
            user32.SetForegroundWindow(prev_hwnd)
        else:
            pyautogui.hotkey("ctrl", "tab")


def run_once_mode():
    target_dt_str = os.getenv("SCHEDULE_DATETIME")
    if not target_dt_str:
        raise ValueError("SCHEDULE_DATETIME must be set in .env for 'once' mode.")

    try:
        target_dt = datetime.strptime(target_dt_str.strip(), "%Y-%m-%d %H:%M")
    except ValueError:
        raise ValueError("Invalid SCHEDULE_DATETIME format. Use 'YYYY-MM-DD HH:MM'.")

    now = datetime.now()
    delay_seconds = (target_dt - now).total_seconds()

    if delay_seconds < 0:
        print(f"Error: The scheduled time ({target_dt}) is in the past.")
        sys.exit(1)

    print("=" * 60)
    print("WhatsApp Desktop Scheduler [Mode: ONCE]")
    print(f"Recipient: {PHONE_NUMBER}")
    print(f"Message:   {MESSAGE}")
    print(f"Scheduled: {target_dt:%Y-%m-%d %H:%M}")
    print(f"Waiting:   {delay_seconds / 3600:.2f} hours ({int(delay_seconds)} seconds)")
    print("=" * 60)

    time.sleep(delay_seconds)

    print(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] Time reached. Dispatching message...")
    send_whatsapp_message(PHONE_NUMBER, MESSAGE)
    print("Message dispatched successfully. Exiting scheduler.")


def run_recurring_mode():
    interval_hours = float(os.getenv("INTERVAL_HOURS", "2"))
    interval_seconds = interval_hours * 3600

    start_str = os.getenv("WINDOW_START_TIME", "05:30").split(":")
    end_str = os.getenv("WINDOW_END_TIME", "20:00").split(":")
    window_start = dtime(int(start_str[0]), int(start_str[1]))
    window_end = dtime(int(end_str[0]), int(end_str[1]))

    def in_window(now):
        return window_start <= now.time() < window_end

    def seconds_until_start(now):
        target = datetime.combine(now.date(), window_start)
        if now >= target:
            target += timedelta(days=1)
        return (target - now).total_seconds()

    print("=" * 60)
    print("WhatsApp Desktop Scheduler [Mode: RECURRING]")
    print(f"Recipient:     {PHONE_NUMBER}")
    print(f"Active Window: {window_start.strftime('%H:%M')} - {window_end.strftime('%H:%M')}")
    print(f"Interval:      Every {interval_hours} hour(s)")
    print("=" * 60)

    while True:
        now = datetime.now()

        if not in_window(now):
            wait = seconds_until_start(now)
            print(f"[{now:%Y-%m-%d %H:%M:%S}] Outside active window. Sleeping until {window_start}...")
            time.sleep(wait)
            continue

        try:
            print(f"[{now:%Y-%m-%d %H:%M:%S}] Dispatching message...")
            send_whatsapp_message(PHONE_NUMBER, MESSAGE)
            print(f"Sent. Sleeping for {interval_hours} hour(s)...")
            time.sleep(interval_seconds)

        except Exception as e:
            print(f"An error occurred: {e}")
            time.sleep(60)


if __name__ == "__main__":
    if SCHEDULE_MODE == "once":
        run_once_mode()
    elif SCHEDULE_MODE == "recurring":
        run_recurring_mode()
    else:
        print(f"Invalid SCHEDULE_MODE '{SCHEDULE_MODE}'. Use 'once' or 'recurring'.")