import discord
from data.store_data import RegisterStore
from services.input_services import ConvertInput
from settings import BOTGUILD
from tuple_conversions import ConvertToStore

def RegisterNewStore(interaction: discord.Interaction, store_name: str):
  name_of_store = ConvertInput(store_name)

  guild = interaction.guild
  if guild is None:
    raise Exception('No guild found')
  discord_id = guild.id
  discord_name = ConvertInput(guild.name)
  
  owner = guild.owner
  if owner is None:
    raise Exception('No owner found')
  owner_id = owner.id
  owner_name = ConvertInput(owner.name)

  storeobj = RegisterStore(discord_id,
                           discord_name,
                           name_of_store,
                           owner_id,
                           owner_name)
  return ConvertToStore(storeobj)

async def SetPermissions(interaction):
  owner = interaction.guild.owner
  owner_role = discord.utils.find(lambda r: r.name == 'Owner',
                                  interaction.guild.roles)
  mtsubmitter_role = discord.utils.find(lambda r: r.name == 'MTSubmitter',
                                        interaction.guild.roles)
  #TODO: This is giving me a "Missing Permissions" error even when manage_roles is true??
  if owner_role is None:
    owner_role = await interaction.guild.create_role(name="Owner",
                                                     permissions=discord.Permissions.all())
  await owner.add_roles(owner_role)
  
  if mtsubmitter_role is None:
    mtsubmitter_role = await interaction.guild.create_role(name="MTSubmitter",
                                                           permissions=discord.Permissions.all())
  await owner.add_roles(mtsubmitter_role)

  permissions = discord.PermissionOverwrite(send_messages=False)
  everyone_role = interaction.guild.default_role
  await interaction.channel.set_permissions(everyone_role,
                                            overwrite=permissions)

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
  bot_guild = bot.get_guild(int(BOTGUILD.id))
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