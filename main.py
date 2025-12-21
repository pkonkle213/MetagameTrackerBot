import contextlib
import pytz
import pathlib
import datetime
import discord
from discord.ext import commands, tasks
import settings
from timedposts.automated_paid_users import UpdatePaidUsers
from timedposts.automated_check_events import EventCheck
from services.store_services import NewStoreRegistration
from timedposts.automated_updates import UpdateDataGuild
from services.sync_service import SyncCommands

intents = discord.Intents.all()
intents.message_content = True
intents.members = True
intents.guilds = True
bot = commands.Bot(command_prefix='?', intents=intents)

BASE_DIR = pathlib.Path(__file__).parent
CMDS_DIR = BASE_DIR / "commands"

TIME_ZONE = pytz.timezone('US/Eastern')


@bot.event
async def on_ready():
  print(f'Logged on as {format(bot.user)}!')
  data_guild_update.start()
  find_the_unknown.start()
  sync_paid_users.start()
  await SyncCommands(bot, CMDS_DIR)
  print('Synced commands. Good to go')


@bot.event
async def on_guild_join(guild: discord.Guild):
  """This event triggers when the bot joins a new guild (server)."""
  await NewStoreRegistration(bot, guild)


@tasks.loop(time=datetime.time(hour=18, minute=00, tzinfo=TIME_ZONE))
async def find_the_unknown():
  """Every day at 6:00 PM EST, the bot will check for events that are 3 days old and have unknown archetypes."""
  await EventCheck(bot)


@find_the_unknown.before_loop
async def before_find_the_unknown():
  await bot.wait_until_ready()


@tasks.loop(minutes=5)
async def sync_paid_users():
  """Every 5 minutes, the bot will sync the paid users for command permission"""
  with contextlib.suppress(Exception):
    UpdatePaidUsers()


@sync_paid_users.before_loop
async def before_sync_paid_users():
  await bot.wait_until_ready()


@tasks.loop(time=datetime.time(hour=10, minute=00, tzinfo=TIME_ZONE))
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
