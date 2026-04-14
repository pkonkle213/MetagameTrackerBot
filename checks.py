from discord import utils, Interaction, app_commands
from settings import PHILID
from timedposts.automated_paid_users import PAID_USERS
from timedposts.automated_paid_users import STORES

def isPaidUser():
  async def predicate(interaction: Interaction) -> bool:
    if interaction.user.id in PAID_USERS:
      return True
    raise app_commands.CheckFailure("This command is only available to paid users")
  return app_commands.check(predicate)

def isStore():
  async def predicate(interaction: Interaction) -> bool:
    if interaction.guild_id in STORES:
      return True
    raise app_commands.CheckFailure("This command must be executed in a store guild")
  return app_commands.check(predicate)

def isSubmitter(guild, author, role_name):
  role = utils.find(lambda r: r.name == role_name, guild.roles)
  return role in author.roles #or author.id == PHILID

def isOwner(interaction: Interaction):
  userid = interaction.user.id
  ownerid = interaction.guild.owner_id if interaction.guild else None
  return userid == ownerid

def isPhil(interaction: Interaction):
  return interaction.user.id == PHILID
