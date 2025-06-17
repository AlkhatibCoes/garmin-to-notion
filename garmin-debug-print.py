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

# Dictionary of endpoints to fetch
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
    "User Summary": lambda: garmin.get_user_summary(date_str),
    "Hydration": lambda: garmin.get_hydration_data(date_str),
    "Activities": lambda: garmin.get_activities(date_str, 1)
}

# Run each and print results
for name, func in endpoints.items():
    try:
        print(f"\n== {name} ==")
        data = func()
        print(json.dumps(data, indent=2))
    except Exception as e:
        print(f"⚠️ Failed to fetch {name}: {e}")
