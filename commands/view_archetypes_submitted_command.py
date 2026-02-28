import discord
from discord import Interaction, app_commands
from discord.ext import commands
from output_builder import BuildTableOutput
from paid_stores import PAIDSTORES
from services.command_error_service import Error
from services.submitted_archetypes_service import SubmittedArchetypesReport

class ArchetypeSubmittedCommand(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @app_commands.command(name='viewsubmissions',
                        description='Generate a report of the archetypes submitted and by whom')
  @app_commands.guilds(*[discord.Object(id=guild_id) for guild_id in PAIDSTORES])
  @app_commands.guild_only()
  @app_commands.checks.cooldown(1, 60.0, key=lambda i: (i.guild_id, i.user.id))
  @app_commands.checks.has_role('MTSubmitter')
  async def ViewSubmittedArchetypes(self,
                                    interaction: Interaction,
                                    player_name: str = '',
                                    event_date: str = ''):
    """
    Parameters
    ----------
    player_name: string
      The player the archetype was submitted for
    event_date: string
      The date of the event (MM/DD/YYYY)
    """
    await interaction.response.defer(ephemeral=True)
    data, headers, title = SubmittedArchetypesReport(interaction,
                                                                       player_name,
                                                                       event_date)
    if data is None or len(data) == 0:
      await interaction.followup.send('No archetypes submitted for this store or format')
    else:
      output = BuildTableOutput(title, headers, data)
      await interaction.followup.send(output, ephemeral=True)


  @ViewSubmittedArchetypes.error
  async def Errors(self,
                   interaction: Interaction,
                   error: app_commands.AppCommandError):
    await Error(self.bot, interaction, error)

async def setup(bot):
  await bot.add_cog(ArchetypeSubmittedCommand(bot))
