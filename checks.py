from discord import Guild, Member, User, utils, Interaction, app_commands
from settings import PHILID
import timedposts.automated_paid_users as apu

def IsPaidUser():
  async def predicate(interaction: Interaction) -> bool:
    if interaction.user.id in apu.PAID_USERS:
      return True
    raise app_commands.CheckFailure("This command is only available to paid users")
  return app_commands.check(predicate)

def IsPaidStore():
  async def predicate(interaction: Interaction) -> bool:
    if interaction.guild_id in apu.PAID_STORES:
      return True
    raise app_commands.CheckFailure("This command is only available to paid stores.")
  return app_commands.check(predicate)

def IsPaidHub():
  async def predicate(interaction: Interaction) -> bool:
    if interaction.guild_id in apu.PAID_HUBS:
      return True
    raise app_commands.CheckFailure("This command is only available to paid hubs.")
  return app_commands.check(predicate)
  
def IsStore():
  async def predicate(interaction: Interaction) -> bool:
    if interaction.guild_id in apu.STORES:
      return True
    raise app_commands.CheckFailure("This command must be executed in a store guild")
  return app_commands.check(predicate)

def IsHub():
  async def predicate(interaction: Interaction) -> bool:
    if interaction.guild_id in apu.HUBS:
      return True
    raise app_commands.CheckFailure("This command must be executed in a hub guild")
  return app_commands.check(predicate)

def isSubmitter(guild:Guild, author: Member, role_name:str) -> bool:
  role = utils.find(lambda r: r.name == role_name, guild.roles)
  return role in author.roles

def IsOwner():
  async def predicate(interaction: Interaction) -> bool:
    userid = interaction.user.id
    ownerid = interaction.guild.owner_id if interaction.guild else None
    if userid == ownerid:
      return True
    raise app_commands.CheckFailure("You must be the owner of this server to use this command")
  return app_commands.check(predicate)

def isPhil(interaction: Interaction) -> bool:
  return interaction.user.id == PHILID
