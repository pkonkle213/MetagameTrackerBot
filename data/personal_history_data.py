from datetime import date

from psycopg.rows import TupleRow
from settings import DATABASE_URL
import psycopg
from settings import DATAGUILDID
from tuple_conversions import Format, Game, Store

def GetPairingsHistory(
  user_id: int,
  game: Game | None,
  format: Format | None,
  start_date: date,
  end_date: date,
  store: Store
) -> list[TupleRow]:
  conn = psycopg.connect(DATABASE_URL)
  with conn, conn.cursor() as cur:
    command = f'''
    SELECT
      TO_CHAR(e.event_date, 'MM/DD') as event_date,
      {'s.discord_name,' if store.discord_id == DATAGUILDID else ''}
      {'INITCAP(g.game_name) AS game_name,' if not game else ''}
      {'INITCAP(f.format_name) AS format_name,' if not format else ''}
      fp.round_number,
      INITCAP(COALESCE(uap.archetype_played, 'Unknown')) as players_archetype,
      INITCAP(COALESCE(uao.archetype_played, 'BYE')) as opponents_archetype,
      INITCAP(fp.result) as result
    FROM
      full_pairings fp
      INNER JOIN events e ON e.id = fp.event_id
      INNER JOIN stores s ON s.discord_id = e.discord_id
      INNER JOIN player_names pn ON UPPER(pn.player_name) = UPPER(fp.player_name) AND pn.discord_id = s.discord_id
      LEFT JOIN unique_archetypes uap ON uap.event_id = e.id AND UPPER(uap.player_name) = UPPER(pn.player_name)
      LEFT JOIN unique_archetypes uao ON uao.event_id = e.id AND UPPER(uao.player_name) = UPPER(fp.opponent_name)
      INNER JOIN games g ON g.id = e.game_id
      INNER JOIN formats f ON f.id = e.format_id
    WHERE
      pn.submitter_id = {user_id}
      {f'AND e.discord_id = {store.discord_id}' if store.discord_id != DATAGUILDID else ''}
      {f'AND e.game_id = {game.id}' if game else ''}
      {f'AND e.format_id = {format.id}' if format else ''}
      AND e.event_date BETWEEN '{start_date}' AND '{end_date}'
    ORDER BY
      e.event_date DESC,
      fp.round_number
    '''

    cur.execute(command)
    rows = cur.fetchall()
    return rows
    

def GetStandingsHistory(
  user_id: int,
  game: Game | None,
  format: Format | None,
  start_date: date,
  end_date: date,
  store: Store
) -> list[TupleRow]:
  conn = psycopg.connect(DATABASE_URL)
  with conn, conn.cursor() as cur:
    command = f'''
    SELECT
      TO_CHAR(event_date, 'MM/DD') as event_date,
      {'s.discord_name,' if store.discord_id == DATAGUILDID else ''}
      {'INITCAP(g.game_name) AS game_name,' if not game else ''}
      {'INITCAP(f.format_name) AS format_name,' if not format else ''}
      INITCAP(archetype_played) as archetype_played,
      wins,
      losses,
      draws
    FROM
      full_standings fp
      INNER JOIN events e ON e.id = fp.event_id
      INNER JOIN games g ON g.id = e.game_id
      INNER JOIN formats f ON f.id = e.format_id
      INNER JOIN player_names pn ON pn.discord_id = e.discord_id AND UPPER(pn.player_name) = UPPER(fp.player_name)
      INNER JOIN unique_archetypes uar ON uar.event_id = e.id AND UPPER(uar.player_name) = UPPER(pn.player_name)
    WHERE
      pn.submitter_id = {user_id}
      {f'AND e.discord_id = {store.discord_id}' if store.discord_id != DATAGUILDID else ''}
      {f'AND e.game_id = {game.id}' if game else ''}
      {f'AND e.format_id = {format.id}' if format else ''}
      AND e.event_date BETWEEN '{start_date}' AND '{end_date}'
    ORDER BY
      e.event_date DESC
    '''

    cur.execute(command)
    rows = cur.fetchall()
    return rows