from tuple_conversions import MTBRoles
from discord import Interaction, app_commands
from discord.ext import commands

from checks import IsStore, HasRequiredRoles
from custom_errors import KnownError
from output_builder import BuildTableOutput
from services.command_error_service import Error
from services.event_details_services import GetEventStats


class UniqueSubmitters(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="events_statistics",
        description="See unique submitters and percent reported for all events",
    )
    @HasRequiredRoles([MTBRoles.MTSubmitter.name])
    @app_commands.guild_only()
    @app_commands.checks.cooldown(1, 60.0, key=lambda i: (i.guild_id, i.user.id))
    @IsStore()
    async def MyEventsReported(self, interaction: Interaction):
        await interaction.response.defer(thinking=True, ephemeral=True)
        objects = interaction.extras.get("db_object")
        if not objects or not objects.store or not objects.game or not objects.format:
            raise KnownError("No store, game, or format found.")
        table = await GetEventStats(objects.store, objects.game, objects.format)
        output = BuildTableOutput(table.title, table.headers, table.data)
        for message in output:
            await interaction.followup.send(message, ephemeral=True)

    @MyEventsReported.error
    async def Errors(
        self, interaction: Interaction, error: app_commands.AppCommandError
    ):
        await Error(self.bot, interaction, error)


async def setup(bot: commands.Bot):
    await bot.add_cog(UniqueSubmitters(bot))
