from psycopg.rows import scalar_row
from settings import DATABASE_URL
import psycopg
from tuple_conversions import Store, Game, Format

def AddUpdatedArchetypes(
  store:Store,
  game:Game,
  format:Format,
  old_archetype:str,
  new_archetype:str,
  is_submitter:bool,
  submitter_name:str,
  submitter_id:int,
  submitter_discord_id:int,
  submitter_discord_name: str
) -> int:
  conn = psycopg.connect(DATABASE_URL)
  with conn, conn.cursor(row_factory=scalar_row) as cur:
    command = '''
    WITH inserted_rows AS (
    INSERT INTO
      archetype_submissions (
        event_id,
        player_name,
        archetype_played,
        date_submitted,
        submitter_id,
        submitter_username,
        reported,
        submitter_discord_id,
        submitter_discord_name,
        is_submitter
      )
    SELECT
      event_id,
      player_name,
      %s,
      NOW(),
      %s,
      %s,
      FALSE,
      %s,
      %s,
      TRUE
    FROM
      archetype_submissions asu
      INNER JOIN events e ON asu.event_id = e.id
    WHERE
      UPPER(archetype_played) = UPPER(%s)
      AND e.discord_id = %s
      AND e.format_id = %s
      AND e.game_id = %s
    RETURNING 1
    )
    SELECT COUNT(*) FROM inserted_rows
    '''

    print('UpdateArchetypes Command:', command)
    criteria = [new_archetype, submitter_id, submitter_name, submitter_discord_id, submitter_discord_name, old_archetype, store.discord_id, format.id, game.id]
    cur.execute(command, criteria)
    conn.commit()
    row = cur.fetchone()
    if not row:
      raise Exception(f'Unable to update archetypes')
    return row