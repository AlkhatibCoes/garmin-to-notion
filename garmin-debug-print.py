from garminconnect import Garmin
from dotenv import load_dotenv
from datetime import datetime, timedelta
import os

# Load credentials
load_dotenv()
garmin = Garmin(os.getenv("GARMIN_EMAIL"), os.getenv("GARMIN_PASSWORD"))
garmin.login()

# Target date: yesterday
date = datetime.today() - timedelta(days=1)
date_str = date.strftime("%Y-%m-%d")
print(f"\n📅 Garmin Data for: {date_str}")

# === Summary Data ===
try:
    summary = garmin.get_user_summary(date_str)

    print("\n🔥 Calories:")
    print(f"   - Total Calories Burned: {summary.get('totalKilocalories')} kcal")
    print(f"   - Wellness Calories: {summary.get('wellnessKilocalories')} kcal")
    print(f"   - Consumed Calories: {summary.get('consumedKilocalories')} kcal")
    print(f"   - Remaining Calories: {summary.get('remainingKilocalories')} kcal")
    print(f"   - Active Calories: {summary.get('activeKilocalories')} kcal")
    print(f"   - BMR (Resting): {summary.get('bmrKilocalories')} kcal")

    print("\n💪 Intensity Minutes:")
    print(f"   - Moderate: {summary.get('moderateIntensityMinutes')} min")
    print(f"   - Vigorous: {summary.get('vigorousIntensityMinutes')} min")

except Exception as e:
    print(f"⚠️ Error fetching user summary: {e}")

# === Hydration Data ===
try:
    hydration = garmin.get_hydration_data(date_str)
    hydration_ml = hydration.get("totalHydration")
    print("\n💧 Hydration:")
    print(f"   - Total: {hydration_ml if hydration_ml is not None else 'No hydration data found'} mL")
except Exception as e:
    print(f"⚠️ Error fetching hydration: {e}")

# === 7-Day Avg Resting Heart Rate ===
try:
    hr = garmin.get_heart_rates(date_str)
    avg_rhr_7d = hr.get("lastSevenDaysAvgRestingHeartRate")
    print("\n❤️ 7-Day Avg Resting HR:")
    print(f"   - {avg_rhr_7d} bpm")
except Exception as e:
    print(f"⚠️ Error fetching heart rate data: {e}")
