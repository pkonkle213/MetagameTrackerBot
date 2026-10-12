from pathlib import Path

import discord
from discord.ext import commands
from custom_errors import KnownError
from discord_messages import MessageUser
import settings
from data.store_data import DeleteStore

async def SyncCommands(bot: commands.Bot, commands_directory: Path):
  try: 
    for file in commands_directory.glob("*.py"):
      if file.name != "__init__.py":
        await bot.load_extension(f'commands.{file.name[:-3]}')
    try:
      sync_my_bot = await bot.tree.sync(guild=discord.Object(id=settings.BOTGUILDID))
      print(f'Synced {len(sync_my_bot)} command(s) to guild My Bot -> {settings.BOTGUILDID}')
    except Exception as error:
      print(f'Unable to sync commands to the bot guild:\n{error}')
    try:
      sync_global = await bot.tree.sync()
      print(f'Synced {len(sync_global)} commands globally')
    except Exception as error:
      print(f'Unable to sync commands globally:\n{error}')

  except Exception as error:
    print(f'Error syncing commands:\n{error}')