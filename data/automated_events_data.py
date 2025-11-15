import os
import psycopg2
from collections import namedtuple

Message = namedtuple('Message',['DiscordID',
                                'GameID',
                                'CategoryID',
                                'FormatID',
                                'ChannelID'])

def ThreeDayOldEventsWithUnknown():
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
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
    return [Message(row[0], row[1], row[2], row[3], row[4]) for row in rows]

Event = namedtuple('Event',['ID',
                            'DiscordID',
                            'ChannelID'])

def GetCompletedUnpostedEvents():
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command = """
    SELECT
      ev.id,
      ev.discord_id,
      fm.channel_id
    FROM
      events_view ev
      INNER JOIN formatchannelmaps fm ON fm.discord_id = ev.discord_id
      AND fm.format_id = ev.format_id
      INNER JOIN events_reported er ON ev.id = er.id
    WHERE
      is_complete
      AND NOT is_posted
      AND er.reported = er.total_attended;
    """

    cur.execute(command)
    rows = cur.fetchall()
    return [Event(row[0], row[1], row[2]) for row in rows]