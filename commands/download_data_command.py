import discord
from discord.ext import commands
from discord import app_commands, Interaction
from checks import isOwner
from services.download_data_services import GetStoreData, GetPlayerData
from discord_messages import MessageUser
from services.command_error_service import Error

class DownloadDataGroup(commands.GroupCog, name='download'):
  """A group of commands for downloading data"""
  def __init__(self, bot):
    self.bot = bot

  @app_commands.command(name='store',
  description='Download the store data for a date range')
  @app_commands.check(isOwner)
  #@app_commands.guilds(*[discord.Object(id=guild_id) for guild_id in LEVELINFSTORES])
  @app_commands.guild_only()
  @app_commands.checks.cooldown(1, 60.0, key=lambda i: (i.guild_id, i.user.id))
  async def StoreDownload(self,
                          interaction: Interaction,
                          start_date: str = '',
                          end_date: str = ''):
    """
    Parameters
    ----------
    start_date: string
      Beginning of Date Range (MM/DD/YYYY)
    end_date: string
      End of Date Range (MM/DD/YYYY)
    """
    await interaction.response.defer(ephemeral=True)
    message, files = GetStoreData(interaction, start_date, end_date)
    if len(files) == 0:
      await interaction.followup.send('No data found for this store')
    else:
      await MessageUser(self.bot,
                        message,
                        interaction.user.id,
                        files)
      await interaction.followup.send('The data for the store will arrive by message')
 
  @app_commands.command(name='player',
                        description="Download the player's data for a store for a date range")
  @app_commands.guild_only()
  #@app_commands.guilds(*[discord.Object(id=guild_id) for guild_id in LEVELINFSTORES])
  @app_commands.checks.cooldown(1, 60.0, key=lambda i: (i.guild_id, i.user.id))
  async def PlayerDownload(self,
                           interaction: Interaction,
                           start_date: str = '',
                           end_date: str = ''):
    """
    Parameters
    ----------
    start_date: string
      Beginning of Date Range (MM/DD/YYYY)
    end_date: string
      End of Date Range (MM/DD/YYYY)
    """
    await interaction.response.defer(ephemeral=True)
    title, files = GetPlayerData(interaction, start_date, end_date)
    if len(files) == 0:
      await interaction.followup.send('No data found for this player')
    else:
      await MessageUser(self.bot,
                        title,
                        interaction.user.id,
                        files)
      await interaction.followup.send('Your data will arrive by message')


  @PlayerDownload.error
  @StoreDownload.error
  async def Errors(self,
                   interaction: discord.Interaction,
                   error: app_commands.AppCommandError):
    await Error(self.bot, interaction, error)

async def setup(bot):
  await bot.add_cog(DownloadDataGroup(bot))
