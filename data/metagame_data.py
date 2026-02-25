from datetime import date
import settings
import os
import psycopg2
from settings import DATABASE_URL
from tuple_conversions import Format, Game, Store


def GetAreaForMeta(store: Store) -> str:
  if store.IsHub:
    return f'AND s.region = {store.Region}'
  if store.DiscordId == settings.DATAGUILDID:
    return f'AND s.used_for_data = {True}'
  return f'AND s.discord_id = {store.DiscordId}'


def GetMetagame(
  game: Game,
  format: Format,
  start_date: date,
  end_date: date,
  store: Store
) -> list:
  conn = psycopg2.connect(DATABASE_URL)
  with conn, conn.cursor() as cur:
    command = f'''
    SELECT
      archetype_played,
      ROUND(metagame_percent * 100, 2) AS metagame_percent,
      ROUND(win_percent * 100, 2) AS win_percent
    FROM (
      SELECT
        COALESCE(UPPER(ua.archetype_played), 'UNKNOWN') AS archetype_played,
        1.0 * sum(fp.wins) / (sum(fp.wins) + sum(fp.losses) + sum(fp.draws)) AS win_percent,
        COUNT(*) * 1.0 / SUM(count(*)) OVER () AS Metagame_Percent
      FROM
        full_standings fp
        LEFT JOIN unique_archetypes ua ON fp.event_id = ua.event_id AND UPPER(fp.player_name) = UPPER(ua.player_name)
        INNER JOIN events e ON fp.event_id = e.id
        INNER JOIN stores s ON e.discord_id = s.discord_id
      WHERE
        e.event_date BETWEEN '{start_date}' AND '{end_date}'
        {GetAreaForMeta(store)}
        AND e.format_id = {format.FormatId}
        AND e.game_id = {game.GameId}
      GROUP BY
        UPPER(ua.archetype_played)
      )
    WHERE
    metagame_percent >= 0.02
    ORDER BY
    2 DESC,
    3 DESC
    '''

    cur.execute(command)
    rows = cur.fetchall()
    return rows
