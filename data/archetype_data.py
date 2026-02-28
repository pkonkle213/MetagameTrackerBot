from settings import DATABASE_URL
import psycopg

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

def GetUnknownArchetypes(discord_id,
                         game_id,
                         format_id,
                         start_date,
                         end_date) -> list:
  with psycopg.connect(DATABASE_URL) as conn:
    with conn.cursor() as cur:
      command = f'''
      SELECT
        event_date,
        player_name
      FROM
        unknown_archetypes
      WHERE
        event_date BETWEEN '{start_date}' AND '{end_date}'
        AND game_id = {game_id}
        AND format_id = {format_id}
        AND discord_id = {discord_id}
      ORDER BY
        event_date desc,
        player_name
      '''

      cur.execute(command)  # type: ignore[arg-type]
      rows = cur.fetchall()
      return rows
