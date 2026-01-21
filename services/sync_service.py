import discord
from custom_errors import KnownError
from discord_messages import MessageUser
import settings
from data.store_data import DeleteStore, GetAllStoreDiscordIds

async def SyncCommands(bot, commands_directory):
  try: 
    for file in commands_directory.glob("*.py"):
      if file.name != "__init__.py":
        await bot.load_extension(f'commands.{file.name[:-3]}')

    stores = GetAllStoreDiscordIds()
    if stores is None:
      raise KnownError("No stores found?")
    for guild_id in stores:
      try:
        sync_store = await bot.tree.sync(guild=discord.Object(id=guild_id))
        print(f'Synced {len(sync_store)} command(s) to guild {guild_id}')
      except Exception as error:
        await MessageUser(bot,
                          f'Unable to sync commands to guild {guild_id}: {error}. Deleting store from database.',
                          settings.PHILID)
        DeleteStore(guild_id)

    sync_global = await bot.tree.sync()
    print(f'Synced {len(sync_global)} commands globally')

    sync_my_bot = await bot.tree.sync(guild=discord.Object(settings.BOTGUILDID))
    print(f'Synced {len(sync_my_bot)} command(s) to guild My Bot -> {settings.BOTGUILDID}')
    
    sync_test_guild = await bot.tree.sync(guild=discord.Object(settings.TESTGUILDID))
    print(f'Synced {len(sync_test_guild)} command(s) to guild Test Guild -> {settings.TESTGUILDID}')
    
  except Exception as error:
    print(f'Error syncing commands: {error}')