from discord.ext import commands
from discord import app_commands, Interaction
from output_builder import BuildTableOutput
from services.player_win_record import PlayRecord

class PlayerWinRecord(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @app_commands.command(name="playrecord",
    description="Look up your win/loss record(s)")
  @app_commands.guild_only()
  async def WLDRecord(self,
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
    data, title, header = PlayRecord(interaction, start_date, end_date)
    output = BuildTableOutput(title, header, data)
    await interaction.followup.send(output)
  
async def setup(bot):
  await bot.add_cog(PlayerWinRecord(bot))