from collections import namedtuple
import os
import psycopg2

from tuple_conversions import Format, Game, Store


def GetPlayerName(user_id: int,
                  discord_id: int):
  """Pulls the player name for a userId and a discordId from the database"""
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
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
    return row[0] if row else None

def GetWinPercentage(user_id: int,
                     store: Store,
                     game: Game,
                     format: Format):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command = f"""
    SELECT
      ROUND(100.0 * SUM(wins) / (SUM(wins) + SUM(losses) + SUM(draws)), 2) AS win_percentage
    FROM
      full_standings fs
      INNER JOIN events e ON fs.event_id = e.id
      INNER JOIN player_names pn ON UPPER(pn.player_name) = UPPER(fs.player_name) AND pn.discord_id = e.discord_id
    WHERE
      e.discord_id = {store.DiscordId}
      AND pn.submitter_id = {user_id}
      AND e.event_date >= CURRENT_DATE - INTERVAL '1 year'
      AND e.format_id = {format.ID}
      AND e.game_id = {game.ID}
    """
    cur.execute(command)
    row = cur.fetchone()
    return row[0] if row else None

def GetLastArchetype(user_id: int,
                  store: Store,
                  game: Game,
                  format: Format):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command = f"""
    SELECT
      e.event_date,
      archetype_played
    FROM
      full_standings fs
      INNER JOIN events e ON fs.event_id = e.id
      INNER JOIN player_names pn ON UPPER(pn.player_name) = UPPER(fs.player_name) AND pn.discord_id = e.discord_id
      INNER JOIN unique_archetypes ua ON e.id = ua.event_id AND UPPER(ua.player_name) = UPPER(fs.player_name)
    WHERE
      e.discord_id = {store.DiscordId}
      AND pn.submitter_id = {user_id}
      AND e.format_id = {format.ID}
      AND e.game_id = {game.ID}
    ORDER BY e.event_date DESC
    LIMIT 1
    """
    
    cur.execute(command)
    row = cur.fetchone()
    return row if row else None

TopDeck = namedtuple('TopDecks',['Archetype','WinPercentage','ChancePlayed'])

def GetMostPlayed(user_id: int,
                  store: Store,
                  game: Game,
                  format: Format):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command = f"""
    SELECT
      UPPER(archetype_played) AS archetype_played,
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
      e.discord_id = {store.DiscordId}
      AND pn.submitter_id = {user_id}
      AND e.format_id = {format.ID}
      AND e.game_id = {game.ID}
      AND e.event_date >= CURRENT_DATE - INTERVAL '1 year'
    GROUP BY
      UPPER(archetype_played)
    ORDER BY
      3 DESC, 1
    LIMIT
      3
    """

    cur.execute(command)
    rows = cur.fetchall()
    return [TopDeck(row[0].title(), row[1], row[2]) for row in rows] if rows else None