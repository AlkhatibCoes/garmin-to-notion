from garminconnect import Garmin
from dotenv import load_dotenv
from datetime import datetime, timedelta
import os

# Load environment variables (email, password)
load_dotenv()

# Login to Garmin
garmin = Garmin(os.getenv("GARMIN_EMAIL"), os.getenv("GARMIN_PASSWORD"))
garmin.login()

# Target date: yesterday
date = datetime.today() - timedelta(days=1)
date_str = date.strftime("%Y-%m-%d")
print(f"\n📅 Garmin Data for: {date_str}")

# === 1. Total Calories & Intensity Minutes ===
try:
    stats = garmin.get_stats(date_str)
    total_calories = stats.get("calories")
    burned_kcal = stats.get("burnedKilocalories")
    active_kcal = stats.get("activeKilocalories")
    bmr_kcal = stats.get("bmrKilocalories")
    moderate_minutes = stats.get("moderateIntensityMinutes")
    vigorous_minutes = stats.get("vigorousIntensityMinutes")

    print("\n🔥 Calories:")
    print(f"   - Total Calories: {total_calories} kcal")
    print(f"   - Burned (Total): {burned_kcal} kcal")
    print(f"   - Active Calories: {active_kcal} kcal")
    print(f"   - BMR (Resting): {bmr_kcal} kcal")

    print("\n💪 Intensity Minutes:")
    print(f"   - Moderate: {moderate_minutes} min")
    print(f"   - Vigorous: {vigorous_minutes} min")

except Exception as e:
    print(f"⚠️ Error fetching stats: {e}")

# === 2. Hydration ===
try:
    hydration = garmin.get_hydration_data(date_str)
    total_hydration = hydration.get("totalHydration")
    print("\n💧 Hydration:")
    print(f"   - Total: {total_hydration} mL")

except Exception as e:
    print(f"⚠️ Error fetching hydration: {e}")
