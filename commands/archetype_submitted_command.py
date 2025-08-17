import discord
from discord import Interaction, app_commands
from discord.ext import commands
from output_builder import BuildTableOutput
from services.command_error_service import Error
from services.submitted_archetypes_service import SubmittedArchetypesReport
from services.store_level_service import Level2StoreIds

TARGET_GUILDS = Level2StoreIds()

class ArchetypeSubmittedCommand(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @app_commands.command(name='viewsubmissions',
                        description='Generate a report of the archetypes submitted and by whom')
  @app_commands.guilds(*[discord.Object(id=guild_id) for guild_id in TARGET_GUILDS])
  @app_commands.guild_only()
  @app_commands.checks.has_role('MTSubmitter')
  async def ViewSubmittedArchetypes(self,
                                    interaction: Interaction,
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
      await Error(self.bot, interaction, exception)

  #TODO: This doesn't seem to be catching the error I need it to. Dunno why
  @ViewSubmittedArchetypes.error
  async def my_command_error(self,
                             interaction: discord.Interaction,
                             error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingRole):
      await interaction.followup.send(f"You need the '{error.missing_role}' role to use this command.", ephemeral=True)
    else:
      await interaction.followup.send(f"An unexpected error occurred: {error}", ephemeral=True)


async def setup(bot):
  await bot.add_cog(ArchetypeSubmittedCommand(bot))
