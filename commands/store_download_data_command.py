from discord.ext import commands
from discord import app_commands, Interaction
from checks import isOwner
from services.store_data_download_services import GetDataReport
from discord_messages import MessageUser, Error

class DownloadStoreData(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @app_commands.command(name='downloaddata',
  description='Download the data for a store for a date range')
  @app_commands.check(isOwner)
  @app_commands.guild_only()
  async def DownloadData(self,
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
      title, file = GetDataReport(interaction, start_date, end_date)
      if file is None:
        await interaction.followup.send('No data found for this store')
        await MessageUser(title,
          interaction.user.id,
          file)
        await interaction.followup.send('The data for the store will arrive by message')
    except Exception as exception:
      await interaction.followup.send("Something unexpected went wrong. It's been reported. Please try again in a few hours.", ephemeral=True)
      await Error(self.bot, exception)

async def setup(bot):
  await bot.add_cog(DownloadStoreData(bot))
