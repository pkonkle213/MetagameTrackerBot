import asyncpg
from settings import DATABASE_URL
from discord.ext import commands
from discord import Intents

class MetagameTrackerBot(commands.Bot):
  def __init__(self):
    intents = Intents.all()
    intents.message_content = True
    intents.members = True
    intents.guilds = True
    super().__init__(command_prefix="?", intents=intents)
    self.db_pool:asyncpg.Pool | None = None

  async def setup_hook(self):
    self.db_pool = await asyncpg.create_pool(
      dsn=DATABASE_URL
    )

  async def close(self):
    await super().close()
    if self.db_pool:
      await self.db_pool.close()