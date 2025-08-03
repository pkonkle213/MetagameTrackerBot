import pathlib
import discord
from discord.ext import commands, tasks
import datetime
import settings
import logging
from timedposts.automated_updates import UpdateDataGuild

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

bot = commands.Bot(command_prefix='?', intents=discord.Intents.all())
BASE_DIR = pathlib.Path(__file__).parent
CMDS_DIR = BASE_DIR / "commands"

@bot.event
async def on_ready():
  print(f'Logged on as {format(bot.user)}!')
  scheduled_post.start()
  try: 
    for file in CMDS_DIR.glob("*.py"):
      if file.name != "__init__.py":
        await bot.load_extension(f'commands.{file.name[:-3]}')

    sync_global = await bot.tree.sync()
    print(f'Synced {len(sync_global)} commands globally, allegedly')
    
    '''
    No commands need this for now
    for guild in GetLevel2Stores():
      sync_store = await bot.tree.sync(guild=guild)
      print(f'Syncing {len(sync_store)} commands for {guild.id}')
    '''
      
    sync_my_bot = await bot.tree.sync(guild=settings.BOTGUILD)
    print(f'Synced {len(sync_my_bot)} command(s) to guild My Bot -> {settings.BOTGUILD.id}')
    
    sync_test_guild = await bot.tree.sync(guild=settings.TESTSTOREGUILD)
    print(f'Synced {len(sync_test_guild)} command(s) to guild Test Guild -> {settings.TESTSTOREGUILD.id}')
    
    
  except Exception as error:
    print(f'Error syncing commands: {error}')

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
