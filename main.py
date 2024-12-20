import discord
from discord.ext import commands
from discord.ui import Select, View
from discord import app_commands
import os
from dotenv.main import load_dotenv
import myCommands
import newDatabase
from io import BytesIO
import outputBuilder
import tupleConversions

load_dotenv()
SHEETSURL = os.getenv('SHEETSURL')
MYBOTURL = os.getenv('MYBOTURL')
PHILID = int(os.getenv('PHILID'))
CBUSGUILDID = int(os.getenv('COLUMBUSGUILDID'))
TESTGUILDID = int(os.getenv('TESTGUILDID'))
GUILDID = int(os.getenv('BOTGUILDID'))
BOTGUILD = discord.Object(id=GUILDID)
CBUSGUILD = discord.Object(id=CBUSGUILDID)
TESTSTOREGUILD = discord.Object(id=TESTGUILDID)
SOPURL = os.getenv('SOPURL')
ERRORID = int(os.getenv('BOTERRORCHANNELID'))
APPROVALID = int(os.getenv('BOTAPPROVALCHANNELID'))


class Client(commands.Bot):

  async def on_ready(self):
    print(f'Logged on as {format(self.user)}!')

    try:
      other = await self.tree.sync()
      print(f'Synced {len(other)} commands globally, allegedly')
      synced = await self.tree.sync(guild=BOTGUILD)
      print(f'Synced {len(synced)} command(s) to guild Bot Guild -> {BOTGUILD.id}')
      #For when/if we can link with the Columbus MTG discord
      #synced = await self.tree.sync(guild=CBUSGUILD)
      #print(f'Synced {len(synced)} command(s) to guild Bot Guild -> {CBUSGUILD.id}')
      synced = await self.tree.sync(guild=TESTSTOREGUILD)
      print(f'Synced {len(synced)} command(s) to guild Bot Guild -> {TESTSTOREGUILD.id}')
    except Exception as e:
      print(f'Error syncing commands: {e}')

  async def on_message(self, message):
    if message.author == self.user:
      return

    command = message.content.split()[0].upper()
    if command == '$ADDRESULTS' and ((storeCanTrack and isSubmitter) or
                                     (isPhil and isMyGuild)):
      results = message.content.split('\n')[1:]
      await message.channel.send(f'Attempting to add {len(results)} results...')

      output = myCommands.AddResults(message.guild.id, GUILDID, results,
                                     message.author.id)
      await message.channel.send(output)
      await message.delete()


intents = discord.Intents.default()
intents.message_content = True
client = Client(command_prefix='?', intents=intents)


def isOwner(interaction: discord.Interaction):
  return interaction.user.id == interaction.guild.owner_id


def isMyGuild(interaction: discord.Interaction):
  return interaction.guild_id == GUILDID


def isPhil(interaction: discord.Interaction):
  return interaction.user.id == PHILID


def isCBUSMTG(interaction: discord.Interaction):
  return interaction.guild_id == CBUSGUILDID


def isSubmitter(interaction: discord.Interaction):
  if interaction.user.id == PHILID or isOwner(interaction):
    return True
  discord_id = interaction.guild_id
  submitters = newDatabase.GetSubmitters(discord_id)
  print("Submitters: ", submitters)
  print(submitters)
  return interaction.user.id in submitters


def storeCanTrack(interaction: discord.Interaction):
  store = myCommands.GetStore(interaction.guild_id)
  if store is None:
    return False
  return store.ApprovalStatus


async def MessageUser(msg, userId):
  user = await client.fetch_user(userId)
  await user.send(f'{msg}')


async def MessageUserFile(msg, userId, file):
  user = await client.fetch_user(userId)
  await user.send(f'{msg}', file=file)


async def MessageChannel(msg, guildId, channelId):
  server = client.get_guild(int(guildId))
  channel = server.get_channel(int(channelId))
  await channel.send(f'{msg}')


async def Error(interaction, error):
  await ErrorMessage(f'Error: {error}')
  await interaction.response.send_message(
      'Something went wrong, it has been reported. Please try again later.',
      ephemeral=True)


async def ErrorMessage(msg):
  await MessageChannel(msg, GUILDID, ERRORID)


async def ApprovalMessage(msg):
  await MessageChannel(msg, GUILDID, APPROVALID)


@client.tree.command(name="getbot",
                     description="Display the url to get the bot",
                     guild=BOTGUILD)
@app_commands.checks.has_role("Owner")
@app_commands.check(isOwner)
async def GetBot(interaction: discord.Interaction):
  await interaction.response.send_message(MYBOTURL, ephemeral=True)


@GetBot.error
async def GetBot_error(interaction: discord.Interaction, error):
  await Error(interaction, error)


@client.tree.command(name="getsheets",
                     description="Display the url to get the sheets companion")
@app_commands.checks.has_role("Owner")
@app_commands.check(isOwner)
async def GetSheets(interaction: discord.Interaction):
  await interaction.response.send_message(SHEETSURL, ephemeral=True)


@GetSheets.error
async def GetSheets_error(interaction: discord.Interaction, error):
  await Error(interaction, error)


@client.tree.command(name="getsop",
                     description="Display the url to get the SOP")
@app_commands.checks.has_role("Owner")
@app_commands.check(isOwner)
async def GetSOP(interaction: discord.Interaction):
  await interaction.response.send_message(SOPURL, ephemeral=True)


@GetSOP.error
async def GetSOP_error(interaction: discord.Interaction, error):
  await Error(interaction, error)


@client.tree.command(name="register", description="Register your store")
@app_commands.checks.has_role("Owner")
@app_commands.check(isOwner)
async def Register(interaction: discord.Interaction, store_name: str):
  if store_name == '':
    await interaction.response.send_message('Please provide a store name',
                                            ephemeral=True)
  else:
    store_name = store_name.upper()
    discord_id = interaction.guild_id
    discord_name = str(interaction.guild).upper()
    owner = interaction.user.id
    store = tupleConversions.Store(store_name, discord_id, discord_name, owner,
                                   False)
    newDatabase.AddStore(store)
    await MessageUser(
        f'{store.Name.title()} has registered to track their data. DiscordId: {store.DiscordId}',
        PHILID)
    await MessageChannel(
        f'{store.Name.title()} has registered to track their data. DiscordId: {store.DiscordId}',
        GUILDID, APPROVALID)
    await interaction.response.send_message(
        f'Registered {store_name.title()} with discord {discord_name.title()} with owner {interaction.user}'
    )


@Register.error
async def register_error(interaction: discord.Interaction, error):
  await Error(interaction, error)


@client.tree.command(name="metagame", description="Get the metagame")
async def Metagame(interaction: discord.Interaction,
                   format: str = '',
                   start_date: str = '',
                   end_date: str = ''):
  discord_id = interaction.guild_id
  game = interaction.channel.category.name.upper()
  if discord_id == CBUSGUILDID:
    game = 'MAGIC'
    discord_id = 0
  if format == '':
    format = interaction.channel.name.upper()
  else:
    format = format.upper()
  output = myCommands.GetMetagame(discord_id, game, format, start_date,
                                  end_date)
  await interaction.response.send_message(output)


@Metagame.error
async def metagame_error(interaction: discord.Interaction, error):
  await Error(interaction, error)


#TODO: Should this assume game and format?
@client.tree.command(
    name="recentevents",
    description="Get the recent events and their attendance for this store")
async def RecentEvents(interaction: discord.Interaction):
  game = interaction.channel.category.name.upper()
  mappedgame = newDatabase.GetGameName(game)
  if mappedgame is None:
    await ErrorMessage(f'Game {game} not mapped in {interaction.guild.name}')
    raise Exception(f'Game {game} not found or mapped')
  format = interaction.channel.name.upper()
  discord_id = interaction.guild.id
  output = myCommands.FindEvents(discord_id)
  await interaction.response.send_message(output)


@RecentEvents.error
async def recentevents_error(interaction: discord.Interaction, error):
  await Error(interaction, error)


#Output when no results should be indicitave that there wasn't an appropriate event that day
@client.tree.command(
    name="participants",
    description="Get the participants of an event based on channel name")
@app_commands.checks.has_role("Owner")
async def Participants(interaction: discord.Interaction, date: str):
  game = interaction.channel.category.name.upper()
  format = interaction.channel.name.upper()
  owner = interaction.guild.owner_id
  output = myCommands.GetPlayersInEvent(owner, game, date, format)
  await interaction.response.send_message(output, ephemeral=True)


@Participants.error
async def participants_error(interaction: discord.Interaction, error):
  await Error(interaction, error)


@client.tree.command(name="topplayers",
                     description="Get the top players of the format")
@app_commands.checks.has_role("Owner")
async def TopPlayers(interaction: discord.Interaction,
                     year: app_commands.Range[int, 2000],
                     quarter: app_commands.Range[int, 1, 4],
                     top: app_commands.Range[int, 1, 10] = 0):
  game = interaction.channel.category.name
  format = interaction.channel.name
  discord_id = interaction.guild.id
  output = myCommands.GetTopPlayers(discord_id, game, format, year, quarter)
  await interaction.response.send_message(output, ephemeral=True)


@TopPlayers.error
async def topplayers_error(interaction: discord.Interaction, error):
  await Error(interaction, error)

@client.tree.command(name="getcolumns", description="Get the columns for a table",guild=TESTSTOREGUILD)
async def GetColumns(interaction: discord.Interaction, table: str):
  output = newDatabase.GetColumnNames(table)
  print(output)
  await interaction.response.send_message('This seems cool', ephemeral=True)

@client.tree.command(
    name="test", description="Relays all information about channel to Phil")
@app_commands.checks.has_role("Owner")
@app_commands.check(isOwner)
async def Test(interaction: discord.Interaction):
  output = outputBuilder.DiscordInfo(interaction)
  await MessageUser(output, PHILID)
  await interaction.response.send_message('Information has been sent to Phil')


@Test.error
async def test_error(interaction: discord.Interaction, error):
  await Error(interaction, error)


@client.tree.command(name='updaterow',
                     description='Update a row in the database')
@app_commands.checks.has_role("Owner")
@app_commands.check(isOwner)
async def UpdateRow(interaction: discord.Interaction, old_row: str,
                    new_row: str):
  print('Old row', old_row)
  print('New row', new_row)
  await interaction.response.send_message(
      f'Updating row {old_row} with {new_row}')
  output = myCommands.UpdateDataRow(old_row, new_row, interaction.user.id)


@UpdateRow.error
async def updaterow_error(interaction: discord.Interaction, error):
  await Error(interaction, error)


@client.tree.command(name='addgamemap',
                     description='Add a game map to the database')
@app_commands.checks.has_role("Owner")
async def AddGameMap(interaction: discord.Interaction):
  games_list = newDatabase.GetAllGames()
  game_options = []
  for game in games_list:
    game_options.append(
        discord.SelectOption(label=game[0].title(), value=game[0]))
  select = Select(placeholder='Choose a game', options=game_options)

  async def my_callback(interaction):
    actual_name = select.values[0]
    used_name = interaction.channel.category.name.upper()
    output = myCommands.AddGameMap(used_name, actual_name)
    await interaction.response.send_message(output, ephemeral=True)
    return select.values[0]

  select.callback = my_callback
  view = View()
  view.add_item(select)
  await interaction.response.send_message('Please select a game', view=view)


@AddGameMap.error
async def addgamemap_error(interaction: discord.Interaction, error):
  await Error(interaction, error)


@client.tree.command(name='approvestore',
                     description='Approve a store to track',
                     guild=BOTGUILD)
@app_commands.checks.has_role("Owner")
@app_commands.check(isPhil)
async def ApproveStore(interaction: discord.Interaction, discord_id: str):
  discord_id_int = int(discord_id)
  store = myCommands.ApproveStore(discord_id_int)
  await MessageUser(
      f'{store.Name.title()} has been approved to track metagame data!',
      store.Owner)
  await interaction.response.send_message(
      f'{store.Name.title()} is now approved to track their data')


@ApproveStore.error
async def ApproveStore_error(interaction: discord.Interaction, error):
  await Error(interaction, error)


@client.tree.command(name='disapprovestore',
                     description='Disapprove a store to track',
                     guild=BOTGUILD)
@app_commands.checks.has_role("Owner")
@app_commands.check(isPhil)
async def DisapproveStore(interaction: discord.Interaction, discord_id: str):
  discord_id_int = int(discord_id)
  store = myCommands.DisapproveStore(discord_id_int)
  await interaction.response.send_message(
      f'Store {store.Name} ({store.DiscordId}) no longer approved to track')


@DisapproveStore.error
async def DisapproveStore_error(interaction: discord.Interaction, error):
  await Error(interaction, error)


@client.tree.command(name='getallstores',
                     description='View All Stores information',
                     guild=BOTGUILD)
@app_commands.checks.has_role("Owner")
@app_commands.check(isPhil)
async def GetAllStores(interaction: discord.Interaction):
  await interaction.response.send_message('Displaying all stores information',
                                          ephemeral=True)


@GetAllStores.error
async def GetAllStores_error(interaction: discord.Interaction, error):
  await Error(interaction, error)


@client.tree.command(name='events',
                     description='Get attendance for stores holding events',
                     guild=CBUSGUILD)
async def GetStoreEvents(interaction: discord.Interaction):
  format = interaction.channel.name.upper()
  output = myCommands.GetStoresByGameFormat('MAGIC', format)
  await interaction.response.send_message(output)


@GetStoreEvents.error
async def GetStoreEvents_error(interaction: discord.Interaction, error):
  await Error(interaction, error)


@client.tree.command(name='download',
                     description='Downloads the Database',
                     guild=BOTGUILD)
@app_commands.check(isPhil)
async def DownloadDatabase(interaction: discord.Interaction):
  tables = ['datarows', 'gamenamemaps', 'stores']
  for table in tables:
    data = newDatabase.GetData(table)
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
    content = b'\n'.join(as_bytes)
    file = discord.File(BytesIO(content), filename=f'{table}.csv')
    await MessageUserFile('Message', PHILID, file)

  await interaction.response.send_message(
      'Database has been downloaded and messaged')


@DownloadDatabase.error
async def DownloadDatabase_error(interaction: discord.Interaction, error):
  await Error(interaction, error)


client.run(os.getenv('DISCORDTOKEN'))
