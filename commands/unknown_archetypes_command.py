from discord import Interaction, app_commands
from discord.ext import commands

from checks import IsStore
from output_builder import BuildTableOutput
from services.command_error_service import Error
from services.unknown_archetypes_services import GetAllUnknown


class UnknownArchetypes(commands.Cog):
    def __init__(self, bot:commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="unknown",
        description="See what archetypes still need submitted for a date range",
    )
    @app_commands.guild_only()
    @IsStore()
    @app_commands.checks.cooldown(1, 60.0, key=lambda i: (i.guild_id, i.user.id))
    async def IntoTheUnknown(
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
        table = GetAllUnknown(interaction, start_date, end_date)
        if len(table.data) == 0:
            await interaction.followup.send(
                "Congratulations! No unknown archetypes found for this format"
            )
        else:
            output = BuildTableOutput(table.title, table.headers, table.data)
            output = output[:1940]
            output += "...```\nTo submit yours, use the command `/submit archetype`"
            await interaction.followup.send(output)

    @IntoTheUnknown.error
    async def Errors(
        self, interaction: Interaction, error: app_commands.AppCommandError
    ):
        await Error(self.bot, interaction, error)


async def setup(bot:commands.Bot):
    await bot.add_cog(UnknownArchetypes(bot))
