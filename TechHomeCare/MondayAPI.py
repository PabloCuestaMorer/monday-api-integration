import os
import requests
import json
from dotenv import load_dotenv
import boto3

# Load environment variables
load_dotenv()

# Retrieve the API key from the environment variable
api_key = os.getenv("MONDAY_API_KEY")
if not api_key:
    print("API key is not set. Check your .env file.")
else:
    print("API Key loaded successfully.")

# Retrieve the AWS variables
aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
aws_region = os.getenv("AWS_DEFAULT_REGION")

if not aws_access_key_id or not aws_secret_access_key or not aws_region:
    print("AWS credentials are not set. Check your .env file.")
else:
    print("AWS credentials loaded successfully.")

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
    """Fetches and formats all items from a specified board using items_page for pagination."""
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
            if column_def["type"] == "formula":
                # Instead of evaluating, insert the literal formula string
                formula_str = json.loads(column_def["settings_str"]).get("formula", "")
                row[column_def["title"]] = f"Formula: {formula_str}"
            else:
                row[column_def["title"]] = column["text"]
        formatted_rows.append(row)

    return formatted_rows


def update_user_subscription(board_id, item_id, new_status):
    """Update the subscription status of a user in Monday.com."""
    query = """
        mutation ($boardId: ID!, $itemId: ID!, $columnId: String!, $value: String!) {
            change_simple_column_value(
                board_id: $boardId,
                item_id: $itemId,
                column_id: $columnId,
                value: $value
            ) {
                id
            }
        }
    """
    variables = {
        "boardId": str(board_id),
        "itemId": str(item_id),
        "columnId": "estado__1",
        "value": new_status
    }
    data = {"query": query, "variables": json.dumps(variables)}
    response = requests.post(api_url, headers=headers, json=data)
    return response.json()



# Initialize the SNS client
sns_client = boto3.client(
    'sns',
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    region_name=aws_region
)
sns_client = boto3.client('sns')

def send_sms(phone_number, message):
    """Send an SMS to a specified phone number using AWS SNS."""
    response = sns_client.publish(
        PhoneNumber=phone_number,
        Message=message
    )
    return response