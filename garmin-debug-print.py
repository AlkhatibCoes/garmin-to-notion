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

    total_kcal = summary.get('totalKilocalories')
    consumed_kcal = summary.get('consumedKilocalories')
    active_kcal = summary.get('activeKilocalories')
    mod_min = summary.get('moderateIntensityMinutes')
    vig_min = summary.get('vigorousIntensityMinutes')

    # Calculate absolute and % calorie balance
    if total_kcal is not None and consumed_kcal is not None:
        calorie_balance = consumed_kcal - total_kcal
        calorie_percent = round(abs(calorie_balance) / total_kcal * 100)
    else:
        calorie_balance = None
        calorie_percent = None

    print("\n🔥 Calories:")
    print(f"   - Total Calories Burned: {total_kcal} kcal")
    print(f"   - Consumed Calories: {consumed_kcal} kcal")
    print(f"   - Active Calories: {active_kcal} kcal")

    if calorie_balance is not None and calorie_percent is not None:
        label = "Surplus" if calorie_balance > 0 else "Deficit"
        print(f"   - Calorie {label}: {abs(calorie_balance)} kcal ({calorie_percent}%)")
    else:
        print("   - Calorie Balance: Not available")

    print("\n💪 Intensity Minutes:")
    print(f"   - Moderate: {mod_min} min")
    print(f"   - Vigorous: {vig_min} min")

except Exception as e:
    print(f"⚠️ Error fetching user summary: {e}")

# === Hydration ===
try:
    hydration = garmin.get_hydration_data(date_str)
    hydration_ml = hydration.get("valueInML")
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
