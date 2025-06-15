from datetime import datetime, timedelta
from garminconnect import Garmin
from dotenv import load_dotenv
import os
import json

# Load environment variables
load_dotenv()

def main():
    garmin_email = os.getenv("GARMIN_EMAIL")
    garmin_password = os.getenv("GARMIN_PASSWORD")

    # Authenticate with Garmin
    garmin = Garmin(garmin_email, garmin_password)
    garmin.login()

    # Target date (yesterday for consistency with sleep reporting)
    target_date = (datetime.today() - timedelta(days=1)).strftime("%Y-%m-%d")

    print("\n== Raw Garmin Sleep Data ==")
    try:
        sleep_data = garmin.get_sleep_data(target_date)
        print(json.dumps(sleep_data, indent=2))
    except Exception as e:
        print(f"⚠️ Error fetching sleep data: {e}")

    print("\n== Raw Garmin Stress Data ==")
    try:
        stress_data = garmin.get_stress_data(target_date)
        print(json.dumps(stress_data, indent=2))
    except Exception as e:
        print(f"⚠️ Error fetching stress data: {e}")

if __name__ == '__main__':
    main()
