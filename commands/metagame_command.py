from discord import Interaction, app_commands
from discord.ext import commands

from custom_errors import KnownError
from output_builder import BuildTableOutput
from services.command_error_service import Error
from services.date_functions import BuildDateRange
from services.metagame_heatmap_services import SendMetagameHeatmap
from services.metagame_services import (
    FormatLockedMetagame,
    GetWholeMetagame,
    RegionLockedMetagame,
    StoreMetagame,
)
from checks import IsPaidUser, IsStore
from settings import DATAGUILDID
from tuple_conversions import GameEnum, MetagameResult
from data.metagame_heatmap_data import GetMetagameHeatmap


class MetagameCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="metagame", description="Get the metagame for this format"
    )
    @app_commands.checks.cooldown(
        1, 60.0, key=lambda i: (i.guild_id, i.user.id, i.channel_id)
    )
    @app_commands.guild_only()
    async def ViewMetagame(
        self, interaction: Interaction, start_date: str = "", end_date: str = ""
    ):
        """
        Parameters
        ----------
        start_date: string
            The start date of the metagame (MM/DD/YYYY)
        end_date: string
            The end date of the metagame (MM/DD/YYYY)
        """
        await interaction.response.defer(thinking=False)
        objects = interaction.extras.get("db_object")

        if not objects or not objects.game or not objects.format:
            raise KnownError(
                "This channel is not set up with a game or format to view a metagame."
            )

        date_start, date_end = BuildDateRange(start_date, end_date, objects.format)

        if not interaction.channel_id:
            raise KnownError("Try a channel that has an id")

        title: str = ""
        data: list[MetagameResult] = []
        if interaction.guild_id == DATAGUILDID:
            data = await GetWholeMetagame(
                objects.game, objects.format, date_start, date_end
            )
            title = f"{objects.format.format_name.title()} metagame from {date_start.strftime('%-m/%-d')} to {date_end.strftime('%-m/%-d')}"
        elif objects.store:
            data = await StoreMetagame(
                objects.store,
                objects.game,
                objects.format,
                date_start,
                date_end,
            )
            title = f"{objects.format.format_name.title()} metagame from {date_start.strftime('%-m/%-d')} to {date_end.strftime('%-m/%-d')}"
        elif objects.hub and objects.hub.region_id:
            data = await RegionLockedMetagame(
                objects.hub,
                objects.game,
                objects.format,
                date_start,
                date_end,
            )
            title = f"{objects.format.format_name.title()} metagame from {date_start.strftime('%-m/%-d')} to {date_end.strftime('%-m/%-d')}"
        elif objects.hub:
            data = await FormatLockedMetagame(
                objects.hub,
                objects.game,
                objects.format,
                objects.region,
                date_start,
                date_end,
            )
            title_name = (
                objects.region.region_name.title()
                if objects.region
                else "General " + objects.format.format_name.title()
            )
            title = f"{title_name} metagame from {date_start.strftime('%-m/%-d')} to {date_end.strftime('%-m/%-d')}"
        else:
            raise KnownError(
                "This channel is not set up with a store or hub to view a metagame."
            )

        if len(data) == 0:
            await interaction.followup.send(
                "No metagame data found for this discord and format"
            )
        else:
            headers = ["Deck Archetype", "Meta %", "Win %"]
            output = BuildTableOutput(title, headers, data)
            await interaction.followup.send(output)

    @app_commands.command(
        name="metagame_heatmap",
        description="Get a private heatmap of the top 16 archetypes in this format",
    )
    @app_commands.checks.cooldown(
        1, 60.0, key=lambda i: (i.guild_id, i.user.id, i.channel_id)
    )
    @app_commands.guild_only()
    # @IsPaidUser()
    @IsStore()
    async def ViewMetagameHeatmap(
        self, interaction: Interaction, start_date: str = "", end_date: str = ""
    ) -> None:
        await interaction.response.defer(ephemeral=True, thinking=True)
        objects = interaction.extras.get("db_object")
        if not objects or not objects.game or not objects.format:
            raise KnownError(
                "This channel is not set up with a game or format to view a metagame."
            )

        date_start, date_end = BuildDateRange(
            start_date, end_date, objects.format
        )

        if interaction.guild_id == DATAGUILDID:
            scope, scope_id = "data", None
        elif objects.store:
            scope, scope_id = "store", objects.store.discord_id
        elif objects.hub:
            scope, scope_id = "hub", objects.hub.discord_id
        else:
            raise KnownError(
                "This channel is not set up with a store or hub to view a metagame."
            )

        rows = await GetMetagameHeatmap(
            objects.game.id,
            objects.format.id,
            date_start,
            date_end,
            scope,
            scope_id,
        )
        if not rows:
            await interaction.followup.send(
                "No matchup data found for this format and date range.",
                ephemeral=True,
            )
            return

        title = (
            f"{objects.format.format_name.title()} metagame heatmap "
            f"from {date_start.strftime('%-m/%-d')} to "
            f"{date_end.strftime('%-m/%-d')}"
        )
        await SendMetagameHeatmap(interaction, title, rows)

    @ViewMetagame.error
    @ViewMetagameHeatmap.error
    async def Errors(
        self, interaction: Interaction, error: app_commands.AppCommandError
    ):
        await Error(self.bot, interaction, error)


async def setup(bot: commands.Bot):
    await bot.add_cog(MetagameCommand(bot))
