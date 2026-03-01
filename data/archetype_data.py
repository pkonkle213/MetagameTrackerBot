from datetime import date
from settings import DATABASE_URL
import psycopg

from tuple_conversions import Format, Store, Game

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
      INSERT INTO ArchetypeSubmissions
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
      RETURNING id
      '''

      cur.execute(command, criteria)  # type: ignore[arg-type]
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
        AND game_id = {game.GameId}
        AND format_id = {format.FormatId}
        AND discord_id = {store.DiscordId}
      ORDER BY
        event_date desc,
        INITCAP(player_name)
      '''

      cur.execute(command)  # type: ignore[arg-type]
      rows = cur.fetchall()
      return rows
