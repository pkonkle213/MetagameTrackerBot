import discord
from custom_errors import KnownError
from data.games_data import AddGameMap
from data.store_data import RegisterStore
from services.game_mapper_services import GetGameOptions
from data.formats_data import AddFormatMap, GetFormatsByGameId
from tuple_conversions import Format, Game
from services.input_services import ConvertInput
from settings import BOTGUILDID

async def NewStoreRegistration(guild: discord.Guild):
  #Starting to register new store
  if guild is None:
    raise KnownError('No guild found')
  #I know this works
  #store = AddStoreToDatabase(guild)
  output, mappings = MapCategoriesAndChannels(guild)
  await MessageOwnerMappings(guild, output, mappings)
  """
  CreateAndAssignMTSubmitterRoleInGuild()
  AssignStoreOwnerRoleInBotGuild()
  """

async def MessageOwnerMappings(guild: discord.Guild, output: str, mappings: bool):
  """Messages the owner of the guild with the mappings that were performed"""
  owner = guild.owner
  if owner is None:
    raise KnownError('No owner found')
  if mappings:
    await owner.send(f"Your store has been auto registered!\n\nHere's what was also automapped:\n{output}If you'd like to change these mappings, please use the /map commands.")
  else:
    await owner.send("Your store has been auto registered! However, categories or channels weren't automapped. Please map your categories and channels manually.")

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

def MatchGame(category_name: str, games: list[Game]):
  """Matches the category name to a game"""
  for game in games:
    if game.Name.lower() in category_name.lower():
      return game

def MatchFormat(channel_name: str, formats: list[Format]):
  """Matches the channel name to a format"""
  for format in formats:
    if format.Name.lower() in channel_name.lower():
      return format

def MapCategoriesAndChannels(guild: discord.Guild):
  """Sequentially maps the categories and channels in the guild"""
  output = ''
  mapping = False
  games = GetGameOptions()
  if games is None:
    raise KnownError('No games found')

  for category in guild.categories:
    game = MatchGame(category.name, games)
    if game:
      result = AddGameMap(guild.id, game.ID, category.id)
      mapping = True
      if result:
        output += f'Game: {game.Name.title()}, Category: {category.name} ({category.id})\n'
    
      formats = GetFormatsByGameId(game.ID)
      if formats:
        for channel in category.channels:
          format = MatchFormat(channel.name, formats)
          if format:
            result = AddFormatMap(guild.id, format.ID, channel.id)
            if result:
              output += f'Format: {format.Name.title()}, Channel: {channel.name} ({channel.id})\n'

      output += '\n'

  return output, mapping

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