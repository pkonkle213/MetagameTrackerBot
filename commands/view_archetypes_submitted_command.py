from discord import Interaction, app_commands
from discord.ext import commands

from checks import IsPaidStore
from output_builder import BuildTableOutput
from services.command_error_service import Error
from services.submitted_archetypes_service import SubmittedArchetypesReport


class ArchetypeSubmittedCommand(commands.Cog):
    def __init__(self, bot:commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="view_submissions",
        description="Generate a report of the archetypes submitted and by whom",
    )
    @app_commands.guild_only()
    @app_commands.checks.has_role("MTSubmitter")
    @IsPaidStore()
    async def ViewSubmittedArchetypes(
        self, interaction: Interaction, player_name: str = "", event_date: str = ""
    ):
        """
        Parameters
        ----------
        player_name: string
          The player the archetype was submitted for
        event_date: string
          The date of the event (MM/DD/YYYY)
        """
        await interaction.response.defer(ephemeral=True, thinking=False)
        table = SubmittedArchetypesReport(interaction, player_name, event_date)
        if len(table.data) == 0:
            await interaction.followup.send(
                "No archetypes submitted for this store or format"
            )
        else:
            output = BuildTableOutput(table.title, table.headers, table.data)
            await interaction.followup.send(output, ephemeral=True)

    @ViewSubmittedArchetypes.error
    async def Errors(
        self, interaction: Interaction, error: app_commands.AppCommandError
    ):
        await Error(self.bot, interaction, error)


async def setup(bot:commands.Bot):
    await bot.add_cog(ArchetypeSubmittedCommand(bot))
