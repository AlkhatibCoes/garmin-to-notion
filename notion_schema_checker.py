import os
from notion_client import Client
from dotenv import load_dotenv
import json

# Load Notion token and database ID
load_dotenv()
notion_token = os.getenv("NOTION_TOKEN")
database_id = os.getenv("NOTION_SLEEP_DB_ID")

# Initialize Notion client
client = Client(auth=notion_token)

# Fetch and display the database schema
try:
    response = client.databases.retrieve(database_id=database_id)
    print("\n📘 Notion Database Schema:")
    for prop_name, prop in response['properties'].items():
        prop_type = prop['type']
        print(f"- {prop_name}: {prop_type}")
except Exception as e:
    print("❌ Failed to fetch schema:", e)
