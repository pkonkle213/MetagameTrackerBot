import discord
from discord.ext import commands, tasks
import datetime
import settings
import logging
from services.store_attendance import GetStoreAttendance
from checks import isSubmitter
from services.claim_result import ClaimResult, CheckEventPercentage, OneEvent
from custom_errors import KnownError
from data_translation import ConvertMessageToParticipants, Participant, Round
from services.demonstration_functions import NewDemo
from services.ban_word import AddBadWord, Offenders
from services.formats import AddStoreFormatMap, GetFormatOptions
from services.game_mapper import AddStoreGameMap, GetGameOptions
from interaction_data import GetInteractionData
from timedposts.automated_updates import UpdateDataGuild
from services.level_2_stores import GetLevel2Stores
from text_modal import SubmitDataModal
from services.metagame import GetMyMetagame
from output_builder import BuildTableOutput
from services.player_win_record import PlayRecord
from services.store_services import AssignStoreOwnerRoleInBotGuild, RegisterNewStore, SetPermissions, ApproveMyStore, DisapproveMyStore, AssignMTSubmitterRole
from services.add_results import SubmitData
from select_menu_bones import SelectMenu
from services.store_data_download import GetDataReport
from services.events_reported import GetMyEventsReported
from services.personal_matchups import PersonalMatchups
from services.top_players import GetTopPlayers
from services.unknown_archetypes import GetAllUnknown

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

bot = commands.Bot(command_prefix='?', intents=intents)

@bot.event
async def on_ready():
  print(f'Logged on as {format(bot.user)}!')
  scheduled_post.start()

  try: 
    sync_global = await bot.tree.sync()
    print(f'Synced {len(sync_global)} commands globally, allegedly')
    for guild in level2guilds:
      sync_store = await bot.tree.sync(guild=guild)
      print(f'Syncing {len(sync_store)} commands for {guild.id}')
    sync_my_bot = await bot.tree.sync(guild=settings.BOTGUILD)
    print(f'Synced {len(sync_my_bot)} command(s) to guild My Bot -> {settings.BOTGUILD.id}')
    sync_test_guild = await bot.tree.sync(guild=settings.TESTSTOREGUILD)
    print(f'Synced {len(sync_test_guild)} command(s) to guild Test Guild -> {settings.TESTSTOREGUILD.id}')
  except Exception as error:
    print(f'Error syncing commands: {error}')

@tasks.loop(time=datetime.time(hour=13, minute=0, tzinfo=datetime.timezone.utc))
async def scheduled_post():
  time_now = datetime.datetime.now(datetime.timezone.utc)
  if time_now.weekday() == 4:  # Check if it's Friday?
    await UpdateDataGuild(bot)

@scheduled_post.before_loop
async def before_scheduled_post():
  await bot.wait_until_ready()
    
def isOwner(interaction: discord.Interaction):
  userid = interaction.user.id
  ownerid = interaction.guild.owner_id if interaction.guild else None
  return userid == ownerid

def isPhil(interaction: discord.Interaction):
  return interaction.user.id == settings.PHILID

async def MessageUser(msg, userId, file=None):
  user = await bot.fetch_user(userId)
  if file is None:
    await user.send(f'{msg}')
  else:
    await user.send(f'{msg}', file=file)

async def MessageChannel(msg, guildId, channelId):
  server = bot.get_guild(int(guildId))
  if server is None:
    print(f'Server {guildId} not found')
    raise Exception(f'Server {guildId} not found')
  if msg != '':
    channel = server.get_channel(int(channelId))
    if channel is None:
      print(f'Channel {channelId} not found')
      raise Exception(f'Channel {channelId} not found')
    if not isinstance(channel, discord.TextChannel):
      raise Exception(f'Channel {channelId} is not a text channel')

    await channel.send(f'{msg}')

async def Error(interaction, error, phil_message = ''):
  #TODO: Known errors should be caught within the command/method, not caught out here.
  if phil_message != '':
    await MessageUser(phil_message, settings.PHILID)
  print('Type of error:',type(error))
  if isinstance(error, commands.MissingRole):
    await interaction.followup.send("Sorry, you lack the right role to use this command.")
  elif isinstance(error, KnownError):
    await interaction.followup.send(error.message)
  else:
    error_message = f'''
    {interaction.user.display_name} ({interaction.user.id}) got an error: {error}
    Error Type: {type(error)}
    Error Details: {error.__dict__}
    Traceback: {error.__traceback__}
    Command Name: {interaction.command.name}
    Guild: {interaction.guild}
    Channel: {interaction.channel}
    User: {interaction.user}
    '''
    await ErrorMessage(error_message)

async def ErrorMessage(msg):
  await MessageChannel(msg,
                       settings.BOTGUILD.id,
                       settings.ERRORCHANNELID)

async def ApprovalMessage(msg):
  await MessageChannel(msg,
                       settings.BOTGUILD.id,
                       settings.APPROVALCHANNELID)

level2guilds = GetLevel2Stores()

async def Help(interaction: discord.Interaction):
  await interaction.response.send_message(f'Here is the link to my help: {settings.SOPURL}')

@bot.tree.command(name="getbot",
                  description="Display the url to get the bot",
                  guild=settings.BOTGUILD)
async def GetBot(interaction: discord.Interaction):
  await interaction.response.send_message(f'Here is the link to my bot: {settings.MYBOTURL}')

@bot.tree.command(name="getguild",
                  description="Display the invite to the bot's server")
async def GetGuild(interaction: discord.Interaction):
  await interaction.response.send_message(f'Here is the link to my server: {settings.MYBOTGUILDURL}')

@bot.tree.command(name='viewalldata',
                  description='Get an invite to my data hub with more stores')
async def ViewAllData(interaction: discord.Interaction):
  await interaction.response.send_message(f'Here is the link to my data hub: {settings.DATAHUBINVITE}')

@bot.tree.command(name="getsop",
                  description="Display the url to get the bot",
                  guild=settings.BOTGUILD)
async def GetSOP(interaction: discord.Interaction):
  await interaction.response.send_message(f'Here is the link to my bot: {settings.SOPURL}')

@bot.tree.command(name="feedback",
                  description="Provide feedback on the bot")
async def Feedback(interaction: discord.Interaction):
  await interaction.response.send_message(f'Follow this link: {settings.FEEDBACKURL}')

@bot.tree.command(name="atest",
                  description="The new thing I want to test",
                  guild=settings.TESTSTOREGUILD)
async def ATest(interaction: discord.Interaction):
  #ConvertName(name)
  #PrintInfo(interaction.command)
  #print('Result:', result)
  await interaction.response.send_message(f'Me: {interaction.user.mention}')

@bot.tree.command(name="submitdata",
                  description="Submitting your event's data")
@commands.has_role('MTSubmitter')
async def SubmitDataCommand(interaction: discord.Interaction):
  modal = SubmitDataModal()
  await interaction.response.send_modal(modal)
  await modal.wait()
  
  if not modal.is_submitted:
    await interaction.followup.send("SubmitData modal was dismissed or timed out. Please try again", ephemeral=True)
  else:
    data = ConvertMessageToParticipants(modal.submitted_message)
    if data is None:
      await interaction.followup.send("Unable to submit due to not recognizing the form data. Please try again", ephemeral=True)
      await ErrorMessage(modal.submitted_message)
    else:
      date = modal.submitted_date
  
      message_type = 'participants' if isinstance(data[0], Participant) else 'tables'

      await interaction.followup.send(f"Attempting to add {len(data)} {message_type} to event", ephemeral=True)
      msg  = f"Guild name: {interaction.guild.name}\n"
      msg += f"Guild id: {interaction.guild.id}\n"
      msg += f"Channel name: {interaction.channel.name}\n"
      msg += f"Channel id: {interaction.channel.id}\n"
      msg += f"Author name: {interaction.user.name}\n"
      msg += f"Author id: {interaction.user.id}\n"
      msg += f"Message content:\n{modal.submitted_message}"
      await MessageChannel(msg, settings.BOTGUILD.id, settings.BOTEVENTINPUTID)
      output = await SubmitData(interaction, data, date)
      await interaction.followup.send(output)

@SubmitDataCommand.error
async def SubmitDataCommand_error(interaction: discord.Interaction, error):
  await Error(interaction, error)

@bot.tree.command(name='addword',
                  description='Add a banned word')
@discord.app_commands.checks.has_role('MTSubmitter')
async def BadWord(interaction: discord.Interaction,
                   word:str):
  """
  Parameters
  ----------
  word: string
    The inappropriate word or phrase to ban
  """
  if len(word) < 3:
    await interaction.response.send_message('Word must be at least 3 characters long')
  else:
    await interaction.response.defer(ephemeral=True)
    check = AddBadWord(interaction, word)
    if check:
      await interaction.followup.send('Word added and offending archetypes disabled')
    else:
      await interaction.followup.send('Something went wrong. Please try again later.', ephemeral=True)

@BadWord.error
async def BadWord_error(interaction: discord.Interaction, error):
  await Error(interaction, error)

@bot.tree.command(name="register",
                  description="Register your store")
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
  if store is None:
    raise Exception('Unable to register store')
  await SetPermissions(interaction)
  await AssignStoreOwnerRoleInBotGuild(bot, interaction)
  await MessageUser(f'{store.StoreName.title()} has registered to track their data. DiscordId: {store.DiscordId}', settings.PHILID)
  await MessageChannel(f'{store.StoreName.title()} has registered to track their data. DiscordId: {store.DiscordId}', settings.BOTGUILD.id, settings.APPROVALCHANNELID)
  await interaction.followup.send(f'Registered {store_name.title()} with discord {store.DiscordName.title()} with owner {interaction.user}')

@Register.error
async def register_error(interaction: discord.Interaction, error):
  await interaction.followup.send('Unable to complete registration for the store. This has been reported')
  await Error(interaction, error)

@bot.tree.command(name='mapgame',
                  description='Map your category to a game')
@discord.app_commands.checks.has_role("MTSubmitter")
async def AddGameMap(interaction: discord.Interaction):
  await interaction.response.defer(ephemeral=True)
  message = 'Please select a game'
  placeholder = 'Choose a game'
  dynamic_options = GetGameOptions()
  result = await SelectMenu(interaction, message, placeholder, dynamic_options)
  output = AddStoreGameMap(interaction, result[0])
  await interaction.followup.send(output, ephemeral=True)

@AddGameMap.error
async def AddGameMap_error(interaction: discord.Interaction, error):
  await Error(interaction, error)

@bot.tree.command(name='mapformat',
                  description='Map your channel to a format')
@discord.app_commands.checks.has_role("MTSubmitter")
async def AddFormatMap(interaction: discord.Interaction):
  await interaction.response.defer(ephemeral=True)
  dynamic_options = GetFormatOptions(interaction)
  if dynamic_options is None or len(dynamic_options) == 0:
    await interaction.followup.send('No formats found for this game')
  else:
    message = 'Please select a format'
    placeholder = 'Choose a format'
    result = await SelectMenu(interaction, message, placeholder, dynamic_options)
    output = AddStoreFormatMap(interaction, result[0])
    await interaction.followup.send(output, ephemeral=True)

@AddFormatMap.error
async def AddFormatMap_error(interaction: discord.Interaction, error):
  await Error(interaction, error)

@bot.tree.command(name="submitcheck",
                  description="To test if you can submit data",
                  guild=settings.TESTSTOREGUILD)
async def SubmitCheck(interaction: discord.Interaction):
  await interaction.response.defer(ephemeral=True)
  issues = ['Issues I detect:']
  game, format, store, userId = GetInteractionData(interaction)
  if not store:
    issues.append('- Store not registered')
  if not store.ApprovalStatus:
    issues.append('- Store not approved for data submission')
  if not isSubmitter(interaction.guild, interaction.user, 'MTSubmitter'):
    issues.append("- You don't have the MTSubmitter role.")
  if not game:
    issues.append('- Category not mapped to a game')
  if not format:
    issues.append('- Channel not mapped to a format')

  if len(issues) == 1:
    await interaction.followup.send('Everything looks good. Please reach out to Phil to test your data')
  else:
    await interaction.followup.send('\n'.join(issues))

@SubmitCheck.error
async def SubmitCheck_error(interaction: discord.Interaction, error):
  await Error(interaction, error)

@bot.tree.command(name="metagame",
                  description="Get the metagame")
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
                  description="Look up your win/loss record(s)")
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

@bot.tree.command(name="attendance",
                  description="Get the attendance for a date range")
async def Attendance(interaction: discord.Interaction,
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
  await interaction.response.defer()
  data, title, headers = GetStoreAttendance(interaction, start_date, end_date)
  if data is None or len(data) == 0:
    await interaction.followup.send('No attendance data found for this store and/or format')
  else:
    output = BuildTableOutput(title,
                              headers,
                              data)
    await interaction.followup.send(output)

@Attendance.error
async def attendance_error(interaction: discord.Interaction, error):
  await Error(interaction, error)

@bot.tree.command(name="topplayers",
                  description="Get the top players of the format")
@discord.app_commands.checks.has_role("MTSubmitter")
async def TopPlayers(interaction: discord.Interaction,
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
  data, title, headers = GetTopPlayers(interaction,
                                       start_date,
                                       end_date)
  output = BuildTableOutput(title, headers, data)
  await interaction.followup.send(output)

@TopPlayers.error
async def topplayers_error(interaction: discord.Interaction, error):
  await Error(interaction, error)

@bot.tree.command(name='unknown',
                  description='See what archetypes still need submitted for a date range')
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
  await interaction.response.defer()
  data, title, headers = GetAllUnknown(interaction, start_date, end_date)
  if data is None or len(data) == 0:
    await interaction.followup.send('Congratulations! No unknown archetypes found for this format')
  else:
    output = BuildTableOutput(title, headers, data)
    await interaction.followup.send(output)

@IntoTheUnknown.error
async def IntoTheUnknown_error(interaction: discord.Interaction, error):
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
  await interaction.followup.send(f'{store.StoreName.title()} ({store.DiscordId}) is now approved to track their data')

@ApproveStore.error
async def ApproveStore_error(interaction: discord.Interaction, error):
  await Error(interaction, error)


@bot.tree.command(name='disapprovestore',
                     description='Disapprove a store to track',
                     guild=settings.BOTGUILD)
@discord.app_commands.check(isPhil)
async def DisapproveStore(interaction: discord.Interaction, discord_id: str):
  discord_id_int = int(discord_id)
  store = DisapproveMyStore(discord_id_int)
  await interaction.response.send_message(f'{store.StoreName.title()} ({store.DiscordId}) no longer approved to track')

@bot.tree.command(name='downloaddata',
                  description='Download the data for a store for a date range')
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
  title, file = GetDataReport(interaction, start_date, end_date)
  if file is None:
    await interaction.followup.send('No data found for this store')
  await MessageUser(title,
                    interaction.user.id,
                    file)
  await interaction.followup.send('The data for the store will arrive by message')

@DownloadData.error
async def DownloadData_error(interaction: discord.Interaction, error):
  await Error(interaction, error)

@bot.tree.command(name='claim',
                  description='Enter the deck archetype for a player and their last played event')
async def Claim(interaction: discord.Interaction,
                player_name: str,
                archetype: str,
                date: str):
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
  archetype = archetype.strip().encode('ascii', 'ignore').decode('ascii')
  try:
    archetype_submitted, event = await ClaimResult(interaction, player_name, archetype, date)
    if archetype_submitted is None:
      await interaction.followup.send('Unable to submit the archetype. Please try again later.')
    else:
      await interaction.followup.send(f"Thank you for submitting the archetype for {event.EventDate.strftime('%B %d')}'s event!")
    followup = CheckEventPercentage(event)
    if followup:
      if followup[1]:
        title, headers, data = OneEvent(event)
        output = BuildTableOutput(title, headers, data)
        await MessageChannel(output, interaction.guild_id, interaction.channel_id)
      else:
        await MessageChannel(followup[0], interaction.guild_id, interaction.channel_id)
  except KnownError as exception:
    phil_message = f'''
    Error in Claim: {exception.message}
    player_name = {player_name}
    archetype = {archetype}
    date = {date}
    '''
    await Error(interaction, exception, phil_message)
    await interaction.followup.send(exception.message, ephemeral=True)

@Claim.error
async def Claim_error(interaction: discord.Interaction, error):
  await Error(interaction, error)

@bot.tree.command(name='offenders',
                  description='See who has been flagged for bad words/phrases')
@discord.app_commands.checks.has_role('MTSubmitter')
async def StoreOffenders(interaction: discord.Interaction):
  await interaction.response.defer(ephemeral=True)
  data, title, headers = Offenders(interaction)
  output = BuildTableOutput(title, headers, data)
  await interaction.followup.send(output)

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

@bot.tree.command(name='eventsreported',
                  description='See how well events are reported',
                  guild=settings.BOTGUILD)
@discord.app_commands.check(isPhil)
async def MyEventsReported(interaction: discord.Interaction, discord_id:str = ''):
  '''
  Parameters:
  ----------
  discord_id: string
    The discord id of the store to check
  '''
  await interaction.response.defer()
  discord_id_int = 0
  if discord_id != '':
    discord_id_int = int(discord_id)
  data, title, headers = GetMyEventsReported(interaction, discord_id_int)
  output = BuildTableOutput(title, headers, data)
  await interaction.followup.send(output)

@MyEventsReported.error
async def MyEventsReported_error(interaction: discord.Interaction, error):
  await Error(interaction, error)

@bot.tree.command(name='personalmatchups',
                  description='See your matchups against archetypes in this format',
                  guilds=level2guilds)
async def PersonalMatchupReport(interaction: discord.Interaction,
                                start_date: str = '',
                                end_date: str = ''):
  await interaction.response.defer(ephemeral=True)
  data, title, headers = PersonalMatchups(interaction, start_date, end_date)
  output = BuildTableOutput(title, headers, data)
  print('Output:', output)
  await interaction.followup.send(output)

@PersonalMatchupReport.error
async def PersonalMatchupReport_error(interaction: discord.Interaction, error):
  await Error(interaction, error)

@bot.tree.command(name='assignmtsubmitter',
                  description='Assign the MTSubmitter role to a user',
                  guild=settings.BOTGUILD)
async def AssignMTSubmitter(interaction: discord.Interaction, user_id: str, guild_id: str):
  await interaction.response.defer()
  output = await AssignMTSubmitterRole(bot, user_id, guild_id)
  await interaction.followup.send(output)

@AssignMTSubmitter.error
async def AssignMTSubmitter_error(interaction: discord.Interaction, error):
  await Error(interaction, error)
  
if settings.DISCORDTOKEN:
  bot.run(settings.DISCORDTOKEN, log_handler=handler, log_level=logging.DEBUG)
