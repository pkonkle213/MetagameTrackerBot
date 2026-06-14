import re
import requests

def get_moxfield_decklist(url) -> list[str]:
  # Extract the Deck ID from any valid Moxfield URL
  match = re.search(r"decks/([a-zA-Z0-9_-]+)", url)
  if not match:
    raise ValueError("Invalid Moxfield URL")

  deck_id = match.group(1)
  api_url = f"https://api2.moxfield.com/v2/decks/all/{deck_id}"

  # Send request with a standard User-Agent to avoid being blocked
  headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
  }

  response = requests.get(api_url, headers=headers)
  response.raise_for_status()

  deck_data = response.json()
  cards = []

  format_name = deck_data.get("format")
  print(f'----Format: {format_name}----')
  
  # Loop through the board (Mainboard/Sideboard/Commander)
  for board_name in ["mainboard", "sideboard"]:
    board = deck_data.get(board_name, {})
    for card_id, details in board.items():
      card_name = details.get("card", {}).get("name")
      cards.append(f"{card_name}")
  return cards
