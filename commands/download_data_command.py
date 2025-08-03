from discord.ext import commands
from discord import app_commands, Interaction
from checks import isOwner
from services.download_data_services import GetParticipantData, GetRoundData, GetPlayersRoundData, GetPlayersParticipantData
from discord_messages import MessageUser, Error

class DownloadDataGroup(commands.GroupCog, name='download'):
  def __init__(self, bot):
    self.bot = bot

  @app_commands.command(name='participants',
  description='Download the basic data for a store for a date range')
  @app_commands.check(isOwner)
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
      await interaction.followup.send("Something unexpected went wrong. It's been reported. Please try again in a few hours.", ephemeral=True)
      await Error(self.bot, exception)

  @app_commands.command(name='rounds',
                        description='Download the round by round data for a store for a date range')
  @app_commands.check(isOwner)
  @app_commands.guild_only()
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
      await Error(self.bot, exception)

  @app_commands.command(name='myrounds',
                        description='Download the round by round data for a player for a date range')
  @app_commands.guild_only()
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
      await Error(self.bot, exception)

  @app_commands.command(name='myresults',
                        description='Download the basic data for a player for a date range')
  @app_commands.guild_only()
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
      await Error(self.bot, exception)

async def setup(bot):
  print('Adding download data commands')
  await bot.add_cog(DownloadDataGroup(bot))
