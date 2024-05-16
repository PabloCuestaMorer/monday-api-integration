import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Retrieve the API key from the environment variable
api_key = os.getenv("MONDAY_API_KEY")
if not api_key:
    print("API key is not set. Check your .env file.")
else:
    print("API Key loaded successfully.")

# API setup
api_url = "https://api.monday.com/v2"
headers = {
    "Authorization": api_key,
    "Content-Type": "application/json",
    "API-Version": "2023-04",
}


def fetch_board_details(board_id):
    """Fetches board details including column definitions."""
    query = """
        query ($boardIds: [ID!]) {
            boards (ids: $boardIds) {
                name
                columns {
                    id
                    title
                    type
                    settings_str
                }
            }
        }
    """
    variables = json.dumps({"boardIds": [str(board_id)]})
    data = {"query": query, "variables": variables}
    response = requests.post(url=api_url, headers=headers, json=data)
    return response.json()


def fetch_items(board_id, username=None):
    """Fetches and formats all items from a specified board using items_page for pagination.
       If username is provided, it fetches only the data for that user.
    """
    board_data = fetch_board_details(board_id)
    if "errors" in board_data:
        print("Error fetching board details:", board_data["errors"])
        return []

    col_defs = {col["id"]: col for col in board_data["data"]["boards"][0]["columns"]}

    query = """
        query ($boardId: ID!) {
            boards (ids: [$boardId]) {
                items_page (limit: 100) {  # Fetch up to 100 items; adjust as needed
                    items {
                        id
                        name
                        column_values {
                            id
                            text
                            value
                        }
                    }
                }
            }
        }
    """
    variables = json.dumps({"boardId": str(board_id)})
    data = {"query": query, "variables": variables}
    response = requests.post(url=api_url, headers=headers, json=data)
    items_data = response.json()
    if "errors" in items_data:
        print("Error fetching items:", items_data["errors"])
        return []

    items = items_data["data"]["boards"][0]["items_page"]["items"]
    formatted_rows = []

    for item in items:
        if username and item["name"] != username:
            continue
        row = {"id": item["id"], "name": item["name"]}
        for column in item["column_values"]:
            column_def = col_defs.get(column["id"], {})
            row[column_def.get("title", column["id"])] = column["text"]
        formatted_rows.append(row)

    return formatted_rows
