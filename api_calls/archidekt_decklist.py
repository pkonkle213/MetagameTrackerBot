from custom_errors import KnownError
import re
import requests
from data.add_decklist_data import AddDeck, AddCards, SelectArchetype
from tuple_conversions import Format, Card, Event

async def GetArchidektDecklist(
  url:str,
  event:Event,
  format:Format,
  player_name:str
) -> str:
  slash = url.rfind('/')
  archidekt_id = url[slash+1:]  

  api_url = f"https://archidekt.com/api/decks/{archidekt_id}/"

  try:
    response = requests.get(api_url)
    response.raise_for_status()
  except requests.exceptions.HTTPError as e:
    raise KnownError("Error fetching decklist")

  deck_data = response.json()
  cards:list[Card] = []

  deck_id = AddDeck(player_name, event.id)

  for raw_card in deck_data.get("cards"):
    categories = raw_card.get("categories") 
    is_main = not any(c.lower() == "sideboard" for c in categories)
   
    quantity = raw_card.get("quantity")
    card = raw_card.get("card")
    name = card.get("oracleCard").get("name")
    legalities = card.get("oracleCard").get("legalities")
    format_legality = legalities.get(format.format_name.lower())
    legal = format_legality == "legal"
    if not legal:
      raise KnownError(f"{name} is not legal in {format.format_name}")

    cards.append(Card(deck_id, quantity, name, is_main))

  rows = await AddCards(deck_id, cards)

  archetype_guess = SelectArchetype(cards, format)

  return "Done, check the console"