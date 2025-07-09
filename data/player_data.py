import os
import psycopg2

def GetStats(discord_id,
             game,
             format,
             user_id,
             start_date,
             end_date):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command = f'''
    SELECT
      {'format_name,' if not format else ''}
      archetype_played,
      wins,
      losses,
      draws,
      ROUND(100 * win_percentage, 2) AS win_percentage
    FROM
      (
        SELECT
          1 AS rank,
          {"' ' AS format_name," if not format else ''}
          'OVERALL' AS archetype_played,
          sum(wins) AS wins,
          sum(losses) AS losses,
          sum(draws) AS draws,
          1.0 * SUM(wins) / (SUM(wins) + SUM(losses) + SUM(draws)) AS win_percentage
        FROM
          fullparticipants fp
          INNER JOIN events e ON e.id = fp.event_id
          INNER JOIN formats f ON e.format_id = f.id
        WHERE
          fp.player_name = (
            SELECT
              player_name
            FROM
              playernames
            WHERE
              submitter_id = {user_id}
              AND discord_id = {discord_id}
          )
          AND e.event_date BETWEEN '{start_date}' AND '{end_date}'
          AND e.discord_id = {discord_id}
          AND e.game_id = {game.ID}
          {f'AND e.format_id = {format.ID}' if format else ''}
        UNION
        SELECT
          2 AS rank,
          {'f.name AS format_name,' if not format else ''}
          COALESCE(archetype_played, 'UNKNOWN') AS archetype_played,
          SUM(wins) AS wins,
          SUM(losses) AS losses,
          SUM(draws) AS draws,
          1.0 * SUM(wins) / (SUM(wins) + SUM(losses) + SUM(draws)) AS win_percentage
        FROM
          fullparticipants fp
          LEFT JOIN uniquearchetypes ua ON ua.event_id = fp.event_id
          AND ua.player_name = fp.player_name
          INNER JOIN events e ON e.id = fp.event_id
          INNER JOIN formats f ON e.format_id = f.id
        WHERE
          fp.player_name = (
            SELECT
              player_name
            FROM
              playernames
            WHERE
              submitter_id = {user_id}
              AND discord_id = {discord_id}
          )
          AND e.event_date BETWEEN '{start_date}' AND '{end_date}'
          AND e.discord_id = {discord_id}
          AND e.game_id = {game.ID}
          {f'AND e.format_id = {format.ID}' if format else ''}
        GROUP BY
          {'f.name,' if not format else ''}
          archetype_played
      )
    '''

    print('Command:', command)
    cur.execute(command)
    rows = cur.fetchall()
    return rows

def GetTopPlayerData(discord_id,
                     game,
                     format,
                     start_date,
                     end_date):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command = f"""
    SELECT
      player_name,
      round(eventpercent * 100, 2) AS eventpercent,
      round(winpercent * 100, 2) AS winpercent,
      round(eventpercent * winpercent * 100, 2) AS Combined
    FROM
      (
        SELECT
          fp.player_name,
          COUNT(*) * 1.0 / (
            SELECT
              COUNT(*)
            FROM
              events
            WHERE
              event_date BETWEEN '{start_date}' AND '{end_date}'
              AND discord_id = {discord_id}
              AND game_id = {game.ID}
              AND format_id = {format.ID}
          ) AS eventpercent,
          sum(fp.wins) * 1.0 / (sum(fp.wins) + sum(fp.losses) + sum(fp.draws)) AS winpercent
        FROM
          events e
          INNER JOIN fullparticipants fp ON e.id = fp.event_id
        WHERE
          event_date BETWEEN '{start_date}' AND '{end_date}'
          AND discord_id = {discord_id}
          AND game_id = {game.ID}
          AND format_id = {format.ID}
        GROUP BY
          fp.player_name
      )
    ORDER BY
      combined DESC
    LIMIT
      10
    """

    cur.execute(command)
    rows = cur.fetchall()
    return rows