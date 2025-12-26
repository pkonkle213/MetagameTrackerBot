import settings
from discord import Interaction, app_commands
from discord.ext import commands
from services.graph_services import MetagameScatterPlot


class Graphs(commands.GroupCog, name='graph'):
  """A group of commands for creating graphs from data"""

  def __init__(self, bot):
    self.bot = bot

  @app_commands.command(
      name="metagame",
      description="A scatterplot of the metagame for a given format")
  @app_commands.guild_only()
  #@app_commands.guilds(settings.TESTGUILDID)
  async def Metagame(self,
                     interaction: Interaction,
                     start_date: str = '',
                     end_date: str = ''):
    await interaction.response.defer()
    result = MetagameScatterPlot(interaction, start_date, end_date)
    await interaction.followup.send(file=result, ephemeral=True)

  @app_commands.command(
      name="heatmap",
      description="A heatmap of the metagame for a given format")
  @app_commands.guild_only()
  @app_commands.guilds(settings.TESTGUILDID)
  async def Heatmap(self,
                    interaction: Interaction,
                    start_date: str = '',
                    end_date: str = ''):
    await interaction.response.send_message(
        'This command is not yet implemented', ephemeral=True)


async def setup(bot):
  await bot.add_cog(Graphs(bot))
