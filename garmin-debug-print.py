from garminconnect import Garmin
from dotenv import load_dotenv
from datetime import datetime, timedelta
import os
import json

# Load credentials
load_dotenv()
garmin = Garmin(os.getenv("GARMIN_EMAIL"), os.getenv("GARMIN_PASSWORD"))
garmin.login()

# Set target date (yesterday)
date = datetime.today() - timedelta(days=1)
date_str = date.strftime("%Y-%m-%d")
print(f"\n📅 Garmin Debug Data for: {date_str}")

# List of Garmin endpoints to test
endpoints = {
    "Steps": lambda: garmin.get_steps_data(date_str),
    "Daily Summary Stats": lambda: garmin.get_stats(date_str),
    "Heart Rate": lambda: garmin.get_heart_rates(date_str),
    "Sleep": lambda: garmin.get_sleep_data(date_str),
    "Stress": lambda: garmin.get_stress_data(date_str),
    "Body Battery": lambda: garmin.get_body_battery_data(date_str),
    "Respiration": lambda: garmin.get_respiration_data(date_str),
    "HRV": lambda: garmin.get_hrv_data(date_str),
    "Pulse Ox": lambda: garmin.get_pulseox_data(date_str),
    "Wellness": lambda: garmin.get_wellness_data(date_str),
    "User Summary": lamb

