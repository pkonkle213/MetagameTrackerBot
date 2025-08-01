from discord.ext import commands
from discord import app_commands, Interaction
from output_builder import BuildTableOutput
from services.player_win_record_services import PlayRecord
from discord_messages import Error

#TODO: This can probably be grouped with the personal matchups command
class PlayerWinRecord(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @app_commands.command(name="personalrecord",
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
    try:
      data, title, header = PlayRecord(interaction, start_date, end_date)
      output = BuildTableOutput(title, header, data)
      await interaction.followup.send(output)
    except Exception as exception:
      await interaction.followup.send("Something unexpected went wrong. It's been reported. Please try again in a few hours.", ephemeral=True)
      await Error(self.bot, exception)
  
async def setup(bot):
  await bot.add_cog(PlayerWinRecord(bot))