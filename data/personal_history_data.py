from custom_errors import KnownError
import settings
from datetime import date
import psycopg
from psycopg.rows import TupleRow
from settings import DATABASE_URL, DATAGUILDID
from tuple_conversions import Format, Game, Store, Hub, Region

def DetermineWhereClause(store:Store | None, hub:Hub | None, region:Region | None) -> str:
  if hub and hub.discord_id == DATAGUILDID:
    return ''
  elif store:
    return f'AND s.discord_id = {store.discord_id}'
  elif region and region.id:
    return f'AND s.region_id = {region.id}'
  elif hub and not region:
    return f'AND rcm.discord_id = {hub.discord_id}'
  else:
    raise Exception('Unable to determine where clause')

def GetPairingsStoreHistory(
  user_id: int,
  store: Store | None,
  hub: Hub | None,
  region: Region | None,
  game: Game | None,
  format: Format | None,
  start_date: date,
  end_date: date
) -> list[TupleRow]:
  where_clause = DetermineWhereClause(store, hub, region)
  conn = psycopg.connect(DATABASE_URL)
  with conn, conn.cursor() as cur:
    command = f'''
    SELECT
      TO_CHAR(e.event_date, 'MM/DD') as event_date,
      {'INITCAP(g.game_name) AS game_name,' if not game else ''}
      {'INITCAP(f.format_name) AS format_name,' if not format else ''}
      fp.round_number,
      INITCAP(COALESCE(uap.archetype_played, 'Unknown')) as players_archetype,
      CASE
        WHEN UPPER(fp.opponent_name) = 'BYE' THEN 'Bye'
        ELSE INITCAP(COALESCE(uao.archetype_played, 'Unknown'))
      END AS opponents_archetype,
      INITCAP(fp.result) as result
    FROM
      full_pairings fp
      INNER JOIN events e ON e.id = fp.event_id
      INNER JOIN stores_view s ON s.discord_id = e.discord_id
      INNER JOIN player_names pn ON UPPER(pn.player_name) = UPPER(fp.player_name) AND pn.discord_id = s.discord_id
      LEFT JOIN unique_archetypes uap ON uap.event_id = e.id AND UPPER(uap.player_name) = UPPER(pn.player_name)
      LEFT JOIN unique_archetypes uao ON uao.event_id = e.id AND UPPER(uao.player_name) = UPPER(fp.opponent_name)
      INNER JOIN games g ON g.id = e.game_id
      INNER JOIN formats f ON f.id = e.format_id
    WHERE
      pn.submitter_id = {user_id}
      AND e.discord_id = {store.discord_id}
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

def GetStandingsHubHistory(
  user_id: int,
  game: Game | None,
  format: Format | None,
  start_date: date,
  end_date: date,
  hub: Hub,
  region: Region | None
) -> list[TupleRow]:
  where_clause = DetermineWhereClause(hub, region)
  conn = psycopg.connect(DATABASE_URL)
  with conn, conn.cursor() as cur:
    command = f'''
    SELECT
      TO_CHAR(event_date, 'MM/DD') as event_date,
      COALESCE(store_name, discord_name) AS store_name,
      {'INITCAP(g.game_name) AS game_name,' if not game else ''}
      {'INITCAP(f.format_name) AS format_name,' if not format else ''}
      COALESCE(INITCAP(archetype_played), 'Unknown') as archetype_played,
      wins,
      losses,
      draws
    FROM
      full_standings fp
      INNER JOIN events e ON e.id = fp.event_id
      INNER JOIN stores_view s ON s.discord_id = e.discord_id
      INNER JOIN games g ON g.id = e.game_id
      INNER JOIN formats f ON f.id = e.format_id
      INNER JOIN player_names pn ON pn.discord_id = e.discord_id AND UPPER(pn.player_name) = UPPER(fp.player_name)
      LEFT JOIN unique_archetypes uar ON uar.event_id = e.id AND UPPER(uar.player_name) = UPPER(pn.player_name)
    WHERE
      pn.submitter_id = {user_id}
      AND e.event_date BETWEEN '{start_date}' AND '{end_date}'
      {f'AND e.game_id = {game.id}' if game else ''}
      {f'AND e.format_id = {format.id}' if format else ''}
      {where_clause}
    ORDER BY
      e.event_date DESC
    '''

    cur.execute(command)
    rows = cur.fetchall()
    return rows

def GetStandingsStoreHistory(
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
      {'INITCAP(g.game_name) AS game_name,' if not game else ''}
      {'INITCAP(f.format_name) AS format_name,' if not format else ''}
      COALESCE(INITCAP(archetype_played), 'Unknown') as archetype_played,
      wins,
      losses,
      draws
    FROM
      full_standings fp
      INNER JOIN events e ON e.id = fp.event_id
      INNER JOIN games g ON g.id = e.game_id
      INNER JOIN formats f ON f.id = e.format_id
      INNER JOIN player_names pn ON pn.discord_id = e.discord_id AND UPPER(pn.player_name) = UPPER(fp.player_name)
      LEFT JOIN unique_archetypes uar ON uar.event_id = e.id AND UPPER(uar.player_name) = UPPER(pn.player_name)
    WHERE
      pn.submitter_id = {user_id}
      AND e.discord_id = {store.discord_id}
      {f'AND e.game_id = {game.id}' if game else ''}
      {f'AND e.format_id = {format.id}' if format else ''}
      AND e.event_date BETWEEN '{start_date}' AND '{end_date}'
    ORDER BY
      e.event_date DESC
    '''

    cur.execute(command)
    rows = cur.fetchall()
    return rows