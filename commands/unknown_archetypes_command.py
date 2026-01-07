import discord
from discord.ext import commands
from discord import app_commands, Interaction
from services.unknown_archetypes_services import GetAllUnknown
from output_builder import BuildTableOutput
from services.command_error_service import Error
from paid_stores import PAIDSTORES


class UnknownArchetypes(commands.Cog):

  def __init__(self, bot):
    self.bot = bot

  @app_commands.command(
      name='unknown',
      description='See what archetypes still need submitted for a date range')
  @app_commands.guild_only()
  @app_commands.checks.cooldown(1, 60.0, key=lambda i: (i.guild_id, i.user.id))
  @app_commands.guilds(
      *[discord.Object(id=guild_id) for guild_id in PAIDSTORES])
  async def IntoTheUnknown(self,
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
    data, title, headers = GetAllUnknown(interaction, start_date, end_date)
    if data is None or len(data) == 0:
      await interaction.followup.send(
          'Congratulations! No unknown archetypes found for this format')
    else:
      output = BuildTableOutput(title, headers, data)
      output = output[:-3] + '\nTo submit yours, type and enter: /submit archetype```'
      await interaction.followup.send(output)

  
  @IntoTheUnknown.error
  async def Errors(self, interaction: Interaction,
                   error: app_commands.AppCommandError):
    await Error(self.bot, interaction, error)
  


async def setup(bot):
  await bot.add_cog(UnknownArchetypes(bot))
