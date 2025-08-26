import discord
from custom_errors import KnownError
from data.store_data import RegisterStore
from services.input_services import ConvertInput
from settings import BOTGUILDID
from tuple_conversions import ConvertToStore

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

  storeobj = RegisterStore(discord_id,
                           discord_name,
                           name_of_store,
                           owner_id,
                           owner_name)
  if storeobj is None:
    raise KnownError('Unable to register store')
  return ConvertToStore(storeobj)

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