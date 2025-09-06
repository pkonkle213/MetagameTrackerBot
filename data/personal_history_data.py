from datetime import date
import os
import psycopg2
from settings import DATAGUILDID

from tuple_conversions import Format, Game, Store

def GetPairingsHistory(user_id: int, game: Game, format: Format,
                       start_date: date, end_date: date, store: Store):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command = f'''
    SELECT
      e.event_date,
      {'s.discord_name,' if store.DiscordId == DATAGUILDID else ''}
      {'g.name AS game_name,' if not game else ''}
      {'f.name AS format_name,' if not format else ''}
      fp.round_number,
      COALESCE(ua.archetype_played,'BYE') as archetype_played,
      fp.result
    FROM
      full_pairings fp
      INNER JOIN events e ON e.id = fp.event_id
      INNER JOIN stores s ON s.discord_id = e.discord_id
      INNER JOIN player_names pn ON pn.player_name = fp.player_name
      AND pn.discord_id = s.discord_id
      LEFT JOIN unique_archetypes ua ON ua.event_id = e.id
      AND ua.player_name = fp.opponent_name
      INNER JOIN games g ON g.id = e.game_id
      INNER JOIN formats f ON f.id = e.format_id
    WHERE
      pn.submitter_id = {user_id}
      {f'AND e.discord_id = {store.DiscordId}' if store.DiscordId != DATAGUILDID else ''}
      {f'AND e.game_id = {game.ID}' if game else ''}
      {f'AND e.format_id = {format.ID}' if format else ''}
      AND e.event_date BETWEEN '{start_date}' AND '{end_date}'
    ORDER BY
      e.event_date DESC,
      fp.round_number
    '''

    cur.execute(command)
    rows = cur.fetchall()
    return rows
    

def GetStandingsHistory(user_id: int, game: Game, format: Format,
                       start_date: date, end_date: date, store: Store):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command = f'''
    SELECT
      event_date,
      {'s.discord_name,' if store.DiscordId == DATAGUILDID else ''}
      {'g.name AS game_name,' if not game else ''}
      {'f.name AS format_name,' if not format else ''}
      archetype_played,
      wins,
      losses,
      draws
    FROM
      full_standings fp
      INNER JOIN events e ON e.id = fp.event_id
      INNER JOIN games g ON g.id = e.game_id
      INNER JOIN formats f ON f.id = e.format_id
      INNER JOIN player_names pn ON pn.discord_id = e.discord_id
      AND pn.player_name = fp.player_name
      INNER JOIN unique_archetypes uar ON uar.event_id = e.id
      AND uar.player_name = pn.player_name
    WHERE
      pn.submitter_id = {user_id}
      {f'AND e.discord_id = {store.DiscordId}' if store.DiscordId != DATAGUILDID else ''}
      {f'AND e.game_id = {game.ID}' if game else ''}
      {f'AND e.format_id = {format.ID}' if format else ''}
      AND e.event_date BETWEEN '{start_date}' AND '{end_date}'
    ORDER BY
      e.event_date DESC
    '''

    cur.execute(command)
    rows = cur.fetchall()
    return rows