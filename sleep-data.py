from datetime import datetime, timedelta
from garminconnect import Garmin
from notion_client import Client
from dotenv import load_dotenv
import pytz
import os

# Load environment variables
load_dotenv()

# Timezone setup
local_tz = pytz.timezone("Europe/Berlin")

# Helper functions
def format_duration(seconds):
    minutes = (seconds or 0) // 60
    return f"{minutes // 60}h {minutes % 60}m"

def format_time(timestamp):
    return datetime.utcfromtimestamp(timestamp / 1000).strftime("%Y-%m-%dT%H:%M:%S.000Z") if timestamp else None

def format_time_readable(timestamp):
    return datetime.fromtimestamp(timestamp / 1000, local_tz).strftime("%H:%M") if timestamp else "Unknown"

def format_date_for_name(date):
    return datetime.strptime(date, "%Y-%m-%d").strftime("%d.%m.%Y") if date else "Unknown"

def sleep_data_exists(client, database_id, sleep_date):
    query = client.databases.query(
        database_id=database_id,
        filter={"property": "Long Date", "date": {"equals": sleep_date}}
    )
    results = query.get('results', [])
    return results[0] if results else None

def create_sleep_entry(client, database_id, sleep_data, yesterday_stress=None, summary=None, hydration_ml=None, weight_kg=None, avg_rhr_7d=None):
    daily = sleep_data.get('dailySleepDTO', {})

    if not daily or not daily.get('sleepStartTimestampGMT'):
        return

    sleep_date = daily.get('calendarDate', "Unknown Date")
    total_sleep = sum((daily.get(k, 0) or 0) for k in ['deepSleepSeconds', 'lightSleepSeconds', 'remSleepSeconds'])

    if total_sleep == 0:
        return

    # Calories & intensity minutes
    total_kcal = summary.get('totalKilocalories') if summary else None
    consumed_kcal = summary.get('consumedKilocalories') if summary else None
    active_kcal = summary.get('activeKilocalories') if summary else None
    mod_min = summary.get('moderateIntensityMinutes') if summary else None
    vig_min = summary.get('vigorousIntensityMinutes') if summary else None

    if total_kcal is not None and consumed_kcal is not None:
        calorie_balance = consumed_kcal - total_kcal
        calorie_percent = round(abs(calorie_balance) / total_kcal * 100)
    else:
        calorie_balance = None
        calorie_percent = None

    properties = {
        "Date": {"title": [{"text": {"content": format_date_for_name(sleep_date)}}]},
        "Times": {"rich_text": [{"text": {"content": f"{format_time_readable(daily.get('sleepStartTimestampGMT'))} → {format_time_readable(daily.get('sleepEndTimestampGMT'))}"}}]},
        "Long Date": {"date": {"start": sleep_date}},
        "Full Date/Time": {"date": {"start": format_time(daily.get('sleepStartTimestampGMT')), "end": format_time(daily.get('sleepEndTimestampGMT'))}},
        "Total Sleep (h)": {"number": round(total_sleep / 3600, 1)},
        "Light Sleep (h)": {"number": round(daily.get('lightSleepSeconds', 0) / 3600, 1)},
        "Deep Sleep (h)": {"number": round(daily.get('deepSleepSeconds', 0) / 3600, 1)},
        "REM Sleep (h)": {"number": round(daily.get('remSleepSeconds', 0) / 3600, 1)},
        "Awake Time (h)": {"number": round(daily.get('awakeSleepSeconds', 0) / 3600, 1)},
        "Total Sleep": {"rich_text": [{"text": {"content": format_duration(total_sleep)}}]},
        "Light Sleep": {"rich_text": [{"text": {"content": format_duration(daily.get('lightSleepSeconds', 0))}}]},
        "Deep Sleep": {"rich_text": [{"text": {"content": format_duration(daily.get('deepSleepSeconds', 0))}}]},
        "REM Sleep": {"rich_text": [{"text": {"content": format_duration(daily.get('remSleepSeconds', 0))}}]},
        "Awake Time": {"rich_text": [{"text": {"content": format_duration(daily.get('awakeSleepSeconds', 0))}}]},
        "Resting HR": {"number": sleep_data.get('restingHeartRate', 0)},
        "Sleep Score": {"number": daily.get('sleepScores', {}).get('overall', {}).get('value', 0)},
        "HRV (ms)": {"number": sleep_data.get('avgOvernightHrv', 0)},
        "HRV Label": {"select": {"name": sleep_data.get('hrvStatus', "No Status")}},
        "Night Stress": {"number": daily.get('avgSleepStress', 0)},
        "Yesterdays Stress": {"number": yesterday_stress or 0},
        "Total Calories": {"number": total_kcal},
        "Consumed Calories": {"number": consumed_kcal},
        "Active Calories": {"number": active_kcal},
        "Calorie Balance": {"number": calorie_balance},
        "Calorie Deficit %": {"number": calorie_percent},
        "Moderate Intensity Min": {"number": mod_min},
        "Vigorous Intensity Min": {"number": vig_min},
        "Hydration (ml)": {"number": hydration_ml},
        "Weight (kg)": {"number": weight_kg},
        "7-Day Avg Resting HR": {"number": avg_rhr_7d},
    }

    try:
        client.pages.create(
            parent={"database_id": database_id},
            properties=properties,
            icon={"emoji": "🛌"}
        )
    except Exception as e:
        print(f"❌ Error creating entry for {sleep_date}: {e}")

def main():
    garmin = Garmin(os.getenv("GARMIN_EMAIL"), os.getenv("GARMIN_PASSWORD"))
    garmin.login()
    client = Client(auth=os.getenv("NOTION_TOKEN"))
    database_id = os.getenv("NOTION_SLEEP_DB_ID")

    date = datetime.today() - timedelta(days=1)
    date_str = date.strftime("%Y-%m-%d")
    yesterday = date - timedelta(days=1)

    try:
        sleep_data = garmin.get_sleep_data(date_str)
        stress_data = garmin.get_stress_data(yesterday.strftime("%Y-%m-%d"))
        yesterday_stress = stress_data.get("avgStressLevel", 0)

        summary = garmin.get_user_summary(date_str)
        hydration = garmin.get_hydration_data(date_str)
        hydration_ml = hydration.get("valueInML")

        heart_data = garmin.get_heart_rates(date_str)
        avg_rhr_7d = heart_data.get("lastSevenDaysAvgRestingHeartRate")

        body_data = garmin.get_body_composition(date_str, date_str)
        weight_kg = body_data[0].get("weight") / 1000 if isinstance(body_data, list) and body_data else None

        if sleep_data:
            sleep_date = sleep_data.get("dailySleepDTO", {}).get("calendarDate")
            if sleep_date and not sleep_data_exists(client, database_id, sleep_date):
                create_sleep_entry(client, database_id, sleep_data, yesterday_stress, summary, hydration_ml, weight_kg, avg_rhr_7d)

    except Exception as e:
        print(f"⚠️ Failed on {date_str}: {e}")

if __name__ == '__main__':
    main()


