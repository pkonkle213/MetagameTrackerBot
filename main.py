import date_functions
import discord
from discord.ext import commands
from discord.ui import Select, View
from discord import NotificationLevel, app_commands
import os
import data_manipulation
import database_connection
import settings
from io import BytesIO

class Client(commands.Bot):

  async def on_ready(self):
    print(f'Logged on as {format(self.user)}!')

    try:
      sync_global = await self.tree.sync()
      print(f'Synced {len(sync_global)} commands globally, allegedly')
      sync_my_bot = await self.tree.sync(guild=settings.BOTGUILD)
      print(f'Synced {len(sync_my_bot)} command(s) to guild My Bot  -> {settings.BOTGUILD.id}')
      sync_test_guild = await self.tree.sync(guild=settings.TESTSTOREGUILD)
      print(f'Synced {len(sync_test_guild)} command(s) to guild Test Guild -> {settings.TESTSTOREGUILD.id}')
    except Exception as error:
      print(f'Error syncing commands: {error}')

  async def on_message(self, message):
    if message.author == self.user:
      return

    print('Content received:', message.content)
    data = data_manipulation.ConvertMessageToParticipants(message.content)
    if data is not None:
      print('Data received:', data)
      if not isSubmitter(message.guild, message.author):
        await ErrorMessage(f'{str(message.author)} ({message.author.id}) lacks the permission to submit data')
        return
      if not storeCanTrack(message.guild):
        await ErrorMessage(f'{str(message.guild)} ({message.guild.id}) is not approved to track data')
        return
      
      await message.channel.send(f'Attempting to add {len(data)} participants a new event')
      await message.delete()
      discord_id = message.guild.id
      game_name = message.channel.category.name.upper()
      game = data_manipulation.GetGame(discord_id, game_name)
      if game is None:
        await message.channel.send('Error: Game not found. Please map a game to this category')
        return

      format = ''
      if game.HasFormats:
        format = data_manipulation.GetFormat(discord_id, game, message.channel.name.replace('-',' ').upper())

      if format is None:
        await message.channel.send('Error: Format not found. Please map a format to this channel')
        return
      
      #TODO: Confirm date
      date_of_event = date_functions.GetToday()
      
      try:
        event = data_manipulation.GetEvent(discord_id, date_of_event, game, format)
        if event is None:
          event = data_manipulation.CreateEvent(date_of_event, message.guild.id, game, format)
      #TODO: This needs to be a more specific error catch
      except Exception as error:
        await message.channel.send('There was an error creating the event. It has been reported')
        await ErrorMessage(error)
        return

      output = data_manipulation.AddResults(event.ID, data, message.author.id)
      await message.channel.send(output)

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
client = Client(command_prefix='?', intents=intents)

def checkIsOwner(interaction: discord.Interaction):
  userid = interaction.user.id
  ownerid = interaction.guild.owner_id if interaction.guild else None
  return userid == ownerid

def isOwner(interaction: discord.Interaction):
  userid = interaction.user.id
  ownerid = interaction.guild.owner_id if interaction.guild else None
  return userid == ownerid

def isMyGuild(guild):
  return guild.id == settings.BOTGUILD.id

def checkIsPhil(interaction: discord.Interaction):
  return interaction.user.id == settings.PHILID

def isPhil(author):
  return author.id == settings.PHILID

def isSubmitter(guild, author):
  role = discord.utils.find(lambda r: r.name == 'MTSubmitter', guild.roles)
  return role in author.roles

def storeCanTrack(guild):
  store = data_manipulation.GetStore(guild.id)
  return store is not None and store.ApprovalStatus

async def MessageUser(msg, userId, file = None):
  user = await client.fetch_user(userId)
  if file is None:
    await user.send(f'{msg}')
  else:
    await user.send(f'{msg}', file = file)

async def MessageChannel(msg, guildId, channelId):
  server = client.get_guild(int(guildId))
  channel = server.get_channel(int(channelId))
  await channel.send(f'{msg}')

#TODO: This is a mess, needs to be refactored
async def Error(interaction, error):
  command = interaction.command.name
  error_message =  f'{interaction.user.display_name} ({interaction.user.id}) got an error: {error}\n'
  error_message += f'Command: {command}\n'
  await ErrorMessage(error_message)
  await interaction.response.send_message('Something went wrong, it has been reported. Please try again later.', ephemeral=True)


async def ErrorMessage(msg):
  await MessageChannel(msg, settings.BOTGUILD.id, settings.ERRORCHANNELID)


async def ApprovalMessage(msg):
  await MessageChannel(msg, settings.BOTGUILD.id, settings.APPROVALCHANNELID)

@client.tree.command(name="getbot",
   description="Display the url to get the bot",
   guild=settings.BOTGUILD)
async def GetBot(interaction: discord.Interaction):
  await interaction.response.send_message(f'Here is the link to my bot: {settings.MYBOTURL}')


@GetBot.error
async def GetBot_error(interaction: discord.Interaction, error):
  await Error(interaction, error)

@client.tree.command(name="getsop",
   description="Display the url to get the bot",
   guild=settings.BOTGUILD)
async def GetSOP(interaction: discord.Interaction):
  await interaction.response.send_message(f'Here is the link to my bot: {settings.SOPURL}')


@GetBot.error
async def GetSOP_error(interaction: discord.Interaction, error):
  await Error(interaction, error)

class FormatDropdown(discord.ui.View):
  def __init__(self, options):
    self.options = options
  
  answer = None
  
  @discord.ui.select(
    placeholder="Choose a format",
    min_values=1,
    max_values=1,
    options=[discord.SelectOption(label=game.Name,value=game.ID) for game in data_manipulation.GetAllGames()]
  )
  async def select_format(self, interaction: discord.Interaction, select: discord.ui.Select):
    self.answer = select.values
    self.stop()

#This is close, but the options aren't flexible.
#I'd like to present options accurate to the game that is being played
@client.tree.command(name="atest",description="The new thing I want to test",guild=settings.TESTSTOREGUILD)
async def ATest(interaction: discord.Interaction):
  options = [discord.SelectOption(label=game.Name,value=game.ID) for game in data_manipulation.GetAllGames()]
  view = FormatDropdown(options)

  await interaction.response.send_message(view=view)
  await view.wait()

  print('Answer:', view.answer)
  await interaction.response.send_message(f'You chose {view.answer[0]}')  

@client.tree.command(name="submitcheck", description="To test if yAou can submit data",guild=settings.TESTSTOREGUILD)
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

@client.tree.command(name="register", description="Register your store")
@app_commands.check(isOwner)
async def Register(interaction: discord.Interaction, store_name: str):
  """
  Parameters
  ----------
  store_name: string
    The name of the store
  """
  await interaction.response.defer()
  store_name = store_name.upper()
  discord_id = interaction.guild.id
  discord_name = interaction.guild.name.upper()
  owner_id = interaction.guild.owner.id
  owner_name = interaction.guild.owner.display_name.upper()
  try:
    store = data_manipulation.RegisterStore(discord_id, discord_name, store_name, owner_id, owner_name)
    await SetPermissions(interaction)
    await MessageUser(f'{store.StoreName.title()} has registered to track their data. DiscordId: {store.DiscordId}',
                      settings.PHILID)
    await MessageChannel(f'{store.StoreName.title()} has registered to track their data. DiscordId: {store.DiscordId}',
                         settings.BOTGUILD.id,
                         settings.APPROVALCHANNELID)
    await interaction.followup.send(f'Registered {store_name.title()} with discord {discord_name.title()} with owner {interaction.user}')
  except Exception as e:
    await interaction.followup.send('Unable to register the store. This has been reported')
    await Error(interaction, e)

@Register.error
async def register_error(interaction: discord.Interaction, error):
  await Error(interaction, error)

async def SetPermissions(interaction):
  owner = interaction.guild.owner
  mtsubmitter_role = discord.utils.find(lambda r: r.name == 'MTSubmitter', interaction.guild.roles)
  owner_role = discord.utils.find(lambda r: r.name == 'Owner', interaction.guild.roles)

  #TODO: This is giving me a "Missing Permissions" error even when manage_roles is true
  if owner_role is None:
    owner_role = await interaction.guild.create_role(name="Owner", permissions=discord.Permissions.all())
  await owner.add_roles(owner_role)

  if mtsubmitter_role is None:
    mtsubmitter_role = await interaction.guild.create_role(name="MTSubmitter", permissions=discord.Permissions.all())
  await owner.add_roles(mtsubmitter_role)

  permissions = discord.PermissionOverwrite(send_messages=False)
  everyone_role = interaction.guild.default_role
  await interaction.channel.set_permissions(everyone_role, overwrite=permissions)

#TODO: Update to be used in MetagameTrackerData guild 
@client.tree.command(name="metagame", description="Get the metagame")
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
  discord_id = interaction.guild_id
  game_name = interaction.channel.category.name
  format_name = interaction.channel.name

  output = data_manipulation.GetMetagame(discord_id,
                                         game_name,
                                         format_name,
                                         start_date,
                                         end_date)
  
  await interaction.followup.send(output)


@Metagame.error
async def metagame_error(interaction: discord.Interaction, error):
  await Error(interaction, error)

@client.tree.command(name="demo", description="Set up the database for a demonstration",guild=settings.BOTGUILD)
async def Demo(interaction: discord.Interaction):
  await interaction.response.defer()
  data_manipulation.Demo()
  await interaction.followup.send('All set up!')

@Demo.error
async def demo_error(interaction: discord.Interaction, error):
  await Error(interaction, error)

@client.tree.command(name="attendance", description="Get the attendance for the last 8 weeks")
async def Attendance(interaction: discord.Interaction):
  await interaction.response.defer()
  game_name = interaction.channel.category.name
  format_name = interaction.channel.name
  discord_id = interaction.guild_id
  output = data_manipulation.GetAttendance(discord_id, game_name, format_name)
  await interaction.followup.send(output)

@Attendance.error
async def attendance_error(interaction: discord.Interaction, error):
  await Error(interaction, error)

#TODO: Double check this works
@client.tree.command(name="topplayers",
                     description="Get the top players of the format")
@app_commands.checks.has_role("Owner")
async def TopPlayers(interaction: discord.Interaction,
                     year: app_commands.Range[int, 2000] = 0,
                     quarter: app_commands.Range[int, 1, 4] = 0,
                     top: app_commands.Range[int, 1, 10] = 10):
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
  output = data_manipulation.GetTopPlayers(discord_id,
                                           game_name,
                                           format_name,
                                           year,
                                           quarter,
                                           top)
  await interaction.followup.send(output)


@TopPlayers.error
async def topplayers_error(interaction: discord.Interaction, error):
  await Error(interaction, error)


@client.tree.command(name='addgamemap',
                     description='Add a game map to the database')
@app_commands.checks.has_role("Owner")
async def AddGameMap(interaction: discord.Interaction):
  discord_id = interaction.guild.id
  games_list = database_connection.GetAllGames()
  game_options = []
  for game in games_list:
    game_options.append(discord.SelectOption(label=game[1].title(), value=game[0]))
  select = Select(placeholder='Choose a game', options=game_options)

  async def my_callback(interaction):
    game_id = select.values[0]
    used_name = interaction.channel.category.name
    output = data_manipulation.AddGameMap(discord_id, game_id, used_name.upper())
    if output is None:
      await ErrorMessage(f'Unable to map {used_name} in discord {discord_id}')
      await interaction.response.send_message('Unable to map this game. It has been reported')
    else:
      await interaction.response.send_message(output, ephemeral=True)

  select.callback = my_callback
  view = View()
  view.add_item(select)
  await interaction.response.send_message('Please select a game', view=view)

@AddGameMap.error
async def addgamemap_error(interaction: discord.Interaction, error):
  await Error(interaction, error)


@client.tree.command(name='approvestore',
                     description='Approve a store to track',
                     guild=settings.BOTGUILD)
@app_commands.check(checkIsPhil)
async def ApproveStore(interaction: discord.Interaction, discord_id: str):
  await interaction.response.defer()
  discord_id_int = int(discord_id)
  store = data_manipulation.ApproveStore(discord_id_int)
  await MessageUser(f'{store.StoreName.title()} has been approved to track metagame data!',
      store.OwnerId)
  await interaction.followup.send(f'{store.StoreName.title()} is now approved to track their data')


@ApproveStore.error
async def ApproveStore_error(interaction: discord.Interaction, error):
  await Error(interaction, error)


@client.tree.command(name='disapprovestore',
                     description='Disapprove a store to track',
                     guild=settings.BOTGUILD)
@app_commands.check(checkIsPhil)
async def DisapproveStore(interaction: discord.Interaction, discord_id: str):
  discord_id_int = int(discord_id)
  store = data_manipulation.DisapproveStore(discord_id_int)
  await interaction.response.send_message(
      f'Store {store.StoreName.title()} ({store.DiscordId}) no longer approved to track')


@client.tree.command(name='claim', description='Enter your deck archetype')
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
  actual_date = date_functions.convert_to_date(date)
  
  player_name = player_name.upper()
  store_discord = interaction.guild.id
  game_name = interaction.channel.category.name
  format_name = interaction.channel.name
  updater_id = interaction.user.id
  updater_name = interaction.user.display_name.upper()
  archetype = archetype.upper()
  try:
    data_manipulation.Claim(actual_date,
                            game_name,
                            format_name,
                            player_name,
                            archetype,
                            updater_id,
                            updater_name,
                            store_discord)
    await interaction.followup.send('Thank you for submitting your archetype!')
    #TODO: This should be a custom error so that I can figure out what broke
  except Exception as ex:
    await interaction.followup.send(f'{player_name} was not found in that event. The name should match what was put into Companion')
    message_parts = []
    message_parts.append('Error claiming archetype:')
    message_parts.append(f'Name: {player_name}')
    message_parts.append(f'Discord Name: {updater_name}')
    message_parts.append(f'Archetype: {archetype}')
    message_parts.append(f'Date: {actual_date}')
    message_parts.append(f'Format: {format_name}')
    message_parts.append(f'Store Discord: {store_discord}')
    message_parts.append(f'Updater Discord: {updater_id}')
    message_parts.append(f'Error Message: {ex}')

    await ErrorMessage('\n'.join(message_parts))

@Claim.error
async def Claim_error(interaction: discord.Interaction, error):
  await Error(interaction, error)

@client.tree.command(name='downloaddata',
                     description='Download the data for a store for a date range')
@app_commands.check(isOwner)
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
  discord_id = interaction.guild.id
  data = data_manipulation.GetDataReport(discord_id, start_date, end_date)
  if data is None:
    await interaction.followup.send('No data found for this store')
  file = ConvertRowsToFile(data, 'MyStoreData')
  await MessageUser(f'Here is the data for {interaction.guild.name}', interaction.user.id, file)
  await interaction.followup.send('The data for the store will arrive by message')

def ConvertRowsToFile(data, filename):
  data_list = []
  for row in data:
    max = len(row) 
    row_string = ''
    for i in range(max):
      row_string += f'{row[i]}'
      if i != max - 1:
        row_string += ','
      else:
        row_string += '\n'

    data_list.append(row_string)

  as_bytes = map(str.encode, data_list)
  content = b''.join(as_bytes)
  return discord.File(BytesIO(content), filename=f'{filename}.csv')

@client.tree.command(name='download',
                     description='Downloads the Database',
                     guild=settings.BOTGUILD)
@app_commands.check(checkIsPhil)
async def DownloadDatabase(interaction: discord.Interaction):
  tables = ['cardgames', 'gamenamemaps', 'stores', 'inputtracker', 'events', 'formats', 'participants']
  for table in tables:
    data = database_connection.GetData(table)
    file = ConvertRowsToFile(data, table)
    await MessageUser('Message', settings.PHILID, file)

  await interaction.response.send_message('Database has been downloaded and messaged')


@DownloadDatabase.error
async def DownloadDatabase_error(interaction: discord.Interaction, error):
  await Error(interaction, error)


client.run(os.getenv('DISCORDTOKEN'))
