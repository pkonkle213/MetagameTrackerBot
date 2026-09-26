from datetime import date

from psycopg import AsyncConnection
from psycopg.rows import class_row

from settings import DATABASE_URL
from tuple_conversions import Format, Game, PersonalMatchupRows


async def GetPersonalMatchups(
    user_id: int,
    discord_id: int,
    game: Game,
    format: Format,
    start_date: date,
    end_date: date,
) -> list[PersonalMatchupRows]:
    async with (
        await AsyncConnection.connect(DATABASE_URL) as conn,
        conn.cursor(row_factory=class_row(PersonalMatchupRows)) as cur,
    ):
        command = f"""
        WITH
          criteria AS (
            SELECT
              %s AS user_id,
              %s AS discord_id,
              %s AS game_id,
              %s AS format_id,
              %s AS start_date,
              %s AS end_date
          ),
          all_events AS (
            --This is where I'll need to inject different code for stores and hubs
            SELECT
              e.id AS event_id,
              e.discord_id
            FROM
              events e
              INNER JOIN criteria c ON e.discord_id = c.discord_id
              AND e.game_id = c.game_id
              AND e.format_id = c.format_id
              AND e.event_date >= c.start_date
              AND e.event_date <= c.end_date
          ),
          player_pairings AS (
            SELECT
              INITCAP(COALESCE(uap.archetype_played, 'Unknown')) AS player_archetype,
              INITCAP(COALESCE(uao.archetype_played, 'Unknown')) AS opponent_archetype,
              result
            FROM
              full_pairings fp
              INNER JOIN all_events ae ON ae.event_id = fp.event_id
              INNER JOIN player_names pn ON upper(pn.player_name) = upper(fp.player_name)
              AND pn.discord_id = ae.discord_id
              INNER JOIN criteria c ON pn.submitter_id = c.user_id
              LEFT JOIN unique_archetypes uap ON upper(uap.player_name) = upper(fp.player_name)
              AND uap.event_id = fp.event_id
              LEFT JOIN unique_archetypes uao ON upper(uao.player_name) = upper(fp.opponent_name)
              AND uao.event_id = fp.event_id
            WHERE
              fp.opponent_name != 'Bye'
          ),
          player_archetype_ranks AS (
            SELECT
              player_archetype,
              ROW_NUMBER() OVER (
                ORDER BY
                  COUNT(*) DESC
              ) AS player_archetype_rank
            FROM
              player_pairings
            GROUP BY
              player_archetype
            ORDER BY
              COUNT(*) DESC
          ),
          full_metagame AS (
            SELECT
              INITCAP(COALESCE(ua.archetype_played, 'Unknown')) AS archetype_played,
              ROW_NUMBER() OVER (
                ORDER BY
                  COUNT(*) DESC
              ) AS metagame_rank
            FROM
              full_standings fs
              INNER JOIN all_events ae ON ae.event_id = fs.event_id
              LEFT JOIN unique_archetypes ua ON ua.event_id = fs.event_id
              AND upper(ua.player_name) = upper(fs.player_name)
            GROUP BY
              INITCAP(COALESCE(ua.archetype_played, 'Unknown'))
            ORDER BY
              COUNT(*) DESC
          ),
          matchup_records AS (
            SELECT
              pp.player_archetype,
              pp.opponent_archetype,
              SUM(
                CASE
                  WHEN pp.result = 'WIN' THEN 1
                  ELSE 0
                END
              ) AS wins,
              SUM(
                CASE
                  WHEN pp.result = 'LOSS' THEN 1
                  ELSE 0
                END
              ) AS losses,
              SUM(
                CASE
                  WHEN pp.result = 'DRAW' THEN 1
                  ELSE 0
                END
              ) AS draws,
              COUNT(*) AS total_games
            FROM
              player_pairings pp
            GROUP BY
              player_archetype,
              opponent_archetype
          )
        SELECT
          mr.player_archetype,
          par.player_archetype_rank,
          mr.opponent_archetype,
          fm.metagame_rank,
          mr.total_games,
          ROUND(
            100.0 * mr.wins / (mr.wins + mr.losses + mr.draws),
            2
          ) AS win_percent
        FROM
          matchup_records mr
          INNER JOIN player_archetype_ranks par ON par.player_archetype = mr.player_archetype
          INNER JOIN full_metagame fm ON fm.archetype_played = mr.opponent_archetype
        ORDER BY
          player_archetype_rank,
          metagame_rank
        """

        await cur.execute(
            command, [user_id, discord_id, game.id, format.id, start_date, end_date]
        )
        rows = await cur.fetchall()
        return rows
