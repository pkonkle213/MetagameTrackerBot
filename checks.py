from discord import utils, Interaction
from settings import PHILID

#TODO: Not a check, but a method
def isSubmitter(guild, author, role_name):
  role = utils.find(lambda r: r.name == role_name, guild.roles)
  return role in author.roles #or author.id == PHILID

def isOwner(interaction: Interaction):
  userid = interaction.user.id
  ownerid = interaction.guild.owner_id if interaction.guild else None
  return userid == ownerid

def isPhil(interaction: Interaction):
  return interaction.user.id == PHILID
