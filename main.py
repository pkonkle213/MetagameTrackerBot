import pathlib
import discord
from discord.ext import commands, tasks
import datetime
import settings
import logging
from timedposts.automated_updates import UpdateDataGuild
from services.sync_service import SyncCommands

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

bot = commands.Bot(command_prefix='?', intents=discord.Intents.all())
BASE_DIR = pathlib.Path(__file__).parent
CMDS_DIR = BASE_DIR / "commands"

@bot.event
async def on_ready():
  print(f'Logged on as {format(bot.user)}!')
  scheduled_post.start()
  await SyncCommands(bot, CMDS_DIR)

@tasks.loop(time=datetime.time(hour=14, minute=00, tzinfo=datetime.timezone.utc)) #14:00 UTC is 10:00 AM EST
async def scheduled_post():
  time_now = datetime.datetime.now(datetime.timezone.utc)
  if time_now.weekday() == 4:  # Check if it's Friday, 0 = Monday
    await UpdateDataGuild(bot)

@scheduled_post.before_loop
async def before_scheduled_post():
  await bot.wait_until_ready()
  
if settings.DISCORDTOKEN:
  bot.run(settings.DISCORDTOKEN, log_handler=handler, log_level=logging.DEBUG)
