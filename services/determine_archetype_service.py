import re
import requests
from tuple_conversions import Format, Card

def GetMoxfieldArchetype(url:str, format:Format) -> str:
  print('----Getting Moxfield Archetype----')
  # Determine if the url is a moxfield url or a moxfield deck id
  slashes = url.count('/')
  mox_url = ''
  if slashes == 0:
    mox_url = f"https://www.moxfield.com/decks/{url}"
  elif slashes == 1:
    mox_url = f"https://www.moxfield.com/{url}"

  match = re.search(r"decks/([a-zA-Z0-9_-]+)", url)
  if not match:
    raise ValueError("Invalid Moxfield URL")

  deck_id = match.group(1)
  api_url = f"https://api2.moxfield.com/v2/decks/all/{deck_id}"
  
  # Get api response (get_deck.py). Have it return qty, card name. Check legality of each card and throw error if illegal
  headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
  }

  response = requests.get(api_url, headers=headers)
  response.raise_for_status()

  deck_data = response.json()
  cards:list[Card] = []

  print(f'----Format: {format.format_name}----')
  
  # Loop through cards and make decklist of card qty, name, and check if legal
  for board_name in ["mainboard", "sideboard"]:
    board = deck_data.get(board_name, {})
    for card_id, details in board.items():
      card_name = details.get("card", {}).get("name")
      card_qty = details.get("quantity")
      legal = details.get("card").get("legalities").get(format.format_name)
      print(f"{card_qty} {card_name} is {legal} in {format.format_name} format")
      if legal != 'legal':
        print(f"{card_name} is not legal in {format.format_name} format")
        raise ValueError(f"{card_name} is not legal in {format.format_name} format")
        
      cards.append(Card(card_qty, card_name))

  print('----Decklist cards----')
  for card in cards:
    print(f"{card.quantity} {card.name}")
  # Build an array of strings of card names, get archetypes and their haves/nots. loop through to determine the name of the archetype
  
  return ''