from discord import Guild, Member, utils, Interaction
from settings import PHILID
from timedposts.automated_paid_user_sync import PAID_USERS

#TODO: Not a check, but a method
def isSubmitter(guild:Guild, author:Member, role_name:str) -> bool:
  role = utils.find(lambda r: r.name == role_name, guild.roles)
  return role in author.roles #or author.id == PHILID

def isOwner(interaction: Interaction) -> bool:
  userid = interaction.user.id
  ownerid = interaction.guild.owner_id if interaction.guild else None
  return userid == ownerid

def isPhil(interaction: Interaction) -> bool:
  return interaction.user.id == PHILID

def isPaidUser(interaction:Interaction) -> bool:
  userId = interaction.user.id
  return userId in PAID_USERS