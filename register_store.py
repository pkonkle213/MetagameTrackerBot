import discord
from database_connection import RegisterStore
from tuple_conversions import ConvertToStore

def RegisterNewStore(interaction: discord.Interaction, store_name: str):
  name_of_store = store_name.upper()

  guild = interaction.guild
  if guild is None:
    raise Exception('No guild found')
  discord_id = guild.id
  discord_name = guild.name.upper()
  
  owner = guild.owner
  if owner is None:
    raise Exception('No owner found')
  owner_id = owner.id
  owner_name = owner.display_name.upper()
  
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

  #TODO: This is giving me a "Missing Permissions" error even when manage_roles is true
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