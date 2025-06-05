import discord
from discord.ext import commands
import settings
import logging
from attendance_report import GetStoreAttendance
from checks import isSubmitter
from claim_result import ClaimResult, CheckEventPercentage, OneEvent
from custom_errors import KnownError
from data_translation import ConvertMessageToParticipants, Participant, Round
from demo_functions import NewDemo
from flag_bad_word import AddBadWord, Offenders
from format_mapper import AddStoreFormatMap, GetFormatOptions
from game_mapper import AddStoreGameMap, GetGameOptions
from interaction_data import GetInteractionData, GetStore
from text_input import GetTextInput
from metagame_report import GetMyMetagame
from output_builder import BuildTableOutput
from player_win_record import PlayRecord
from register_store import AssignStoreOwnerRoleInBotGuild, RegisterNewStore, SetPermissions
from report_event import SubmitData
from select_menu_bones import SelectMenu
from store_approval import ApproveMyStore, DisapproveMyStore
from store_data_download import GetDataReport
from top_players import GetTopPlayers
from unknown_archetypes import GetAllUnknown
from store_event_reported.events_reported import GetMyEventsReported

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

#TODO: Right now, an event can be submitted by rounds AND in total. I need a way to prevent both from happening. Maybe another column in events to mark how it was submitted??
@bot.event
async def on_message(message):
  if message.author == bot.user:
    return

  data = ConvertMessageToParticipants(message.content)
  if data is not None:
    if not isSubmitter(message.guild, message.author, 'MTSubmitter'):
      await ErrorMessage(f'{str(message.author).title()} ({message.author.id}) lacks the permission to submit data')
      return
    store = GetStore(message.guild.id)
    if store is None or not store.ApprovalStatus:
      await ErrorMessage(f'{str(message.guild).title()} ({message.guild.id}) is not approved to track data')
      return
    date = await GetTextInput(bot, message)
    print('Outside date:', date)
    print('Outside type of date:', type(date))
    
    message_type = 'participants' if isinstance(data[0], Participant) else 'tables'

    await message.channel.send(f"Attempting to add {len(data)} {message_type} to event")
    msg  = f"Guild name: {message.guild.name}\n"
    msg += f"Guild id: {message.guild.id}\n"
    msg += f"Channel name: {message.channel.name}\n"
    msg += f"Channel id: {message.channel.id}\n"
    msg += f"Author name: {message.author.name}\n"
    msg += f"Author id: {message.author.id}\n"
    msg += f"Message content:\n{message.content}"
    await MessageChannel(msg, settings.BOTGUILD.id, settings.BOTEVENTINPUTID)
    print(message.content)
    await message.delete()
    output = await SubmitData(message, data, date)
    await message.channel.send(output)

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
  channel = server.get_channel(int(channelId))
  if channel is None:
    print(f'Channel {channelId} not found')
    raise Exception(f'Channel {channelId} not found')
  if not isinstance(channel, discord.TextChannel):
    raise Exception(f'Channel {channelId} is not a text channel')

  await channel.send(f'{msg}')

async def Error(interaction, error):
  #TODO: The error isn't being caught correctly here. I need to figure out how to do that
  #This is to keep error messages clear and concise, and especially specific for me
  if isinstance(error, KnownError):
    await interaction.followup.send(error.message)
  else:
    #TODO: Traceback is still not giving me a clear message of what happened.
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
    await interaction.followup.send('Something went wrong, it has been reported. Please try again later.', ephemeral=True)

async def ErrorMessage(msg):
  await MessageChannel(msg,
                       settings.BOTGUILD.id,
                       settings.ERRORCHANNELID)

async def ApprovalMessage(msg):
  await MessageChannel(msg,
                       settings.BOTGUILD.id,
                       settings.APPROVALCHANNELID)

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

#Something I'd like to test:
#@discord.app_commands.AppCommand(default_member_permissions=0)
#?????
@bot.tree.command(name="atest",
  description="The new thing I want to test",
  guild=settings.TESTSTOREGUILD)
async def ATest(interaction: discord.Interaction):
  await interaction.response.defer()
  result = 'Hi!'

  if not result:
    await interaction.followup.send("Nope, something didn't work")
  else:
    await interaction.followup.send("Yep, it worked")

@ATest.error
async def ATest_error(interaction: discord.Interaction, error):
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
    The bad word or phrase to ban
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
  await SetPermissions(interaction)
  await AssignStoreOwnerRoleInBotGuild(bot, interaction)
  await MessageUser(f'{store.StoreName.title()} has registered to track their data. DiscordId: {store.DiscordId}', settings.PHILID)
  await MessageChannel(f'{store.StoreName.title()} has registered to track their data. DiscordId: {store.DiscordId}', settings.BOTGUILD.id, settings.APPROVALCHANNELID)
  await interaction.followup.send(f'Registered {store_name.title()} with discord {store.DiscordName.title()} with owner {interaction.user}')

#TODO: More specific error catching needs to be in the command.
#Catching errors like this is removing the type of error and more details that I could be using
@Register.error
async def register_error(interaction: discord.Interaction, error):
  await interaction.followup.send('Unable to register the store. This has been reported')
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
                  description="To test if you can submit data")
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

#TODO: Is there a better way to require a date be inputted?
#https://discord.com/developers/docs/reference#message-formatting
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
                  description='Enter your deck archetype')
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
  archetype = archetype.strip().encode('ascii', 'ignore').decode('ascii')
  print('Sending:', player_name, archetype, date)
  archetype_submitted, event = await ClaimResult(interaction, player_name, archetype, date)
  if archetype_submitted is None:
    await interaction.followup.send('Unable to submit the archetype. Please try again later.')
  else:
    #id like this to say 'thank you for submitting the archetype for [date] [format]'
    await interaction.followup.send(f"Thank you for submitting the archetype for {event.EventDate.strftime('%B %d')}'s event!")
    
  followup = CheckEventPercentage(event)
  if followup:
    if followup[1]:
      title, headers, data = OneEvent(event)
      output = BuildTableOutput(title, headers, data)
      await MessageChannel(output, interaction.guild_id, interaction.channel_id)
    else:
      await MessageChannel(followup[0], interaction.guild_id, interaction.channel_id)

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

@bot.tree.command(name='myeventsrepored',
                  description='See how well your events are reported',
                 guild=settings.TESTSTOREGUILD)
@discord.app_commands.checks.has_role('MTSubmitter')
async def MyEventsReported(interaction: discord.Interaction):
  await interaction.response.defer(ephemeral=True)
  data, title, headers = GetMyEventsReported(interaction)
  output = BuildTableOutput(title, headers, data)
  await interaction.followup.send(output)

bot.run(settings.DISCORDTOKEN, log_handler=handler, log_level=logging.DEBUG)
