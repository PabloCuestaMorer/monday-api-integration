import os
from dotenv import load_dotenv
from monday import MondayClient

# Load environment variables
load_dotenv()

# Retrieve the API key from the environment variable
api_key = os.getenv("MONDAY_API_KEY")

# Make sure the API key is correctly retrieved
if api_key is None:
    print("API key is not set. Check your .env file.")
else:
    print("API Key loaded successfully.")

# Initialize the Monday client with the API key
client = MondayClient(api_key)

# Attempt to fetch the first 5 boards
try:
    result = client.boards.fetch_boards(limit=5)
    if 'data' in result and 'boards' in result['data']:
        boards = result['data']['boards']
        for board in boards:
            print(f"Board ID: {board['id']}, Board Name: {board['name']}")
    else:
        print("No boards data found.")
except Exception as e:
    print("Failed to fetch boards:", str(e))
