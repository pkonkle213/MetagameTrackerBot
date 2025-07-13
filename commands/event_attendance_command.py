from discord.ext import commands
from discord import app_commands, Interaction
from services.store_attendance import GetStoreAttendance
from output_builder import BuildTableOutput

class EventAttendance(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @app_commands.command(name="attendance",
                        description="Get the attendance for a date range")
  @app_commands.guild_only()
  async def Attendance(self, interaction: Interaction,
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
    data, title, headers = GetStoreAttendance(interaction, start_date, end_date)
    if data is None or len(data) == 0:
      await interaction.followup.send('No attendance data found for this store and/or format')
    else:
      output = BuildTableOutput(title,
                  headers,
                  data)
      await interaction.followup.send(output)

async def setup(bot):
  await bot.add_cog(EventAttendance(bot))
