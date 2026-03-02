from settings import DATABASE_URL
from typing import NamedTuple
import psycopg
from psycopg.rows import class_row


class Message(NamedTuple):
  DiscordID: int
  GameID: int
  CategoryID: int
  FormatID: int
  ChannelID: int


def ThreeDayOldEventsWithUnknown():
  conn = psycopg.connect(DATABASE_URL)
  with conn, conn.cursor(row_factory=class_row(Message)) as cur:
    command = """
    SELECT
      e.discord_id,
      gm.game_id AS game_id,
      gm.category_id,
      fm.format_id AS format_id,
      fm.channel_id
    FROM
      events_reported er
      INNER JOIN events e ON e.id = er.id
      INNER JOIN gamecategorymaps gm ON gm.game_id = e.game_id
      AND gm.discord_id = e.discord_id
      INNER JOIN formatchannelmaps fm ON fm.format_id = e.format_id
      AND fm.discord_id = e.discord_id
    WHERE
      e.event_date = NOW()::date - INTERVAL '3 days'
    GROUP BY
      e.discord_id,
      gm.game_id,
      gm.category_id,
      fm.format_id,
      fm.channel_id
    HAVING
      SUM(er.reported) < SUM(er.total_attended)
    """

    cur.execute(command)
    rows = cur.fetchall()
    return rows
