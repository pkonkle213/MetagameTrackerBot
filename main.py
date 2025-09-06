import pathlib
import discord
from discord.ext import commands, tasks
import datetime
from services.store_services import NewStoreRegistration
import settings
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
  data_guild_update.start()
  update_store_levels.start()
  await SyncCommands(bot, CMDS_DIR)

@bot.event
async def on_guild_join(guild:discord.Guild):
  """This event triggers when the bot joins a new guild (server)."""
  await NewStoreRegistration(bot, guild)

@tasks.loop(time=datetime.time(hour=8, minute=00, tzinfo=datetime.timezone.utc))
async def update_store_levels():
  """Store levels are updated every day at 8:00 AM UTC, 4:00 AM EST"""
  await SyncCommands(bot, CMDS_DIR)

@update_store_levels.before_loop
async def before_update_store_levels():
  await bot.wait_until_ready()

@tasks.loop(time=datetime.time(hour=14, minute=00, tzinfo=datetime.timezone.utc)) 
async def data_guild_update():
  """Every Friday at 10:00 AM EST, the data guild is updated with new data"""
  time_now = datetime.datetime.now(datetime.timezone.utc)
  if time_now.weekday() == 4:  # Check if it's Friday, 0 = Monday
    try:
      await UpdateDataGuild(bot)
    except Exception as error:
      print(f'Error updating data guild: {error}')

@data_guild_update.before_loop
async def before_scheduled_post():
  await bot.wait_until_ready()

bot.run(settings.DISCORDTOKEN)
