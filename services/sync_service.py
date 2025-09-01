import discord
from custom_errors import KnownError
import settings
from data.store_data import GetAllStoreDiscordIds

async def SyncCommands(bot, commands_directory):
  try: 
    for file in commands_directory.glob("*.py"):
      if file.name != "__init__.py":
        await bot.load_extension(f'commands.{file.name[:-3]}')

    stores = GetAllStoreDiscordIds()
    if stores is None:
      raise KnownError("No stores found?")
    for guild_id in stores:
      sync_store = await bot.tree.sync(guild=discord.Object(id=guild_id))
      print(f'Synced {len(sync_store)} command(s) to guild {guild_id}')

    sync_global = await bot.tree.sync()
    print(f'Synced {len(sync_global)} commands globally, allegedly')

    sync_my_bot = await bot.tree.sync(guild=discord.Object(settings.BOTGUILDID))
    print(f'Synced {len(sync_my_bot)} command(s) to guild My Bot -> {settings.BOTGUILDID}')
    """
        sync_test_guild = await bot.tree.sync(guild=discord.Object(settings.TESTGUILDID))
        print(f'Synced {len(sync_test_guild)} command(s) to guild Test Guild -> {settings.TESTGUILDID}')
    """
  except Exception as error:
    print(f'Error syncing commands: {error}')