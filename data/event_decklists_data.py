from custom_errors import KnownError
from psycopg.rows import class_row
from tuple_conversions import Deck, Event, Card
import psycopg
from settings import DATABASE_URL

def GetDecks(event:Event) -> list[Deck]:
  conn = psycopg.connect(DATABASE_URL)
  with conn, conn.cursor(row_factory=class_row(Deck)) as cur:
    command = f'''
    SELECT
      d.id,
      INITCAP(COALESCE(ua.archetype_played, 'Unknown')) AS archetype_played,
      fs.wins,
      fs.losses,
      fs.draws
    FROM
      decks d
      INNER JOIN full_standings fs ON fs.event_id = d.event_id
      AND upper(fs.player_name) = upper(d.player_name)
      LEFT JOIN unique_archetypes ua ON ua.event_id = d.event_id
      AND upper(ua.player_name) = upper(d.player_name)
    WHERE
      d.event_id = {event.id}
    ORDER BY
      fs.wins DESC,
      fs.draws DESC,
      fs.losses DESC
    '''

    cur.execute(command)
    rows = cur.fetchall()
    if rows is None:
      raise KnownError('Unable to get any decks for this event')
    return rows

def GetDecklists(event:Event) -> list[Card]:
  conn = psycopg.connect(DATABASE_URL)
  with conn, conn.cursor(row_factory=class_row(Card)) as cur:
    command = f'''
    SELECT
      deck_id,
      quantity,
      card_name,
      is_mainboard
    FROM
      decklists
    WHERE
      deck_id IN (
      SELECT
        id
      FROM
        decks
      WHERE
        event_id = {event.id}
      )
    ORDER BY
      deck_id,
      is_mainboard DESC,
      card_name
    '''

    cur.execute(command)
    rows = cur.fetchall()
    
    return rows