from custom_errors import KnownError
import re
import requests
from urllib.parse import urlparse
from data.add_decklist_data import AddDeck, AddCards, SelectArchetype
from tuple_conversions import Format, Card, Event


def GetMoxfieldDeckId(url_or_id: str) -> str:
  value = url_or_id.strip()
  if re.fullmatch(r"[a-zA-Z0-9_-]+", value):
    return value

  parsed_url = urlparse(value)
  if parsed_url.hostname not in {"moxfield.com", "www.moxfield.com"}:
    raise KnownError("Invalid Moxfield URL")

  path_parts = [part for part in parsed_url.path.split("/") if part]
  if len(path_parts) != 2 or path_parts[0] != "decks":
    raise KnownError("Invalid Moxfield URL")

  deck_id = path_parts[1]
  if not re.fullmatch(r"[a-zA-Z0-9_-]+", deck_id):
    raise KnownError("Invalid Moxfield URL")
  return deck_id


async def GetMoxfieldArchetype(
  url:str,
  event:Event,
  format:Format,
  player_name:str
) -> str:
  deck_id = GetMoxfieldDeckId(url)
  api_url = f"https://api2.moxfield.com/v2/decks/all/{deck_id}"
  canonical_link = f"https://moxfield.com/decks/{deck_id}"
  
  headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
  }

  try:
    response = requests.get(api_url, headers=headers)
    response.raise_for_status()
  except requests.exceptions.HTTPError as e:
    raise KnownError(f"Error fetching decklist: {e}")

  
  deck_data = response.json()
  cards:list[Card] = []
  
  # Save the decklist in the db
  # 1) Make a new deck
  deck_id = await AddDeck(player_name, event.id, canonical_link)
  
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
  archetype_guess = await SelectArchetype(cards, format)
    
  return archetype_guess