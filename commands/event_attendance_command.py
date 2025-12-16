import discord
from discord.ext import commands
from discord import app_commands, Interaction
from services.store_attendance_services import GetStoreAttendance
from output_builder import BuildTableOutput
from services.command_error_service import Error
from paid_stores import PAIDSTORES

class EventAttendance(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @app_commands.command(name="attendance",
                        description="Get the attendance for a date range")
  @app_commands.guild_only()
  @app_commands.checks.cooldown(1, 60.0, key=lambda i: (i.guild_id, i.user.id))
  @app_commands.guilds(*[discord.Object(id=guild_id) for guild_id in PAIDSTORES])
  async def Attendance(self,
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
    await interaction.response.defer()
    data, title, headers = GetStoreAttendance(interaction, start_date, end_date)
    if data is None or len(data) == 0:
      await interaction.followup.send('No attendance data found for this store and/or format')
    else:
      output = BuildTableOutput(title,
                  headers,
                  data)
      await interaction.followup.send(output)

  @Attendance.error
  async def Errors(self,
                   interaction: discord.Interaction,
                   error: app_commands.AppCommandError):
    await Error(self.bot, interaction, error)
  
async def setup(bot):
  await bot.add_cog(EventAttendance(bot))

