from psycopg.rows import class_row
from datetime import date
from typing import NamedTuple
from settings import DATABASE_URL
import psycopg
from tuple_conversions import Format, Game, Store


def GetPlayerName(
  user_id: int,
  discord_id: int
) -> str:
  """Pulls the player name for a userId and a discordId from the database"""
  conn = psycopg.connect(DATABASE_URL)
  with conn, conn.cursor() as cur:
    command = f"""
    SELECT
      player_name
    FROM
      player_names
    WHERE
      discord_id = {discord_id}
      AND submitter_id = {user_id}
    """
    
    cur.execute(command)
    row = cur.fetchone()
    if not row:
      raise Exception('Unable to get player name')
    return row[0]

def GetWinPercentage(
  user_id: int,
  store: Store,
  game: Game,
  format: Format
) -> float:
  conn = psycopg.connect(DATABASE_URL)
  with conn, conn.cursor() as cur:
    command = f"""
    SELECT
      ROUND(100.0 * SUM(wins) / (SUM(wins) + SUM(losses) + SUM(draws)), 2) AS win_percentage
    FROM
      full_standings fs
      INNER JOIN events e ON fs.event_id = e.id
      INNER JOIN player_names pn ON UPPER(pn.player_name) = UPPER(fs.player_name) AND pn.discord_id = e.discord_id
    WHERE
      e.discord_id = {store.discord_id}
      AND pn.submitter_id = {user_id}
      AND e.event_date >= CURRENT_DATE - INTERVAL '1 year'
      AND e.format_id = {format.id}
      AND e.game_id = {game.id}
    """
    cur.execute(command)
    row = cur.fetchone()
    if not row:
      raise Exception('Unable to get win percentage')
    return row[0]

class LastArchetype(NamedTuple):
  event_date: date
  archetype_played: str

def GetLastArchetype(
  user_id: int,
  store: Store,
  game: Game,
  format: Format
) -> LastArchetype:
  conn = psycopg.connect(DATABASE_URL)
  with conn, conn.cursor(row_factory=class_row(LastArchetype)) as cur:
    command = f"""
    SELECT
      TO_CHAR(e.event_date,'MM/DD') as event_date,
      INITCAP(archetype_played) as archetype_played
    FROM
      full_standings fs
      INNER JOIN events e ON fs.event_id = e.id
      INNER JOIN player_names pn ON UPPER(pn.player_name) = UPPER(fs.player_name) AND pn.discord_id = e.discord_id
      INNER JOIN unique_archetypes ua ON e.id = ua.event_id AND UPPER(ua.player_name) = UPPER(fs.player_name)
    WHERE
      e.discord_id = {store.discord_id}
      AND e.event_date < CURRENT_DATE
      AND pn.submitter_id = {user_id}
      AND e.format_id = {format.id}
      AND e.game_id = {game.id}
    ORDER BY e.event_date DESC
    LIMIT 1
    """
    
    cur.execute(command)
    row = cur.fetchone()
    if not row:
      raise Exception('Unable to get last archetype')
    return row

class TopDeck(NamedTuple):
  archetype_played: str
  win_percentage: float
  chance_played: float
  
def GetMostPlayed(
  user_id: int,
  store: Store,
  game: Game,
  format: Format
) -> list[TopDeck]:
  conn = psycopg.connect(DATABASE_URL)
  with conn, conn.cursor(row_factory=class_row(TopDeck)) as cur:
    command = f"""
    SELECT
      INITCAP(archetype_played) AS archetype_played,
      ROUND(100.0 * SUM(wins) / (SUM(wins) + SUM(losses) + SUM(draws)), 2) AS win_percentage,
      ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS chance_played
    FROM
      full_standings fs
      INNER JOIN events e ON fs.event_id = e.id
      INNER JOIN player_names pn ON UPPER(pn.player_name) = UPPER(fs.player_name)
      AND pn.discord_id = e.discord_id
      INNER JOIN unique_archetypes ua ON e.id = ua.event_id
      AND UPPER(ua.player_name) = UPPER(fs.player_name)
    WHERE
      e.discord_id = {store.discord_id}
      AND pn.submitter_id = {user_id}
      AND e.format_id = {format.id}
      AND e.game_id = {game.id}
      AND e.event_date >= CURRENT_DATE - INTERVAL '1 year'
    GROUP BY
      INITCAP(archetype_played)
    ORDER BY
      3 DESC, 1
    LIMIT
      3
    """

    cur.execute(command)
    rows = cur.fetchall()
    return rows