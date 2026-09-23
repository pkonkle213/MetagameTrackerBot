from typing import NamedTuple
from psycopg.rows import class_row
from settings import DATABASE_URL
from psycopg import AsyncConnection

class DataGuildChannels(NamedTuple):
    channel_id:int
    category_id: int

async def GetDataChannels(data_guild_id:int) -> list[DataGuildChannels]:
    async with await AsyncConnection.connect(DATABASE_URL) as conn:
        async with conn.cursor(row_factory=class_row(DataGuildChannels)) as cur:
            command = '''
            SELECT
                channel_id,
                category_id
            FROM
                format_channel_maps fcm
                INNER JOIN formats f ON fcm.format_id = f.id
                INNER JOIN Games g ON g.id = f.game_id
                INNER JOIN game_category_maps gcm ON (
                    gcm.game_id = g.id
                    AND gcm.discord_id = fcm.discord_id
                )
            WHERE fcm.discord_id = %s
            '''
    
            criteria = [data_guild_id]
            await cur.execute(command, criteria)
            rows = await cur.fetchall()
            return rows