from discord import Interaction, app_commands
from discord.ext import commands

from checks import IsPaidUser
from services.command_error_service import Error
from services.personal_history_service import (
    GetPersonalPairingsHistory,
    GetPersonalStandingsHistory,
)


class PersonalHistoryCommands(commands.GroupCog, name="history"):
    """A group of commands for getting personal history"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="standings", description="Your history according to standings"
    )
    @app_commands.guild_only()
    @IsPaidUser()
    @app_commands.checks.cooldown(1, 60.0, key=lambda i: (i.guild_id, i.user.id))
    async def GetPersonalStandingsHistory(
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

        await interaction.response.defer(ephemeral=True, thinking=False)
        objects = interaction.extras.get("db_object")
        user_id = interaction.user.id
        output = await GetPersonalStandingsHistory(
            user_id, start_date, end_date, objects
        )
       
        for message in output:
            await interaction.followup.send(message, ephemeral=True)

    @app_commands.command(
        name="pairings", description="Your history according to pairings"
    )
    @app_commands.guild_only()
    @IsPaidUser()
    @app_commands.checks.cooldown(1, 60.0, key=lambda i: (i.guild_id, i.user.id))
    async def GetPersonalPairingsHistory(
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

        await interaction.response.defer(ephemeral=True, thinking=False)
        objects = interaction.extras.get("db_object")
        user_id = interaction.user.id
        output = await GetPersonalPairingsHistory(
            user_id, start_date, end_date, objects
        )
      
        for message in output:
            await interaction.followup.send(message, ephemeral=True)

    @GetPersonalStandingsHistory.error
    @GetPersonalPairingsHistory.error
    async def Errors(
        self, interaction: Interaction, error: app_commands.AppCommandError
    ):
        await Error(self.bot, interaction, error)


async def setup(bot: commands.Bot):
    await bot.add_cog(PersonalHistoryCommands(bot))
