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

def create_sleep_entry(client, database_id, sleep_data):
    daily = sleep_data.get('dailySleepDTO', {})
    hrv = sleep_data.get('hrvSummaryDTO', {})
    stress = sleep_data.get('wellnessDTO', {})

    if not daily or not daily.get('sleepStartTimestampGMT'):
        print("⏭️ Skipping record: missing sleep session data.")
        return

    sleep_date = daily.get('calendarDate', "Unknown Date")
    total_sleep = sum((daily.get(k, 0) or 0) for k in ['deepSleepSeconds', 'lightSleepSeconds', 'remSleepSeconds'])

    if total_sleep == 0:
        print(f"⏭️ Skipping zero sleep day: {sleep_date}")
        return

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
        "Sleep Score": {"number": daily.get('sleepScore', 0)},
        "HRV (ms)": {"number": hrv.get('avg', 0)},
        "HRV Label": {"select": {"name": hrv.get('hrvStatus', {}).get('status', 'No Status')}},
        "Night Stress": {"number": stress.get('sleepStress', 0)}
    }

    try:
        client.pages.create(
            parent={"database_id": database_id},
            properties=properties,
            icon={"emoji": "😴"}
        )
        print(f"✅ Created entry for {sleep_date}")
    except Exception as e:
        print(f"❌ Error creating entry for {sleep_date}: {e}")

def main():
    garmin_email = os.getenv("GARMIN_EMAIL")
    garmin_password = os.getenv("GARMIN_PASSWORD")
    notion_token = os.getenv("NOTION_TOKEN")
    database_id = os.getenv("NOTION_SLEEP_DB_ID")

    garmin = Garmin(garmin_email, garmin_password)
    garmin.login()
    client = Client(auth=notion_token)

    for i in range(5):  # Fetch past 5 days for testing
        date = datetime.today() - timedelta(days=i)
        try:
            data = garmin.get_sleep_data(date.strftime("%Y-%m-%d"))
            if data:
                sleep_date = data.get('dailySleepDTO', {}).get('calendarDate')
                if sleep_date and not sleep_data_exists(client, database_id, sleep_date):
                    create_sleep_entry(client, database_id, data)
        except Exception as e:
            print(f"⚠️ Failed on {date.strftime('%Y-%m-%d')}: {e}")

if __name__ == '__main__':
    main()
