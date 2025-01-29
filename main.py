import date_functions
import discord
from discord.ext import commands
from discord.ui import Select, View
from discord import app_commands
import os
import data_manipulation
import database_connection
import settings
from io import BytesIO
import tuple_conversions

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

    data = data_manipulation.ConvertMessageToParticipants(message.content.split('\n'))
    if storeCanTrack(message.guild) and isSubmitter(message.guild, message.author) and data is not None:
      await message.channel.send(f'Attempting to add {len(data)} participants to the event')
      #TODO: This should call data_manipulation and not skip right to the database
      game_id = database_connection.GetGame(message.guild.id, message.channel.category.name.upper())[0]
      if game_id is None:
        #TODO: If none then ask
        await message.channel.send('Error: Game not found. Please map a game to this category')
        return

      #TODO: Ask for format based on game, allow 'other' option for manual input
      format = message.channel.name.replace('-',' ').upper()
      format_id = database_connection.GetFormat(game_id, format)[0]
      #TODO: If none then create

      #TODO: Confirm date
      date_of_event = date_functions.GetToday()

      event_id = 0
      try:
        event_id = data_manipulation.CreateEvent(date_of_event, message.guild.id, game_id, format_id)
      #TODO: This needs to be a more specific error catch
      except Exception as error:
        await message.channel.send('There was an error creating the event. It has been reported')
        await ErrorMessage(error)
        return

      output = data_manipulation.AddResults(event_id, data, message.author.id)
      await message.delete()
      await message.channel.send(output)

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
client = Client(command_prefix='?', intents=intents)


def checkIsOwner(interaction: discord.Interaction):
  userid = interaction.user.id
  ownerid = interaction.guild.owner_id
  return userid == ownerid

def isOwner(interaction: discord.Interaction):
  userid = interaction.user.id
  ownerid = interaction.guild.owner_id
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


async def Error(interaction, error):
  command = interaction.command
  message = interaction.message
  error_message =  f'{interaction.user.display_name} ({interaction.user.id}) got an error: {error}\n'
  error_message += f'Command: {str(command)}\n'
  error_message += f'Message: {message}\n'
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
  await interaction.response.send_message(settings.MYBOTURL, ephemeral=True)


@GetBot.error
async def GetBot_error(interaction: discord.Interaction, error):
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

  store_name = store_name.upper()
  discord_id = interaction.guild.id
  discord_name = interaction.guild.name.upper()
  owner_id = interaction.guild.owner.id
  owner_name = interaction.guild.owner.display_name.upper()
  store = tuple_conversions.Store(discord_id,
                                  discord_name,
                                  store_name,
                                  owner_id,
                                  owner_name,
                                  False)
  #TODO: This needs to call data_manipulation and not skip straight to the database
  #TODO: data_manipulation can catch the error
  database_connection.AddStore(store)
  if store is not None:
    await SetPermissions(interaction)
    await MessageUser(f'{store.StoreName.title()} has registered to track their data. DiscordId: {store.DiscordId}',
                      settings.PHILID)
    await MessageChannel(f'{store.StoreName.title()} has registered to track their data. DiscordId: {store.DiscordId}',
                         settings.BOTGUILD.id,
                         settings.APPROVALCHANNELID)
    await interaction.response.send_message(f'Registered {store_name.title()} with discord {discord_name.title()} with owner {interaction.user}')
  else:
    await interaction.response.send_message('Unable to register the store. This has been reported')
    await Error(interaction, 'Store unable to be registered')


@Register.error
async def register_error(interaction: discord.Interaction, error):
  await Error(interaction, error)

async def SetPermissions(interaction):
  owner = interaction.guild.owner
  mtsubmitter_role = discord.utils.find(lambda r: r.name == 'MTSubmitter', interaction.guild.roles)
  owner_role = discord.utils.find(lambda r: r.name == 'Owner', interaction.guild.roles)

  if owner_role is None:
    owner_role = await interaction.guild.create_role(name="Owner", permissions=discord.Permissions.all())
  await owner.add_roles(owner_role)

  if mtsubmitter_role is None:
    mtsubmitter_role = await interaction.guild.create_role(name="MTSubmitter", permissions=discord.Permissions.all())
  await owner.add_roles(mtsubmitter_role)

  permissions = discord.PermissionOverwrite(send_messages=False)
  everyone_role = interaction.guild.default_role
  await interaction.channel.set_permissions(everyone_role, overwrite=permissions)
  await interaction.response.send_message('Done?')

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
  game = database_connection.GetGame(discord_id, interaction.channel.category.name.upper())
  #TODO: What if game not found
  format = database_connection.GetFormat(game[0], interaction.channel.name.replace('-',' ').upper())
  if format is None:
    await interaction.followup.send('Error: Format not found.')

  output = data_manipulation.GetMetagame(discord_id,
                                         game,
                                         format,
                                         start_date,
                                         end_date)

  await interaction.followup.send(output)


@Metagame.error
async def metagame_error(interaction: discord.Interaction, error):
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
  game = interaction.channel.category.name.upper()
  discord_id = interaction.guild.id
  format = interaction.channel.name.upper()
  output = data_manipulation.GetTopPlayers(discord_id,
                                           game,
                                           format,
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
  print(games_list)
  game_options = []
  for game in games_list:
    game_options.append(discord.SelectOption(label=game[1].title(), value=game[0]))
  select = Select(placeholder='Choose a game', options=game_options)

  async def my_callback(interaction):
    game_id = select.values[0]
    used_name = interaction.channel.category.name.upper()
    output = data_manipulation.AddGameMap(discord_id, game_id, used_name)
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
  discord_id_int = int(discord_id)
  store = data_manipulation.ApproveStore(discord_id_int)
  await MessageUser(f'{store.StoreName.title()} has been approved to track metagame data!',
      store.OwnerId)
  await interaction.response.send_message(
      f'{store.StoreName.title()} is now approved to track their data')


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
  name: string
    Your name in Companion
  archetype: string
    The deck archetype you played
  date: string
    Date of event (MM/DD/YYYY)
  """
  await interaction.response.defer(ephemeral=True)
  actual_date = date_functions.convert_to_date(date)
  if actual_date is None:
    actual_date = date_functions.GetToday()

  player_name = player_name.upper()
  game = interaction.channel.category.name.upper()
  game_id = database_connection.GetGame(interaction.guild.id, game)[0]
  format = interaction.channel.name.upper()
  format_id = database_connection.GetFormat(game_id, format)[0]
  store_discord = interaction.guild.id
  event_id = database_connection.GetEventId(store_discord, actual_date, game_id, format_id)
  updater_id = interaction.user.id
  updater_name = interaction.user.display_name.upper()
  archetype = archetype.upper()

  success_check = data_manipulation.Claim(event_id,
                                          player_name,
                                          archetype,
                                          updater_id,
                                          updater_name,
                                          store_discord)
  output = ''
  print('Success?', success_check)
  if success_check:
    output = 'Thank you for submitting your archetype!'
  else:
    output = 'Error: Something went wrong. It\'s been reported'
    message_parts = []
    message_parts.append('Error claiming archetype:')
    message_parts.append(f'Name: {player_name}')
    message_parts.append(f'Archetype: {archetype}')
    message_parts.append(f'Date: {actual_date}')
    message_parts.append(f'Format: {format}')
    message_parts.append(f'Store Discord: {store_discord}')
    message_parts.append(f'Updater Discord: {updater_id}')

    await ErrorMessage('\n'.join(message_parts))

  await interaction.followup.send(output)


@Claim.error
async def Claim_error(interaction: discord.Interaction, error):
  await Error(interaction, error)

#TODO: Adjust the list of tables as they've changed
#Is there a script that will do this for me?!
@client.tree.command(name='download',
                     description='Downloads the Database',
                     guild=settings.BOTGUILD)
@app_commands.check(checkIsPhil)
async def DownloadDatabase(interaction: discord.Interaction):
  tables = ['datarows', 'gamenamemaps', 'stores', 'inputtracker']
  for table in tables:
    data = database_connection.GetData(table)
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
    file = discord.File(BytesIO(content), filename=f'{table}.csv')
    await MessageUser('Message', settings.PHILID, file)

  await interaction.response.send_message('Database has been downloaded and messaged')


@DownloadDatabase.error
async def DownloadDatabase_error(interaction: discord.Interaction, error):
  await Error(interaction, error)


client.run(os.getenv('DISCORDTOKEN'))