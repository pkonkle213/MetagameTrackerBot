import os
import psycopg2

def GetSubmittedArchetypes(game, format, store, player_name, date):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    criteria = [player_name] if player_name != '' else []
    command = f'''
    SELECT e.event_date,
      {'f.name,' if not format else ''}
      ua.player_name,
      ua.archetype_played,
      ua.submitter_username,
      ua.submitter_id
    FROM unique_archetypes ua
      INNER JOIN events e on ua.event_id = e.id
      INNER JOIN formats f on f.id = e.format_id
    WHERE ua.reported = FALSE
      AND e.discord_id = {store.DiscordId}
      AND e.game_id = {game.GameId}
      {f'AND e.format_id = {format.FormatId}' if format is not None else ''}
      {f"AND e.event_date = '{date}'" if date is not None else ''}
      {f"AND UPPER(ua.player_name) = UPPER('{player_name}')" if player_name != '' else ''}
    ORDER BY
      e.event_date desc,
      ua.player_name
    LIMIT 15
    '''

    cur.execute(command, criteria)
    rows = cur.fetchall()
    return rows
    