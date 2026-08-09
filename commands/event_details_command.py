from interaction_objects import GetObjectsFromInteraction
from discord import Interaction, app_commands
from discord.ext import commands

from checks import isPhil
from output_builder import BuildTableOutput
from services.command_error_service import Error
from services.event_details_services import GetEventStats
from settings import BOTGUILDID
from checks import IsStore


class UniqueSubmitters(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="events_statistics",
        description="See unique submitters and percent reported for all events",
    )
    @app_commands.checks.has_role("MTSubmitter")
    @app_commands.guild_only()
    @IsStore()
    async def MyEventsReported(self, interaction: Interaction):
        await interaction.response.defer(thinking=True)
        objects = GetObjectsFromInteraction(interaction)
        if not objects.store or not objects.game or not objects.format:
            raise Exception("No store, game, or format found.")
        table = GetEventStats(objects.store, objects.game, objects.format)
        output = BuildTableOutput(table.title, table.headers, table.data)
        await interaction.followup.send(output)

    @MyEventsReported.error
    async def Errors(
        self, interaction: Interaction, error: app_commands.AppCommandError
    ):
        await Error(self.bot, interaction, error)


async def setup(bot: commands.Bot):
    await bot.add_cog(UniqueSubmitters(bot))
