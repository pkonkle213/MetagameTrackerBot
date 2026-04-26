from psycopg.rows import scalar_row
from datetime import date
from settings import DATABASE_URL
import psycopg

from tuple_conversions import Format, Store, Game, Event

def PlayerInEvent(event:Event, player_name:str) -> bool:
  with psycopg.connect(DATABASE_URL) as conn:
    with conn.cursor(row_factory=scalar_row) as cur:
      command = f'''
      SELECT
        e.id
      FROM
        events e
        INNER JOIN full_standings fs ON fs.event_id = e.id
      WHERE
        e.id = {event.id}
        AND UPPER(fs.player_name) = UPPER('{player_name}')
      '''

      cur.execute(command)
      row = cur.fetchone()
      return row is not None

def AddArchetype(
  event_id:int,
  player_name:str,
  archetype_played:str,
  submitter_id:int,
  submitter_name:str
) -> int:
  criteria = [player_name, archetype_played]
  with psycopg.connect(DATABASE_URL) as conn:
    with conn.cursor() as cur:
      command = f'''
      INSERT INTO archetype_submissions
      (event_id,
      player_name,
      archetype_played,
      date_submitted,
      submitter_id,
      submitter_username,
      reported)
      VALUES
      ({event_id},
      %s,
      %s,
      NOW(),
      {submitter_id},
      '{submitter_name}',
      {False})
      RETURNING *
      '''

      cur.execute(command, criteria)
      conn.commit()
      row = cur.fetchone()
      if not row:
        raise Exception('Unable to add archetype')
      return row[0]

def GetUnknownArchetypes(store:Store,
                         game:Game,
                         format:Format,
                         start_date:date,
                         end_date:date) -> list:
  with psycopg.connect(DATABASE_URL) as conn:
    with conn.cursor() as cur:
      command = f'''
      SELECT
        TO_CHAR(event_date,'MM/DD') as event_date,
        event_name,
        INITCAP(player_name) as player_name
      FROM
        unknown_archetypes ua
      WHERE
        event_date BETWEEN '{start_date}' AND '{end_date}'
        AND game_id = {game.id}
        AND format_id = {format.id}
        AND discord_id = {store.discord_id}
      ORDER BY
        event_date desc,
        INITCAP(player_name)
      '''

      cur.execute(command)
      rows = cur.fetchall()
      return rows
