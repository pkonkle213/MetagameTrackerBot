from discord import Interaction, app_commands
from discord.ext import commands

from checks import IsStore
from output_builder import BuildTableOutput
from services.command_error_service import Error
from services.store_attendance_services import GetStoreAttendance


class EventAttendance(commands.Cog):
    def __init__(self, bot:commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="attendance", description="Get the attendance for a date range"
    )
    @app_commands.guild_only()
    @IsStore()
    @app_commands.checks.cooldown(1, 60.0, key=lambda i: (i.guild_id, i.user.id))
    async def Attendance(
        self, interaction: Interaction, start_date: str = "", end_date: str = ""
    ):
        """
        Parameters
        ----------
        start_date: string
          Beginning of Date Range (MM/DD/YYYY)
        end_date: string
          End of Date Range (MM/DD/YYYY)
        """
        await interaction.response.defer(thinking=False)
        table = GetStoreAttendance(interaction, start_date, end_date)
        if len(table.data) == 0:
            await interaction.followup.send(
                "No attendance data found for this store and/or format"
            )
        else:
            output = BuildTableOutput(table.title, table.headers, table.data)
            await interaction.followup.send(output)

    @Attendance.error
    async def Errors(
        self, interaction: Interaction, error: app_commands.AppCommandError
    ):
        await Error(self.bot, interaction, error)


async def setup(bot:commands.Bot):
    await bot.add_cog(EventAttendance(bot))
