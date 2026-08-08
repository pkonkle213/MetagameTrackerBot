from typing import NamedTuple
from psycopg.rows import class_row, scalar_row
from datetime import date
from settings import DATABASE_URL
import psycopg

from tuple_conversions import Format, Store, Game, Event, PlayerArchetype

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
        e.id = %s
        AND UPPER(fs.player_name) = UPPER(%s)
      '''

      cur.execute(command,[event.id, player_name])
      row = cur.fetchone()
      return row is not None

async def BulkAddArchetypes(
  event:Event,
  archetypes:list[PlayerArchetype],
  user_id:int,
  user_name:str,
  user_discord_id:int,
  user_discord_name:str
) -> int:
  data_to_insert = [(event.id, archetype.player_name, archetype.archetype_played, user_id, user_name, user_discord_id, user_discord_name) for archetype in archetypes]

  async with await psycopg.AsyncConnection.connect(DATABASE_URL) as conn:
    async with conn.cursor() as cur:
      command = '''
      INSERT INTO archetype_submissions (event_id, player_name, archetype_played, date_submitted, submitter_id, submitter_username, reported, submitter_discord_id, submitter_discord_name, is_submitter)
      VALUES (%s, %s, %s, NOW(), %s, %s, FALSE, %s, %s, TRUE)
      '''

      await cur.executemany(command, data_to_insert)
      await conn.commit()
      return len(archetypes)
  

def AddArchetype(
  event_id:int,
  player_name:str,
  archetype_played:str,
  submitter_id:int | None,
  submitter_name:str,
  submitter_guild_id:int,
  submitter_guild_name:str,
  is_submitter:bool
) -> None:
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
      submitter_discord_id,
      submitter_discord_name,
      reported,
      is_submitter)
      VALUES
      ({event_id},
      %s,
      %s,
      NOW(),
      {submitter_id if submitter_id else 'NULL'},
      '{submitter_name}',
      {submitter_guild_id},
      '{submitter_guild_name}',
      {False},
      {is_submitter})
      RETURNING *
      '''

      cur.execute(command, criteria)
      conn.commit()
      row = cur.fetchone()
      if not row:
        raise Exception('Unable to add archetype')

class UnknownArchetypes(NamedTuple):
  event_date: str
  event_name: str
  player_name: str

def GetUnknownArchetypes(
  store:Store,
  game:Game,
  format:Format,
  start_date:date,
  end_date:date
) -> list[UnknownArchetypes]:
  with psycopg.connect(DATABASE_URL) as conn:
    with conn.cursor(row_factory=class_row(UnknownArchetypes)) as cur:
      command = f'''
      SELECT
        TO_CHAR(event_date, 'MM/DD/YYYY') as event_date,
        INITCAP(event_name) as event_name,
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
