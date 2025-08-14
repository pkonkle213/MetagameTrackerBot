from discord.ext import commands
from discord import app_commands
from services.command_error_service import MissingRoleError
from services.submitted_archetypes_service import SubmittedArchetypesReport
from output_builder import BuildTableOutput
import discord
from services.store_level_service import Level2StoreIds

TARGET_GUILDS = [Level2StoreIds()]

class ArchetypeSubmittedCommand(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @app_commands.command(name='viewsubmissions',
                        description='Generate a report of the archetypes submitted and by whom')
  @app_commands.guild_only()
  @app_commands.guilds(*[discord.Object(id=guild_id[0]) for guild_id in TARGET_GUILDS])
  @app_commands.checks.has_role('MTSubmitter')
  async def ViewSubmittedArchetypes(self,
                                    interaction,
                                    player_name: str = '',
                                    event_date: str = ''):
    await interaction.response.defer(ephemeral=True)
    try:
      data, headers, title, archetype_column = SubmittedArchetypesReport(interaction,
                                                       player_name,
                                                       event_date)
      if data is None or len(data) == 0:
        await interaction.followup.send('No archetypes submitted for this store or format')
      else:
        output = BuildTableOutput(title, headers, data, archetype_column)
        await interaction.followup.send(output, ephemeral=True)
    except Exception as exception:
      await interaction.followup.send(f'Error: {exception}', ephemeral=True)

  @ViewSubmittedArchetypes.error
  async def ViewSubmittedArchetypesError(self, interaction, error):
    await MissingRoleError(interaction, error)

async def setup(bot):
  await bot.add_cog(ArchetypeSubmittedCommand(bot))
