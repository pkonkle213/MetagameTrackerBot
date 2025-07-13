from discord.ext import commands
from discord import app_commands, Interaction
from services.unknown_archetypes import GetAllUnknown
from output_builder import BuildTableOutput

class UnknownArchetypes(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @app_commands.command(name='unknown',
  description='See what archetypes still need submitted for a date range')
  @app_commands.guild_only()
  async def IntoTheUnknown(self, interaction: Interaction,
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
    await interaction.response.defer()
    data, title, headers = GetAllUnknown(interaction, start_date, end_date)
    if data is None or len(data) == 0:
      await interaction.followup.send('Congratulations! No unknown archetypes found for this format')
    else:
      output = BuildTableOutput(title, headers, data)
      await interaction.followup.send(output)

async def setup(bot):
  await bot.add_cog(UnknownArchetypes(bot))