import httpx
import mtg_parser

def parse_mtg_decklist(deck_id:str):
  url = f'https://www.moxfield.com/decks/{deck_id}'

  headers = {
    'user-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
  }
  with httpx.Client(headers=headers) as http_client:
    cards = mtg_parser.parse_deck(url, http_client)

  print('Cards:', cards)
  return cards