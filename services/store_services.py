import discord
from custom_errors import KnownError
from data.store_data import RegisterStore
from services.game_mapper_services import GetGameOptions
from data.formats_data import GetFormatsByGameId
from services.input_services import ConvertInput
from settings import BOTGUILDID

def NewStoreRegistration(guild: discord.Guild):
  #Starting to register new store
  if guild is None:
    raise KnownError('No guild found')
  #I know this works
  #store = AddStoreToDatabase(guild)
  #print('Store:', store)
  MapCategoriesAndChannels(guild)
  """
  MessageOwnerMappings()
  CreateAndAssignMTSubmitterRoleInGuild()
  AssignStoreOwnerRoleInBotGuild()
  """
  
def AddStoreToDatabase(guild: discord.Guild):
  """Adds the store to the database"""
  owner = guild.owner
  if owner is None:
    raise KnownError('No owner found')
  store = RegisterStore(guild.id,
                            guild.name,
                            '',
                            owner.id,
                            owner.name)
  if store is None:
    raise KnownError('Unable to register store')
  return store

def MatchGame(category_name, games):
  """Matches the category name to a game"""
  for game in games:
    if game.Name.lower() in category_name.lower():
      return game

def MatchFormat(formats, channel_name):
  """Matches the channel name to a format"""
  for format in formats:
    if format.Name.lower() in channel_name.lower():
      return format

def MapCategoriesAndChannels(guild: discord.Guild):
  """Sequentially maps the categories and channels in the guild"""
  print('Mapping categories and channels')
  output = "Category and Channel Names:\n"
  games = GetGameOptions()

  for category in guild.categories:
    game = MatchGame(category.name, games)
    print('Game:', game, 'Category:', category.name, category.id)
    if game is not None:
      formats = GetFormatsByGameId(game.ID)
    
      for channel in category.channels:
        format = MatchFormat(formats, channel.name)
        if format is not None:
          print('Format:', format, 'Channel:', channel.name, channel.id)

  if len(output) > 2000: # Discord message limit
    # If the output is too long, send it in chunks or a file
    print("Output too long to display directly. Check console or consider saving to file.")
    print(output) # Print to console for full output
  else:
    print(f"```\n{output}\n```")

def RegisterNewStore(interaction: discord.Interaction, store_name: str):
  name_of_store = ConvertInput(store_name)

  guild = interaction.guild
  if guild is None:
    raise KnownError('No guild found')
  discord_id = guild.id
  discord_name = ConvertInput(guild.name)
  
  owner = guild.owner
  if owner is None:
    raise KnownError('No owner found')
  owner_id = owner.id
  owner_name = ConvertInput(owner.name)

  store = RegisterStore(discord_id,
                           discord_name,
                           name_of_store,
                           owner_id,
                           owner_name)
  if store is None:
    raise KnownError('Unable to register store')
  return store

async def CreateMTSubmitterRole(interaction):
  owner = interaction.guild.owner
  mtsubmitter_role = discord.utils.find(lambda r: r.name == 'MTSubmitter',
                                        interaction.guild.roles)  
  
  if mtsubmitter_role is None:
    try:
      #TODO: This is giving me a "Missing Permissions" error even when manage_roles is true??  
      mtsubmitter_role = await interaction.guild.create_role(name="MTSubmitter",
                                                             permissions=discord.Permissions.all())
      await owner.add_roles(mtsubmitter_role)
    except Exception:
      await interaction.followup.send('Unable to create MTSubmitter role. Please create and assign manually.', ephemeral=True)

async def AssignMTSubmitterRole(bot:discord.Client, user_id, guild_id):
  guild = bot.get_guild(int(guild_id))
  if guild is None:
    raise Exception('Guild not found')
  user = await guild.fetch_member(int(user_id))
  if user is None:
    raise Exception('User not found')
  mtsubmitter_role = discord.utils.find(lambda r: r.name == 'MTSubmitter',
                                        guild.roles)
  if mtsubmitter_role is None:
    raise Exception('MTSubmitter role not found')
  await user.add_roles(mtsubmitter_role)
  return "Role assigned to user"

async def AssignStoreOwnerRoleInBotGuild(bot:discord.Client, interaction):
  bot_guild = bot.get_guild(BOTGUILDID)
  if bot_guild is None:
    raise Exception('Bot guild not found')
  user = await bot_guild.fetch_member(interaction.user.id)

  if user is None:
    raise Exception('User not found')
  store_owner_role = discord.utils.find(lambda r: r.name == 'Store Owners',
                                        bot_guild.roles)
  if store_owner_role is None:
    raise Exception('Store Owner role not found')
    
  await user.add_roles(store_owner_role)