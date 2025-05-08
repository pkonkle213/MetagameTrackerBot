import discord
import data_translation
from game_mapper import GetGameOptions
import settings
import logging
from discord.ext import commands
from attendance_report import GetStoreAttendance
from demo_functions import NewDemo
from unknown_archetypes import GetAllUnknown
from select_menu_bones import SelectMenu
from game_mapper import AddStoreGameMap
from format_mapper import AddStoreFormatMap, GetFormatOptions
from claim_result import ClaimResult
from report_event import SubmitData
from metagame_report import GetMyMetagame
import interaction_data
from store_data_download import GetDataReport
from output_builder import BuildTableOutput
from player_win_record import PlayRecord
from register_store import RegisterNewStore, SetPermissions
from store_approval import ApproveMyStore, DisapproveMyStore

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

bot = commands.Bot(command_prefix='?', intents=intents)

@bot.event
async def on_ready():
  print(f'Logged on as {format(bot.user)}!')

  try:
    sync_global = await bot.tree.sync()
    print(f'Synced {len(sync_global)} commands globally, allegedly')
    sync_my_bot = await bot.tree.sync(guild=settings.BOTGUILD)
    print(f'Synced {len(sync_my_bot)} command(s) to guild My Bot -> {settings.BOTGUILD.id}')
    sync_test_guild = await bot.tree.sync(guild=settings.TESTSTOREGUILD)
    print(f'Synced {len(sync_test_guild)} command(s) to guild Test Guild -> {settings.TESTSTOREGUILD.id}')
  except Exception as error:
    print(f'Error syncing commands: {error}')

@bot.event
async def on_message(message):
  if message.author == bot.user:
    return

  data = data_translation.ConvertMessageToParticipants(message.content)
  if data is not None:
    if not isSubmitter(message.guild, message.author):
      await ErrorMessage(f'{str(message.author).title()} ({message.author.id}) lacks the permission to submit data')
      return
    if not storeCanTrack(message.guild):
      await ErrorMessage(f'{str(message.guild).title()} ({message.guild.id}) is not approved to track data')
      return

    await message.channel.send(f'Attempting to add {len(data)} participants an event')
    await message.delete()
    output = await SubmitData(bot, message, data)
    await message.channel.send(output)



#TODO: Double check these are needed and accurate
def isOwner(interaction: discord.Interaction):
  userid = interaction.user.id
  ownerid = interaction.guild.owner_id if interaction.guild else None
  return userid == ownerid

def isPhil(interaction: discord.Interaction):
  return interaction.user.id == settings.PHILID

def isSubmitter(guild, author):
  role = discord.utils.find(lambda r: r.name == 'MTSubmitter', guild.roles)
  return role in author.roles

def storeCanTrack(guild):
  store = interaction_data.GetStore(guild.id)
  return store is not None and store.ApprovalStatus

async def MessageUser(msg, userId, file=None):
  user = await bot.fetch_user(userId)
  if file is None:
    await user.send(f'{msg}')
  else:
    await user.send(f'{msg}', file=file)

async def MessageChannel(msg, guildId, channelId):
  server = bot.get_guild(int(guildId))
  if server is None:
    raise Exception(f'Server {guildId} not found')
  channel = server.get_channel(int(channelId))
  if channel is None:
    raise Exception(f'Channel {channelId} not found')
  if not isinstance(channel, discord.TextChannel):
    raise Exception(f'Channel {channelId} is not a text channel')

  await channel.send(f'{msg}')

#TODO: This is a mess, needs to be refactored
async def Error(interaction, error):
  command = interaction.command.name
  text = interaction.message.content if interaction.message else ''
  error_message = f'''
  {interaction.user.display_name} ({interaction.user.id}) got an error: {error}
  Command: {command}
  Text: {text}
  '''
  await ErrorMessage(error_message)
  await interaction.response.send_message('Something went wrong, it has been reported. Please try again later.', ephemeral=True)

async def ErrorMessage(msg):
  await MessageChannel(msg, settings.BOTGUILD.id, settings.ERRORCHANNELID)

async def ApprovalMessage(msg):
  await MessageChannel(msg, settings.BOTGUILD.id, settings.APPROVALCHANNELID)

@bot.tree.command(name="getbot",
                     description="Display the url to get the bot",
                     guild=settings.BOTGUILD)
async def GetBot(interaction: discord.Interaction):
  await interaction.response.send_message(f'Here is the link to my bot: {settings.MYBOTURL}')

@GetBot.error
async def GetBot_error(interaction: discord.Interaction, error):
  await Error(interaction, error)

@bot.tree.command(name="getsop",
                     description="Display the url to get the bot",
                     guild=settings.BOTGUILD)
async def GetSOP(interaction: discord.Interaction):
  await interaction.response.send_message(f'Here is the link to my bot: {settings.SOPURL}')

@GetSOP.error
async def GetSOP_error(interaction: discord.Interaction, error):
  await Error(interaction, error)

@bot.tree.command(name="feedback",
                     description="Provide feedback on the bot")
async def Feedback(interaction: discord.Interaction):
  await interaction.response.send_message(f'Follow this link: {settings.FEEDBACKURL}', ephemeral=True)

@Feedback.error
async def Feedback_error(interaction: discord.Interaction, error):
  await Error(interaction, error)

@bot.tree.command(name="atest",
                     description="The new thing I want to test",
                     guild=settings.TESTSTOREGUILD)
async def ATest(interaction: discord.Interaction):
  ...
  

@ATest.error
async def ATest_error(interaction: discord.Interaction, error):
  await Error(interaction, error)

@bot.tree.command(name="register",
                     description="Register your store",
                     guild=settings.TESTSTOREGUILD)
@discord.app_commands.check(isOwner)
async def Register(interaction: discord.Interaction,
                   store_name: str):
  """
  Parameters
  ----------
  store_name: string
    The name of the store
  """
  await interaction.response.defer()
  store = RegisterNewStore(interaction, store_name)
  await SetPermissions(interaction)
  await MessageUser(f'{store.StoreName.title()} has registered to track their data. DiscordId: {store.DiscordId}', settings.PHILID)
  await MessageChannel(f'{store.StoreName.title()} has registered to track their data. DiscordId: {store.DiscordId}', settings.BOTGUILD.id, settings.APPROVALCHANNELID)
  await interaction.followup.send(f'Registered {store_name.title()} with discord {store.DiscordName.title()} with owner {interaction.user}')

@Register.error
async def register_error(interaction: discord.Interaction, error):
  await interaction.followup.send('Unable to register the store. This has been reported')
  await Error(interaction, error)

#TODO: I think GameCategoryMaps and FormatChannelMaps should include the discordID simply so if a store is deleted, the maps are deleted too
#This could also be good to create a complex primary key with (discordid, channelid) or (discordid, categoryid) as I'm not sure if channelid or categoryid are unique across multiple discord guilds
@bot.tree.command(name='mapgame',
                     description='Map your category to a game',
                     guild=settings.TESTSTOREGUILD)
@discord.app_commands.checks.has_role("Owner")
async def AddGameMap(interaction: discord.Interaction):
  await interaction.response.defer(ephemeral=True)
  message = 'Please select a game'
  placeholder = 'Choose a game'
  dynamic_options = GetGameOptions()
  result = await SelectMenu(interaction, message, placeholder, dynamic_options)
  output = AddStoreGameMap(interaction, result)
  await interaction.followup.send(output, ephemeral=True)

@AddGameMap.error
async def AddGameMap_error(interaction: discord.Interaction, error):
  await Error(interaction, error)

@bot.tree.command(name='mapformat',
                     description='Map your channel to a format',
                     guild=settings.TESTSTOREGUILD)
@discord.app_commands.checks.has_role("Owner")
async def AddFormatMap(interaction: discord.Interaction):
  await interaction.response.defer(ephemeral=True)
  message = 'Please select a format'
  placeholder = 'Choose a format'
  dynamic_options = GetFormatOptions(interaction)
  result = await SelectMenu(interaction, message, placeholder, dynamic_options)
  output = AddStoreFormatMap(interaction, result)
  await interaction.followup.send(output, ephemeral=True)

@AddFormatMap.error
async def AddFormatMap_error(interaction: discord.Interaction, error):
  await Error(interaction, error)

@bot.tree.command(name="submitcheck",
                     description="To test if you can submit data",
                     guild=settings.TESTSTOREGUILD)
async def SubmitCheck(interaction: discord.Interaction):
  if not isSubmitter(interaction.guild, interaction.user):
    await interaction.response.send_message('You don\'t have the MTSubmitter role. Please contact your discord\'s owner')
  elif not storeCanTrack(interaction.guild):
    await interaction.response.send_message('This store isn\'t approved to submit data')
  else:
    await interaction.response.send_message('Everything looks good. Please reach out to Phil to test your data')

@SubmitCheck.error
async def SubmitCheck_error(interaction: discord.Interaction, error):
  await Error(interaction, error)

@bot.tree.command(name="metagame",
                     description="Get the metagame",
                     guild=settings.TESTSTOREGUILD)
async def Metagame(interaction: discord.Interaction,
                   start_date: str = '',
                   end_date: str = ''):
  """
  Parameters
  ----------
  start_date: string
    The start date of the metagame (MM/DD/YYYY)
  end_date: string
    The end date of the metagame (MM/DD/YYYY)
  """
  await interaction.response.defer()
  data, title, headers = GetMyMetagame(interaction, start_date, end_date)
  output = ''
  if data is None:
    output = 'No metagame data found for this store and format'
  else:
    output = BuildTableOutput(title, headers, data)
  await interaction.followup.send(output)

@Metagame.error
async def metagame_error(interaction: discord.Interaction, error):
  await Error(interaction, error)

@bot.tree.command(name="playrecord",
   description="Look up your win/loss record(s)",
   guild=settings.TESTSTOREGUILD)
async def WLDRecord(interaction: discord.Interaction,
  start_date: str = '',
  end_date: str = ''):
  """
  Parameters
  ----------
  start_date: string
    Beginning of Date Range (MM/DD/YYYY)
  end_date: string
    End of Date Range (MM/DD/YYYY)
  """
  await interaction.response.defer(ephemeral=True)
  data, title, header = PlayRecord(interaction, start_date, end_date)
  output = BuildTableOutput(title, header, data)
  await interaction.followup.send(output)
  
@WLDRecord.error
async def WLDRecord_error(interaction: discord.Interaction, error):
  await Error(interaction, error)

#TODO: Update to ask for date range
@bot.tree.command(name="attendance",
                     description="Get the attendance for the last 8 weeks",
                     guild=settings.TESTSTOREGUILD)
async def Attendance(interaction: discord.Interaction):
  await interaction.response.defer()
  data, title, headers = GetStoreAttendance(interaction)
  output = BuildTableOutput(title,
                            headers,
                            data)
  await interaction.followup.send(output)

@Attendance.error
async def attendance_error(interaction: discord.Interaction, error):
  await Error(interaction, error)






































@bot.tree.command(name="demo",
                     description="Set up the database for a demonstration",
                     guild=settings.BOTGUILD)
async def Demo(interaction: discord.Interaction):
  await interaction.response.defer()
  NewDemo()
  await interaction.followup.send('All set up!')


@Demo.error
async def demo_error(interaction: discord.Interaction, error):
  await Error(interaction, error)



#TODO: Should this instead get a date range and default to the last 8 weeks instead of quarters?
@bot.tree.command(name="topplayers",
                     description="Get the top players of the format",
                     guild=settings.TESTSTOREGUILD)
@discord.app_commands.checks.has_role("MTSubmitter")
async def TopPlayers(interaction: discord.Interaction,
                     year: discord.app_commands.Range[int, 2000] = 0,
                     quarter: discord.app_commands.Range[int, 1, 4] = 0,
                     top: discord.app_commands.Range[int, 1, 10] = 10):
  """
  Parameters
  ----------
  year: int
    The year to get the top players for
  quarter: int
    The quarter to get the top players for
  top: int
    The number of top players to get
  """
  await interaction.response.defer(ephemeral=True)
  game_name = interaction.channel.category.name
  discord_id = interaction.guild.id
  format_name = interaction.channel.name
  output = data_translation.GetTopPlayers(discord_id,
                                          game_name,
                                          format_name,
                                          year,
                                          quarter,
                                          top)
  await interaction.followup.send(output)


@TopPlayers.error
async def topplayers_error(interaction: discord.Interaction, error):
  await Error(interaction, error)

@bot.tree.command(name='approvestore',
                     description='Approve a store to track',
                     guild=settings.BOTGUILD)
@discord.app_commands.check(isPhil)
async def ApproveStore(interaction: discord.Interaction, discord_id: str):
  await interaction.response.defer()
  discord_id_int = int(discord_id)
  store = ApproveMyStore(discord_id_int)
  await MessageUser(f'{store.StoreName.title()} has been approved to track metagame data!', store.OwnerId)
  await interaction.followup.send(f'{store.StoreName.title()} is now approved to track their data')

@ApproveStore.error
async def ApproveStore_error(interaction: discord.Interaction, error):
  await Error(interaction, error)

@bot.tree.command(name='unknown',
                     description='Get the unknown archetypes for a date range',
                     guild=settings.TESTSTOREGUILD)
async def IntoTheUnknown(interaction: discord.Interaction,
                         start_date: str = '',
                         end_date: str = ''):
  """
  Parameters
  ----------
  start_date: string
    Beginning of Date Range (MM/DD/YYYY)
  end_date: string
    End of Date Range (MM/DD/YYYY)
  """
  await interaction.response.defer(ephemeral=True)
  data, title, headers = GetAllUnknown(interaction, start_date, end_date)
  output = BuildTableOutput(title, headers, data)
  await interaction.followup.send(output)

@bot.tree.command(name='disapprovestore',
                     description='Disapprove a store to track',
                     guild=settings.BOTGUILD)
@discord.app_commands.check(isPhil)
async def DisapproveStore(interaction: discord.Interaction, discord_id: str):
  discord_id_int = int(discord_id)
  store = DisapproveMyStore(discord_id_int)
  await interaction.response.send_message(f'Store {store.StoreName.title()} ({store.DiscordId}) no longer approved to track')

#TODO: This needs to be broken up into smaller functions
#1) Submit the data to inputtracker
#2) Check to see if the event reporting has hit a new milestone
@bot.tree.command(name='claim',
                     description='Enter your deck archetype',
                     guild=settings.TESTSTOREGUILD)
async def Claim(interaction: discord.Interaction,
                player_name: str,
                archetype: str,
                date: str = ''):
  """
  Parameters
  ----------
  player_name: string
    Your name in Companion
  archetype: string
    The deck archetype you played
  date: string
    Date of event (MM/DD/YYYY)
  """
  await interaction.response.defer(ephemeral=True)
  output = ClaimResult(interaction, player_name, archetype, date)
  await interaction.followup.send(output)


@Claim.error
async def Claim_error(interaction: discord.Interaction, error):
  await Error(interaction, error)

#TODO: Is there a better way to require a date be inputted?
#https://discord.com/developers/docs/reference#message-formatting
@bot.tree.command(name='downloaddata',
                     description='Download the data for a store for a date range',
                     guild=settings.TESTSTOREGUILD)
@discord.app_commands.check(isOwner)
async def DownloadData(interaction: discord.Interaction,
                       start_date: str = '',
                       end_date: str = ''):
  """
  Parameters
  ----------
  start_date: string
    Beginning of Date Range (MM/DD/YYYY)
  end_date: string
    End of Date Range (MM/DD/YYYY)
  """
  await interaction.response.defer(ephemeral=True)
  guild =interaction.guild
  if guild is None:
    raise Exception('No guild found')
  discord_id = guild.id
  file = GetDataReport(discord_id, start_date, end_date)
  if file is None:
    await interaction.followup.send('No data found for this store')
  await MessageUser(f'Here is the data for {guild.name}',
                    interaction.user.id,
                    file)
  await interaction.followup.send('The data for the store will arrive by message')

@DownloadData.error
async def DownloadData_error(interaction: discord.Interaction, error):
  await Error(interaction, error)

bot.run(settings.DISCORDTOKEN, log_handler=handler, log_level=logging.WARNING)
