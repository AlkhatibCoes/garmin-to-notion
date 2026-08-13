import os
import json
from datetime import datetime
from zoneinfo import ZoneInfo

from garminconnect import Garmin

# ---------------------------------------------------------
# CONFIG
# ---------------------------------------------------------

GARMIN_EMAIL = os.environ["GARMIN_EMAIL"]
GARMIN_PASSWORD = os.environ["GARMIN_PASSWORD"]

BERLIN = ZoneInfo("Europe/Berlin")
now = datetime.now(BERLIN)
today = now.date().isoformat()


# ---------------------------------------------------------
# LOGIN
# ---------------------------------------------------------

print(f"Connecting to Garmin for {today}...")

client = Garmin(GARMIN_EMAIL, GARMIN_PASSWORD)
client.login()

print("Garmin login successful.")


# ---------------------------------------------------------
# FETCH DATA
# ---------------------------------------------------------

stats = client.get_stats(today)
sleep = client.get_sleep_data(today)
hrv = client.get_hrv_data(today)
stress = client.get_stress_data(today)
steps_data = client.get_steps_data(today)


# ---------------------------------------------------------
# SAFE DEBUG OUTPUT
#
# We deliberately print only useful Garmin health data,
# never credentials or authentication tokens.
# ---------------------------------------------------------

print("\n==============================")
print("DAILY STATS")
print("==============================")

interesting_stats = {
    "calendarDate": stats.get("calendarDate"),
    "totalSteps": stats.get("totalSteps"),
    "totalKilocalories": stats.get("totalKilocalories"),
    "restingHeartRate": stats.get("restingHeartRate"),
    "averageStressLevel": stats.get("averageStressLevel"),
    "maxStressLevel": stats.get("maxStressLevel"),
}

print(json.dumps(interesting_stats, indent=2))


print("\n==============================")
print("SLEEP")
print("==============================")

daily_sleep = sleep.get("dailySleepDTO", {}) if isinstance(sleep, dict) else {}

interesting_sleep = {
    "sleepScore": (
        daily_sleep.get("sleepScores", {})
        .get("overall", {})
        .get("value")
    ),
    "sleepStartTimestampGMT": daily_sleep.get("sleepStartTimestampGMT"),
    "sleepEndTimestampGMT": daily_sleep.get("sleepEndTimestampGMT"),
}

print(json.dumps(interesting_sleep, indent=2))


print("\n==============================")
print("HRV")
print("==============================")

if isinstance(hrv, dict):
    interesting_hrv = {
        "weeklyAvg": hrv.get("weeklyAvg"),
        "lastNightAvg": hrv.get("lastNightAvg"),
        "lastNight5MinHigh": hrv.get("lastNight5MinHigh"),
        "hrvStatus": hrv.get("hrvStatus"),
    }
else:
    interesting_hrv = {"raw": hrv}

print(json.dumps(interesting_hrv, indent=2))


print("\n==============================")
print("STRESS - KEYS")
print("==============================")

if isinstance(stress, dict):
    print(sorted(stress.keys()))

    stress_summary = {
        key: stress.get(key)
        for key in [
            "overallStressLevel",
            "averageStressLevel",
            "maxStressLevel",
            "stressChartValueOffset",
            "stressChartYAxisOrigin",
        ]
        if key in stress
    }

    print("\nStress summary:")
    print(json.dumps(stress_summary, indent=2))

else:
    print(type(stress).__name__)


print("\n==============================")
print("STEPS DATA - SAMPLE")
print("==============================")

if isinstance(steps_data, list):
    print(f"Number of step records: {len(steps_data)}")

    # Only print a few records so GitHub logs stay readable.
    print(json.dumps(steps_data[:5], indent=2))
else:
    print(type(steps_data).__name__)
    print(json.dumps(steps_data, indent=2))


print("\n==============================")
print("TEST COMPLETE")
print("==============================")
