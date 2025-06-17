from garminconnect import Garmin
from dotenv import load_dotenv
from datetime import datetime, timedelta
import os

# Load environment variables
load_dotenv()

# Login to Garmin
garmin = Garmin(os.getenv("GARMIN_EMAIL"), os.getenv("GARMIN_PASSWORD"))
garmin.login()

# Target date: yesterday
date = datetime.today() - timedelta(days=1)
date_str = date.strftime("%Y-%m-%d")
print(f"\n📅 Garmin Data for: {date_str}")

# === 1. Calories & Intensity from correct endpoint ===
try:
    summary = garmin.get_user_summary(date_str)

    print("\n🔥 Calories:")
    print(f"   - Total Calories: {summary.get('calories')} kcal")
    print(f"   - Burned (Total): {summary.get('burnedKilocalories')} kcal")
    print(f"   - Active Calories: {summary.get('activeKilocalories')} kcal")
    print(f"   - BMR (Resting): {summary.get('bmrKilocalories')} kcal")

    print("\n💪 Intensity Minutes:")
    print(f"   - Moderate: {summary.get('moderateIntensityMinutes')} min")
    print(f"   - Vigorous: {summary.get('vigorousIntensityMinutes')} min")

except Exception as e:
    print(f"⚠️ Error fetching user summary: {e}")

# === 2. Hydration ===
try:
    hydration = garmin.get_hydration_data(date_str)
    print("\n💧 Hydration:")
    print(f"   - Total: {hydration.get('totalHydration')} mL")
except Exception as e:
    print(f"⚠️ Error fetching hydration: {e}")
