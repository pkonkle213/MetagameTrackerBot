from datetime import date
import os
import psycopg2

from tuple_conversions import Format, Game, Store

def GetPersonalHistory(user_id: int, game: Game, format: Format,
                       start_date: date, end_date: date, store: Store):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command = f'''
    SELECT
      event_date,
      {'cg.name AS game_name,' if not game else ''}
      {'f.name AS format_name,' if not format else ''}
      archetype_played,
      wins,
      losses,
      draws
    FROM
      fullparticipants fp
      INNER JOIN events e ON e.id = fp.event_id
      INNER JOIN cardgames cg ON cg.id = e.game_id
      INNER JOIN formats f ON f.id = e.format_id
      INNER JOIN playernames pn ON pn.discord_id = e.discord_id
      AND pn.player_name = fp.player_name
      INNER JOIN uniquearchetypes uar ON uar.event_id = e.id
      AND uar.player_name = pn.player_name
    WHERE
      pn.submitter_id = {user_id}
      AND e.discord_id = {store.DiscordId}
      {f'AND e.game_id = {game.ID}' if game else ''}
      {f'AND e.format_id = {format.ID}' if format else ''}
      AND e.event_date BETWEEN '{start_date}' AND '{end_date}'
    ORDER BY
      e.event_date DESC
    '''

    cur.execute(command)
    rows = cur.fetchall()
    return rows