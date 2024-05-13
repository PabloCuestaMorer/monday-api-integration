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
    variables = json.dumps({'boardIds': [str(board_id)]})
    data = {'query': query, 'variables': variables}
    response = requests.post(url=api_url, headers=headers, json=data)
    return response.json()


def format_item_value(column_type, settings_str, value):
    """Formats an item value based on the column type."""
    if value is None:
        return ""

    settings = json.loads(settings_str or "{}")

    if column_type == "text" or column_type == "long-text":
        return value.strip()
    elif column_type == "numeric":
        return value
    elif column_type == "date":
        return json.loads(value)["date"]
    elif column_type == "color":
        labels = settings["labels"]
        return labels[str(json.loads(value)["index"])]
    elif column_type == "dropdown":
        labels = settings["labels"]
        label_map = {row["id"]: row["name"] for row in labels}
        return ", ".join([label_map[id] for id in json.loads(value)["ids"]])
    else:
        return value  # Default formatter


def fetch_and_format_items(board_id):
    """Fetches and formats all items from a specified board using items_page for pagination."""
    board_data = fetch_board_details(board_id)
    if 'errors' in board_data:
        print("Error fetching board details:", board_data['errors'])
        return []

    col_defs = {col['id']: col for col in board_data['data']['boards'][0]['columns']}
    
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
    variables = json.dumps({'boardId': str(board_id)})
    data = {'query': query, 'variables': variables}
    response = requests.post(url=api_url, headers=headers, json=data)
    items_data = response.json()
    if 'errors' in items_data:
        print("Error fetching items:", items_data['errors'])
        return []

    items = items_data['data']['boards'][0]['items_page']['items']
    formatted_rows = []

    for item in items:
        row = {'id': item['id'], 'name': item['name']}
        for column in item['column_values']:
            column_def = col_defs.get(column['id'], {})
            formatted_value = format_item_value(
                column_def.get('type', 'text'),  # Default to text if type is not found
                column_def.get('settings_str', '{}'),
                column['value']
            )
            row[column_def.get('title', column['id'])] = formatted_value  # Default to column ID if title is not found
        formatted_rows.append(row)

    return formatted_rows