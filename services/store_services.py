from services.input_services import ConvertInput
import settings
from discord_messages import MessageUser
import discord
from custom_errors import KnownError
from data.formats_data import AddFormatMap, GetFormatsByGameId
from data.games_data import AddGameMap
from data.store_data import AddStore, UpdateStore, AddDiscord
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
  store = GetObjectsFromInteraction(interaction)[0]
  
  result = UpdateStore(store.discord_id,
                       modal.submitted_owners_name,
                       modal.submitted_store_name,
                       '', #modal.submitted_store_address,
                       modal.submitted_melee_id,
                       modal.submitted_melee_secret)
  
  if result:
    return 'Store profile updated'

async def NewStoreRegistration(
  bot:discord.Client,
  guild: discord.Guild
) -> str:
  """Goes through steps to register a new store and automap categories and channels"""
  output = ''
  #TODO: Define discord_name, owner_name, and owner_id and others here as they're used in multiple places
  try:
    print('Adding discord to database')
    add_discord = AddDiscordToDatabase(guild)
    if add_discord:
      output += '- Discord added to database\n'

    print('Adding store to database')
    add_store = AddStoreToDatabase(guild)
    if add_store:
      output += '- Store added to database\n'

    print('Mapping categories and channels')
    mapping_message, mapping_success = MapCategoriesAndChannels(guild)
    if mapping_success:
      output += '- Categories and channels automapped:\n'
      output += mapping_message
    else:
      output += '- No categories or channels automapped\n'

    print('Creating and assigning MTSubmitter role')
    role_message, role_success = await CreateMTSubmitterRole(guild)
    
    print('Assigning Store Owner role in bot guild')
    owner = guild.owner
    if owner is None:
      raise Exception('No owner found')
    role_assign = await AssignStoreOwnerRoleInBotGuild(bot, owner.id)
    return output
  except Exception as e:
    await MessageUser(bot, f"Issue with new store registration: {e}", settings.PHILID)
    return f'Unable to add this discord to my database. Please contact the bot owner.'

def AddDiscordToDatabase(guild: discord.Guild) -> str:
  """Adds the discord to the database"""
  guild_name = ConvertInput(guild.name)
  owner_name = ConvertInput(guild.owner.name) if guild.owner else 'Unknown'
  owner_id = guild.owner_id if guild.owner_id else 0
  discord = AddDiscord(guild.id, guild.name, owner_id, owner_name)
  return 'Done'

def AddStoreToDatabase(guild: discord.Guild) -> int:
  """Adds the store to the database"""
  store = AddStore(guild.id)
  return store

def MatchGame(category_name: str, games: list[Game]):
  """Matches the category name to a game"""
  for game in games:
    if game.game_name.lower() in category_name.lower():
      return game

def MatchFormat(channel_name: str, formats: list[Format]):
  """Matches the channel name to a format"""
  for format in formats:
    if format.format_name.lower() in channel_name.lower():
      return format

def MapCategoriesAndChannels(guild: discord.Guild) -> tuple[str, bool]:
  """Sequentially maps the categories and channels in the guild"""
  try:
    output = ''
    mapping = False
    games = GetGameOptions()
    if games is None:
      raise Exception('No games found to automap')
  
    for category in guild.categories:
      game = MatchGame(category.name, games)
      if game:
        result = AddGameMap(guild.id, game.game_id, category.id)
        mapping = True
        if result:
          output += f'Game: {game.game_name.title()}, Category: {category.name} ({category.id})\n'
      
        formats = GetFormatsByGameId(game.game_id)
        if formats:
          for channel in category.channels:
            format = MatchFormat(channel.name, formats)
            if format:
              result = AddFormatMap(guild.id, format.format_id, channel.id)
              if result:
                output += f'Format: {format.format_name.title()}, Channel: {channel.name} ({channel.id})\n'
  
        output += '\n'
  
    return output, mapping
  except Exception as e:
    return '', False

async def CreateMTSubmitterRole(guild:discord.Guild) -> tuple[str, bool]:
  """Creates the MTSubmitter role and assigns it to the owner"""
  owner = guild.owner
  if owner is None:
    raise KnownError('No owner found')
  mtsubmitter_role = discord.utils.get(guild.roles, name="MTSubmitter")
  print('Role:', mtsubmitter_role)

  output = ''
  success = ''
  if mtsubmitter_role is None:
    print("Attempting to create and add the MTSubmitter role")
    try:
      perms = discord.Permissions(manage_messages=True)
      mtsubmitter_role = await guild.create_role(name="MTSubmitter", permissions=perms, reason="Automatic role creation on join")
      print('Created role:', mtsubmitter_role)
      print('MTSubmitter role created')
      output = 'MTSubmitter role created and assigned to owner.'
      success = True
    except discord.Forbidden:
      print(f"Bot lacks 'Manage Roles' permission in {guild.name}")
      return 'Bot lacks permission to create MTSubmitter role. Please create and assign manually.', False
    except Exception as e:
      print('Failure to create or assign MTSubmitter role:', e)
      return 'Unable to create MTSubmitter role. Please create and assign manually.', False
      
  try:
    print('Attempting to assign MTSubmitter role to owner')
    await owner.add_roles(mtsubmitter_role)
    print('MTSubmitter role assigned!')
    output = 'MTSubmitter role assigned to owner.' if output == '' else 'MTSubmitter role created and assigned to owner.'
    success = True
    return output, success
  except Exception as e:
    return 'MTSubmitter role unable to be assigned to owner. Please assign manually.', True

async def AssignStoreOwnerRoleInBotGuild(bot:discord.Client, owner_id: int) -> str:
  """Assigns the Store Owner role to the owner in the bot guild"""
  bot_guild = bot.get_guild(BOTGUILDID)
  if bot_guild is None:
    return 'Bot guild not found'
  user = await bot_guild.fetch_member(owner_id)

  if user is None:
    raise Exception('User not found')
  store_owner_role = discord.utils.find(lambda r: r.name == 'Store Owners',
                                        bot_guild.roles)
  if store_owner_role is None:
    raise Exception('Store Owner role not found')
    
  await user.add_roles(store_owner_role)
  return "If owner is in the bot's guild, they've been assigned the Store Owner role."