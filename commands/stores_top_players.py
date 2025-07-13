from discord.ext import commands
from discord import app_commands, Interaction
from services.top_players import GetTopPlayers
from output_builder import BuildTableOutput

class StoreTopPlayers(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @app_commands.command(name="topplayers",
                        description="Get the top players of the format")
  @app_commands.checks.has_role("MTSubmitter")
  @app_commands.guild_only()
  async def TopPlayers(self,
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
    data, title, headers = GetTopPlayers(interaction,
                           start_date,
                           end_date)
    output = BuildTableOutput(title, headers, data)
    await interaction.followup.send(output)

async def setup(bot):
  await bot.add_cog(StoreTopPlayers(bot))