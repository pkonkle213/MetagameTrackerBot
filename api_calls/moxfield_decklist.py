from custom_errors import KnownError
import re
import requests
from data.add_decklist_data import AddDeck, AddCards, SelectArchetype
from tuple_conversions import Format, Card, Event

#TODO: This does too much and should be broken apart.
async def GetMoxfieldArchetype(
  url:str,
  event:Event,
  format:Format,
  player_name:str
) -> str:
  # Transform into a moxfield deck id
  slash = url.rfind('/')  
  mox_id = url[slash+1:]
  
  match = re.search(r"([a-zA-Z0-9_-]+)", mox_id)
  if not match:
    raise ValueError("Invalid Moxfield URL")

  deck_id = match.group(1)
  api_url = f"https://api2.moxfield.com/v2/decks/all/{deck_id}"
  
  headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
  }

  try:
    response = requests.get(api_url, headers=headers)
    response.raise_for_status()
  except requests.exceptions.HTTPError as e:
    raise KnownError("Error fetching decklist")

  deck_data = response.json()
  cards:list[Card] = []
  
  # Save the decklist in the db
  # 1) Make a new deck
  deck_id = AddDeck(player_name, event.id)
  
  # Loop through cards and make decklist of card qty, name, and check if legal
  for board_name in ["mainboard", "sideboard"]:
    board = deck_data.get(board_name, {})
    for card_id, details in board.items():
      card_name = details.get("card", {}).get("name")
      card_qty = details.get("quantity")
      in_main = board_name == "mainboard"
      legal = details.get("card").get("legalities").get(format.format_name.lower())
      if legal != 'legal':
        raise KnownError(f"{card_name} is not legal in {format.format_name} format")
        
      cards.append(Card(deck_id, card_qty, card_name, in_main))

  
  # 2) Input qty and card names for decklist
  rows = await AddCards(deck_id, cards)

  # 3) Determine Archetype
  archetype_guess = SelectArchetype(cards, format)
    
  return archetype_guess