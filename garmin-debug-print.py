from garminconnect import Garmin
from dotenv import load_dotenv
from datetime import datetime, timedelta
import os
import json

load_dotenv()

garmin = Garmin(os.getenv("GARMIN_EMAIL"), os.getenv("GARMIN_PASSWORD"))
garmin.login()

# Change date range as needed
for days_ago in range(3):
    date = datetime.today() - timedelta(days=days_ago)
    date_str = date.strftime("%Y-%m-%d")
    print(f"\n📅 Debugging Garmin data for: {date_str}")

    try:
        print("\n== Sleep Data ==")
        print(json.dumps(garmin.get_sleep_data(date_str), indent=2))

        print("\n== Wellness Data ==")
        print(json.dumps(garmin.get_wellness_data(date_str), indent=2))

        print("\n== Stress Data ==")
        print(json.dumps(garmin.get_stress_data(date_str), indent=2))

        print("\n== Body Battery Data ==")
        print(json.dumps(garmin.get_body_battery_data(date_str), indent=2))

    except Exception as e:
        print(f"⚠️ Error fetching data for {date_str}: {e}")
