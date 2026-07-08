from settings import DATABASE_URL
import psycopg
from tuple_conversions import Card, Format

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
  data_to_insert = [(deck_id, card.quantity, card.card_name, card.is_mainboard) for card in cards]

  async with await psycopg.AsyncConnection.connect(DATABASE_URL) as conn:
    async with conn.cursor() as cur:
      command = '''
      INSERT INTO decklists (deck_id, quantity, card_name, is_mainboard)
      VALUES (%s, %s, %s, %s)
      '''

      await cur.executemany(command, data_to_insert)
      await conn.commit()
      return len(cards)

def ConvertInputToPostgresArray(input_list:list[Card]) -> str:
  card_names = [card.card_name.replace("'","''") for card in input_list if is_mainboardboard]
  array_string = "',\n'".join(card_names)
  return f"'{array_string}'"

def SelectArchetype(cards:list[Card], format:Format) -> str:
  maindeck = ConvertInputToPostgresArray(cards)
  conn = psycopg.connect(DATABASE_URL)
  with conn, conn.cursor() as cur:
    command = f'''
    WITH
      selected_format AS (
        SELECT
          id
        FROM
          formats
        WHERE
          id = {format.id}
      ),
      archetypes AS (
          SELECT DISTINCT
            ON (UPPER(archetype_played)) ROW_NUMBER() OVER (
              ORDER BY
                archetype_played
            ) AS archetype_id,
            initcap(archetype_played) AS archetype_name
          FROM
            unique_archetypes ua
            INNER JOIN events e ON e.id = ua.event_id
            INNER JOIN selected_format sf ON sf.id = e.format_id
          WHERE
            e.event_date > CURRENT_DATE - INTERVAL '1 year'
        ),
        cards AS (
          SELECT DISTINCT
            ON (card_name) ROW_NUMBER() OVER (
              ORDER BY
                card_name
            ) AS card_id,
            card_name
          FROM
            decklists dl
            INNER JOIN decks ON dl.deck_id = decks.id
            INNER JOIN events e ON e.id = decks.event_id
            INNER JOIN selected_format sf ON sf.id = e.format_id
          WHERE
            e.event_date > CURRENT_DATE - INTERVAL '1 year'
            AND dl.is_mainboard = TRUE
        ),
        my_decks AS (
          SELECT
            d.id AS deck_id,
            a.archetype_id
          FROM
            decks d
            INNER JOIN events e ON e.id = d.event_id
            INNER JOIN selected_format sf ON sf.id = e.format_id
            INNER JOIN unique_archetypes ua ON ua.event_id = e.id
            AND upper(ua.player_name) = upper(d.player_name)
            INNER JOIN archetypes a ON upper(a.archetype_name) = upper(ua.archetype_played)
          WHERE
            e.event_date > CURRENT_DATE - INTERVAL '1 year'
        ),
        deck_cards AS (
          SELECT
            d.deck_id,
            c.card_id,
            quantity
          FROM
            decklists d
            INNER JOIN cards c ON upper(d.card_name) = upper(c.card_name)
            AND d.is_mainboard = TRUE
        ),
        input_cards AS (
          SELECT
            UNNEST(
              ARRAY[{maindeck}]::TEXT[]
            ) AS card_name
        ),
        matched_ids AS (
          SELECT
            c.card_id
          FROM
            cards c
            JOIN input_cards ic ON c.card_name = ic.card_name
        ),
        deck_stats AS (
          SELECT
            deck_id,
            COUNT(card_id) AS total_cards_in_deck
          FROM
            deck_cards
          GROUP BY
            deck_id
        ),
        matches AS (
          SELECT
            dc.deck_id,
            COUNT(dc.card_id) AS matched_card_count
          FROM
            deck_cards dc
            JOIN matched_ids mi ON dc.card_id = mi.card_id
          GROUP BY
            dc.deck_id
        )
      SELECT
        a.archetype_name
      FROM
        matches m
        JOIN deck_stats ds ON m.deck_id = ds.deck_id
        JOIN my_decks d ON m.deck_id = d.deck_id
        JOIN archetypes a ON d.archetype_id = a.archetype_id
      WHERE
        1.0 * m.matched_card_count / ds.total_cards_in_deck > 0.9
      ORDER BY
        1.0 * m.matched_card_count / ds.total_cards_in_deck DESC,
        m.matched_card_count DESC
      LIMIT 1
    '''

    cur.execute(command)
    archetype = cur.fetchone()
    if archetype is None:
      return 'Other'
    return archetype[0]