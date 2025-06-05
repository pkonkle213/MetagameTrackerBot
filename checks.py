from discord import utils
from settings import PHILID

def isSubmitter(guild, author, role_name):
  role = utils.find(lambda r: r.name == role_name, guild.roles)
  return role in author.roles or author.id == PHILID