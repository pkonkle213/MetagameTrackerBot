import pathlib
import discord
from discord.ext import commands, tasks
import datetime
from services.store_services import NewStoreRegistration
import settings
import logging
from timedposts.automated_updates import UpdateDataGuild
from services.sync_service import SyncCommands

intents = discord.Intents.all()
intents.message_content = True
intents.members = True
intents.guilds = True
bot = commands.Bot(command_prefix='?', intents=intents)

BASE_DIR = pathlib.Path(__file__).parent
CMDS_DIR = BASE_DIR / "commands"

@bot.event
async def on_ready():
  print(f'Logged on as {format(bot.user)}!')
  scheduled_post.start()
  update_store_levels.start()
  await SyncCommands(bot, CMDS_DIR)

@bot.event
async def on_guild_join(guild:discord.Guild):
  """
  This event triggers when the bot joins a new guild (server).
  """
  await NewStoreRegistration(bot, guild)

#This should start at 08:00 UTC, which is 4:00 AM EST
@tasks.loop(time=datetime.time(hour=8, minute=00, tzinfo=datetime.timezone.utc))
async def update_store_levels():
  await SyncCommands(bot, CMDS_DIR)

@update_store_levels.before_loop
async def before_update_store_levels():
  await bot.wait_until_ready()

#This should start at #14:00 UTC, which is 10:00 AM EST
@tasks.loop(time=datetime.time(hour=14, minute=00, tzinfo=datetime.timezone.utc)) 
async def scheduled_post():
  time_now = datetime.datetime.now(datetime.timezone.utc)
  if time_now.weekday() == 4:  # Check if it's Friday, 0 = Monday
    try:
      await UpdateDataGuild(bot)
    except Exception as error:
      print(f'Error updating data guild: {error}')

@scheduled_post.before_loop
async def before_scheduled_post():
  await bot.wait_until_ready()

bot.run(settings.DISCORDTOKEN)
