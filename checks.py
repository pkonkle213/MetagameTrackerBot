from discord import utils

def isSubmitter(guild, author, role_name):
  role = utils.find(lambda r: r.name == role_name, guild.roles)
  return role in author.roles