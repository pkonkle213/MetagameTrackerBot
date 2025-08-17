from discord.ext import commands
from discord import app_commands, Interaction
from checks import isOwner
from services.download_data_services import GetParticipantData, GetRoundData, GetPlayersRoundData, GetPlayersParticipantData
from discord_messages import MessageUser
from services.command_error_service import Error
import discord
from services.store_level_service import LEVELINFSTORES

#TODO: Combined store download and player downloads into one command each using the following logic to send multiple files
"""
file1 = discord.File('path/to/your/file1.txt')
file2 = discord.File('path/to/your/file2.png')

# Send the message with both files
await user.send("Here are your files!", files=[file1, file2])
"""

class DownloadDataGroup(commands.GroupCog, name='download'):
  """A group of commands for downloading data"""
  def __init__(self, bot):
    self.bot = bot

  @app_commands.command(name='participants',
  description='Download the basic data for a store for a date range')
  @app_commands.check(isOwner)
  @app_commands.guilds(*[discord.Object(id=guild_id) for guild_id in LEVELINFSTORES])
  @app_commands.guild_only()
  async def ParticipantData(self,
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
    try:
      title, file = GetParticipantData(interaction, start_date, end_date)
      if file is None:
        await interaction.followup.send('No data found for this store')
      await MessageUser(title,
        interaction.user.id,
        file)
      await interaction.followup.send('The data for the store will arrive by message')
    except Exception as exception:
      await Error(self.bot, interaction, exception)

  @app_commands.command(name='rounds',
                        description='Download the round by round data for a store for a date range')
  @app_commands.check(isOwner)
  @app_commands.guild_only()
  @app_commands.guilds(*[discord.Object(id=guild_id) for guild_id in LEVELINFSTORES])
  async def RoundData(self,
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
    try:
      title, file = GetRoundData(interaction, start_date, end_date)
      if file is None:
        await interaction.followup.send('No data found for this store')
      await MessageUser(title,
        interaction.user.id,
        file)
      await interaction.followup.send('The data for the store will arrive by message')
    except Exception as exception:
      await interaction.followup.send("Something unexpected went wrong. It's been reported. Please try again in a few hours.", ephemeral=True)
      await Error(self.bot, interaction, exception)

  @app_commands.command(name='myrounds',
                        description='Download the round by round data for a player for a date range')
  @app_commands.guild_only()
  @app_commands.guilds(*[discord.Object(id=guild_id) for guild_id in LEVELINFSTORES])
  async def MyRoundData(self,
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
    try:
      title, file = GetPlayersRoundData(interaction, start_date, end_date)
      if file is None:
        await interaction.followup.send('No data found for this player')
      await MessageUser(title,
        interaction.user.id,
        file)
      await interaction.followup.send('Your data will arrive by message')
    except Exception as exception:
      await interaction.followup.send("Something unexpected went wrong. It's been reported. Please try again in a few hours.", ephemeral=True)
      await Error(self.bot, interaction, exception)

  @app_commands.command(name='myresults',
                        description='Download the basic data for a player for a date range')
  @app_commands.guild_only()
  @app_commands.guilds(*[discord.Object(id=guild_id) for guild_id in LEVELINFSTORES])
  async def MyParticipantData(self,
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
    try:
      title, file = GetPlayersParticipantData(interaction, start_date, end_date)
      if file is None:
        await interaction.followup.send('No data found for this player')
      await MessageUser(title,
        interaction.user.id,
        file)
      await interaction.followup.send('Your data will arrive by message')
    except Exception as exception:
      await interaction.followup.send("Something unexpected went wrong. It's been reported. Please try again in a few hours.", ephemeral=True)
      await Error(self.bot, interaction, exception)

async def setup(bot):
  await bot.add_cog(DownloadDataGroup(bot))
