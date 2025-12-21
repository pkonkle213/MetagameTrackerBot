from discord import utils, Interaction, app_commands
from settings import PHILID
from discord.ext import commands
from timedposts.automated_paid_users import PAID_USERS

def isPaidUser():
  async def predicate(interaction: Interaction) -> bool:
    return interaction.user.id in PAID_USERS
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
