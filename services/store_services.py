import discord
from custom_errors import KnownError
from data.formats_data import AddFormatMap, GetFormatsByGameId
from data.games_data import AddGameMap
from data.store_data import AddStore, UpdateStore
from input_modals.store_profile_update import StoreProfileModal
from interaction_objects import GetObjectsFromInteraction
from services.game_mapper_services import GetGameOptions
from settings import BOTGUILDID
from tuple_conversions import Format, Game

async def UpdateStoreDetails(interaction: discord.Interaction):
  """Updates the store details in the database"""
  # Send modal FIRST before any database operations to avoid Discord timeout
  modal = StoreProfileModal(None)
  await interaction.response.send_modal(modal)
  await modal.wait()

  if not modal.is_submitted:
    raise KnownError('Modal not submitted correctly')

  # Now get store from database after modal is submitted
  objects = GetObjectsFromInteraction(interaction, store=True)
  
  result = UpdateStore(objects.Store.DiscordId,
                       modal.submitted_owners_name,
                       modal.submitted_store_name,
                       modal.submitted_store_address,
                       modal.submitted_melee_id,
                       modal.submitted_melee_secret)
  
  if result:
    return 'Store profile updated'

async def NewStoreRegistration(bot:discord.Client,
                               guild: discord.Guild):
  """Goes through steps to register a new store and automap categories and channels"""
  try:
    if guild is None:
      raise KnownError('No guild found')
    AddStoreToDatabase(guild)
    message, mappings = MapCategoriesAndChannels(guild)
    await MessageOwnerMappings(guild, message, mappings)
    output = await CreateMTSubmitterRole(guild)
    owner = guild.owner
    if owner is None:
      raise KnownError('No owner found')
    await AssignStoreOwnerRoleInBotGuild(bot, owner.id)
    return output
  except KnownError as error:
    print(f'KnownError registering store: {error}')
  except Exception as error:
    print(f'Error registering store: {error}')

async def MessageOwnerMappings(guild: discord.Guild,
                               output: str,
                               mappings: bool):
  """Messages the owner of the guild with the mappings that were performed"""
  owner = guild.owner
  if owner is None:
    raise KnownError('No owner found')
  if mappings:
    await owner.send(f"Your store has been auto registered!\n\nHere's what was also automapped:\n{output}If you'd like to change these mappings, please use the `/map` commands.")
  else:
    await owner.send("Your store has been auto registered! However, categories or channels weren't automapped. Please map your categories and channels manually.")

def AddStoreToDatabase(guild: discord.Guild):
  """Adds the store to the database"""
  owner = guild.owner
  if owner is None:
    raise KnownError('No owner found')
  store = AddStore(guild.id,
                        guild.name,
                        owner.id,
                        owner.name)
  if store is None:
    raise KnownError('Unable to register store')
  return store

def MatchGame(category_name: str, games: list[Game]):
  """Matches the category name to a game"""
  for game in games:
    if game.GameName.lower() in category_name.lower():
      return game

def MatchFormat(channel_name: str, formats: list[Format]):
  """Matches the channel name to a format"""
  for format in formats:
    if format.FormatName.lower() in channel_name.lower():
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
      result = AddGameMap(guild.id, game.GameId, category.id)
      mapping = True
      if result:
        output += f'Game: {game.GameName.title()}, Category: {category.name} ({category.id})\n'
    
      formats = GetFormatsByGameId(game.GameId)
      if formats:
        for channel in category.channels:
          format = MatchFormat(channel.name, formats)
          if format:
            result = AddFormatMap(guild.id, format.FormatId, channel.id)
            if result:
              output += f'Format: {format.FormatName.title()}, Channel: {channel.name} ({channel.id})\n'

      output += '\n'

  return output, mapping

async def CreateMTSubmitterRole(guild:discord.Guild):
  """Creates the MTSubmitter role and assigns it to the owner"""
  owner = guild.owner
  if owner is None:
    raise KnownError('No owner found')
  mtsubmitter_role = discord.utils.get(guild.roles, name="MTSubmitter")

  if mtsubmitter_role is None:
    print("Attempting to create and add the MTSubmitter role")
    try: 
      perms = discord.Permissions(manage_messages=True)
      mtsubmitter_role = await guild.create_role(name="MTSubmitter", permissions=perms)
      await owner.add_roles(mtsubmitter_role)
      print('Success!')
      return 'MTSubmitter role created and assigned to owner.'
    except Exception:
      print('Failure')
      return 'Unable to create MTSubmitter role. Please create and assign manually.'

async def AssignStoreOwnerRoleInBotGuild(bot:discord.Client, owner_id: int):
  """Assigns the Store Owner role to the owner in the bot guild"""
  bot_guild = bot.get_guild(BOTGUILDID)
  if bot_guild is None:
    raise Exception('Bot guild not found')
  user = await bot_guild.fetch_member(owner_id)

  if user is None:
    raise Exception('User not found')
  store_owner_role = discord.utils.find(lambda r: r.name == 'Store Owners',
                                        bot_guild.roles)
  if store_owner_role is None:
    raise Exception('Store Owner role not found')
    
  await user.add_roles(store_owner_role)