from io import BytesIO

from discord import File, Interaction, app_commands
from discord.ext import commands

from checks import HasRequiredRoles, IsPaidStore
from output_builder import BuildTableOutput
from services.command_error_service import Error
from services.store_attendance_graph_services import GetAttendanceGraph
from services.store_attendance_services import GetAttendance
from tuple_conversions import MTBRoles


class EventAttendance(commands.GroupCog, name="attendance"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="table", description="Get the attendance table for a date range"
    )
    @app_commands.guild_only()
    @app_commands.checks.cooldown(1, 60.0, key=lambda i: (i.guild_id, i.user.id))
    async def Table(
        self, interaction: Interaction, start_date: str = "", end_date: str = ""
    ):
        """Show attendance in a table (dates use MM/DD/YYYY)."""
        await interaction.response.defer(thinking=True)
        objects = interaction.extras.get("db_object")
        table = await GetAttendance(objects, start_date, end_date)
        if not table.data:
            await interaction.followup.send(
                "No attendance data found for this store and/or format"
            )
        else:
            output = BuildTableOutput(table.title, table.headers, table.data)
            for message in output:
                await interaction.followup.send(message)

    @app_commands.command(
        name="graph", description="Graph store event attendance over time"
    )
    @app_commands.guild_only()
    @HasRequiredRoles([MTBRoles.MTStore.name])
    @IsPaidStore()
    @app_commands.describe(
        start_date="Beginning of date range (MM/DD/YYYY); defaults to one year before end date",
        end_date="End of date range (MM/DD/YYYY); defaults to today",
    )
    async def Graph(
        self,
        interaction: Interaction,
        start_date: str | None = None,
        end_date: str | None = None,
    ):
        await interaction.response.defer(ephemeral=True, thinking=True)
        objects = interaction.extras.get("db_object")
        graph = await GetAttendanceGraph(objects, start_date, end_date)
        await interaction.followup.send(
            file=File(BytesIO(graph), filename="attendance_graph.png"), ephemeral=True
        )

    @Table.error
    @Graph.error
    async def AttendanceError(
        self, interaction: Interaction, error: app_commands.AppCommandError
    ):
        await Error(self.bot, interaction, error)


async def setup(bot: commands.Bot):
    await bot.add_cog(EventAttendance(bot))
