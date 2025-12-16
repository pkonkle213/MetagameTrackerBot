import discord
from discord.ext import commands
from discord import app_commands, Interaction
from services.personal_matchups_services import PersonalMatchups
from services.player_win_record_services import PlayRecord
from output_builder import BuildTableOutput
from services.command_error_service import Error
from paid_stores import PAIDSTORES

class PersonalStatisticsGroup(commands.GroupCog, name='personalstats'):
  """A group of commands to get personal statistics"""
  def __init__(self, bot):
    self.bot = bot

  @app_commands.command(name='matchups',
                        description="See your win/loss record based upon archetypes you've played against in this format")
  @app_commands.guild_only()
  @app_commands.checks.cooldown(1, 60.0, key=lambda i: (i.guild_id, i.user.id))
  @app_commands.guilds(*[discord.Object(id=guild_id) for guild_id in PAIDSTORES])
  async def PersonalMatchupReport(self,
                                  interaction: Interaction,
                start_date: str = '',
                end_date: str = ''):
    await interaction.response.defer(ephemeral=True)
    data, title, headers = PersonalMatchups(interaction, start_date, end_date)
    output = BuildTableOutput(title, headers, data)
    await interaction.followup.send(output)


  @app_commands.command(name="wlrecord",
                        description="Look up your win/loss record(s)")
  @app_commands.guild_only()
  @app_commands.checks.cooldown(1, 60.0, key=lambda i: (i.guild_id, i.user.id))
  @app_commands.guilds(*[discord.Object(id=guild_id) for guild_id in PAIDSTORES])
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
  
  @PersonalMatchupReport.error
  @WLDRecord.error
  async def Errors(self,
                   interaction: discord.Interaction,
                   error: app_commands.AppCommandError):
    await Error(self.bot, interaction, error)
  

async def setup(bot):
  await bot.add_cog(PersonalStatisticsGroup(bot))