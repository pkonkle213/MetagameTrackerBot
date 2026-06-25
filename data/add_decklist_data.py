from settings import DATABASE_URL
import psycopg
from tuple_conversions import Card

def AddDeck(player_name:str, event_id: int) -> int:
  conn = psycopg.connect(DATABASE_URL)
  with conn, conn.cursor() as cur:
    command = f'''
    INSERT INTO decks (event_id, player_name)
    VALUES (%s, %s)
    RETURNING id
    '''

    cur.execute(command, [event_id, player_name])
    deck = cur.fetchone()
    if deck is None:
      raise Exception('Unable to add new deck')
      
    return deck[0]

async def AddCards(deck_id:int, cards:list[Card]) -> int:
  data_to_insert = [(deck_id, card.quantity, card.name, card.in_mainboard) for card in cards]
  print(f'----Data to insert:----', data_to_insert)

  async with await psycopg.AsyncConnection.connect(DATABASE_URL) as conn:
    async with conn.cursor() as cur:
      command = '''
      INSERT INTO decklists (deck_id, quantity, card_name, in_mainboard)
      VALUES (%s, %s, %s, %s)
      '''

      await cur.executemany(command, data_to_insert)
      await conn.commit()
      return len(cards)