from datetime import date
from settings import DATABASE_URL
import psycopg
from tuple_conversions import Format, Game, Store, Event
from psycopg.rows import class_row

def GetSubmittedArchetypes(
  game:Game,
  format:Format | None,
  store:Store,
  player_name: str | None,
  date:date | None):
  conn = psycopg.connect(DATABASE_URL)
  with conn, conn.cursor() as cur:
    criteria = [player_name] if player_name != '' else []
    command = f'''
    SELECT e.event_date,
      {'f.format_name,' if not format else ''}
      INITCAP(ua.player_name) as player_name,
      ua.archetype_played,
      ua.submitter_username,
      ua.submitter_id
    FROM unique_archetypes ua
      INNER JOIN events e on ua.event_id = e.id
      INNER JOIN formats f on f.id = e.format_id
    WHERE ua.reported = FALSE
      AND e.discord_id = {store.discord_id}
      AND e.game_id = {game.id}
      {f'AND e.format_id = {format.id}' if format is not None else ''}
      {f"AND e.event_date = '{date}'" if date is not None else ''}
      {f"AND UPPER(ua.player_name) = UPPER('{player_name}')" if player_name != '' else ''}
    ORDER BY
      e.event_date desc,
      ua.player_name
    LIMIT 15
    '''

    print('Command used:\n', command)
    cur.execute(command, criteria)
    rows = cur.fetchall()
    return rows
    