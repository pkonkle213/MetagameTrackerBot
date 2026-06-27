from discord import Interaction, app_commands
from discord.ext import commands

from checks import isPhil
from output_builder import BuildTableOutput
from services.command_error_service import Error
from services.event_details_services import GetEventStats
from settings import BOTGUILDID


class UniqueSubmitters(commands.Cog):
    def __init__(self, bot:commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="events_statistics",
        description="See unique submitters and percent reported for all events",
    )
    @app_commands.guilds(BOTGUILDID)
    @app_commands.check(isPhil)
    async def MyEventsReported(self, interaction: Interaction, discord_id: str = ""):
        """
        Parameters:
        -----------
        discord_id: string
          The discord id of the store to check
        """
        await interaction.response.defer(thinking=True)
        discord_id_int = 0
        if discord_id != "":
            discord_id_int = int(discord_id)
        table = GetEventStats(discord_id_int)
        output = BuildTableOutput(table.title, table.headers, table.data)
        await interaction.followup.send(output)

    @MyEventsReported.error
    async def Errors(
        self, interaction: Interaction, error: app_commands.AppCommandError
    ):
        await Error(self.bot, interaction, error)


async def setup(bot:commands.Bot):
    await bot.add_cog(UniqueSubmitters(bot))
