from input_modals.hub_league_input_modal import HubLeagueInputModal
import pandas as pd
from data.metagame_data import GetLeagueMetagame
from input_modals.league_selector import LeagueSelector
from input_modals.hub_league_selector import HubLeagueSelector
from tuple_conversions import (
    League,
    MetagameResult,
    TopPlayers,
    PlayerStanding,
    LeaderboardRace,
)
from interaction_objects import GetObjectsFromInteraction
from data.league_data import (
    GetFullLeagueLeaderboard,
    GetLeagues,
    GetLeagueLeaderboard,
    GetPlayerStanding,
    GetLeaderboardTimeLapse,
    GetHubLeagues
)
from custom_errors import KnownError
from discord.ext import commands
from discord import Interaction, File
from input_modals.league_input_modal import LeagueInputModal
import bar_chart_race as bcr


async def SelectLeague(
    bot: commands.Bot,
    interaction: Interaction,
    isEdit: bool = False
) -> League:
    """Selects a league from the database"""
    objects = GetObjectsFromInteraction(interaction)

    if (not objects.hub and not objects.store) or not objects.game or not objects.format or not objects.region:
        raise KnownError(
            "No store, game, or format found. Leagues must be created in a format mapped channel"
        )

    if objects.hub:
        discord_id = objects.hub.discord_id
        leagues = GetHubLeagues(discord_id, objects.game.id, objects.format.id)
        modal = HubLeagueSelector(
            bot,
            objects.hub,
            objects.game,
            objects.format,
            objects.region,
            leagues,
            isEdit=isEdit
        )
        
    if objects.store:
        discord_id = objects.store.discord_id
        leagues = GetLeagues(discord_id, objects.game.id, objects.format.id)
        modal = LeagueSelector(
            bot,
            objects.store,
            objects.game,
            objects.format,
            leagues,
            isEdit=isEdit
        )
        
    await interaction.response.send_modal(modal)
    await modal.wait()

    return modal.league


def FindPlayerStanding(league: League, user_id: int, discord_id: int) -> PlayerStanding:
    """Displays the player's standing in a league"""
    return GetPlayerStanding(league, user_id, discord_id)


def LeagueLeaderboard(league: League) -> list[TopPlayers]:
    """Displays the leaderboard of a league"""
    return GetLeagueLeaderboard(league)


def FullLeagueLeaderboard(league: League) -> list[TopPlayers]:
    """Displays the leaderboard of a league"""
    return GetFullLeagueLeaderboard(league)


def LeagueTimeLapse(league: League) -> File:  # TODO: Should return a file, probably?
    """Gets data for a racing leaderboard of a league"""
    rows = GetLeaderboardTimeLapse(league)

    if len(rows) == 0:
        raise KnownError("No data found for this league")

    df = pd.DataFrame(rows, columns=["Date", "Player", "Points"])

    pivot_df = df.groupby(["Date", "Player"])["Points"].sum().unstack()
    pivot_df = pivot_df.fillna(0)
    pivot_df.index = pd.to_datetime(pivot_df.index)
    pivot_df = pivot_df.cumsum()
    output_filename = "racing_bar_chart.mp4"
    bcr.bar_chart_race(
        df=pivot_df,
        filename=output_filename,
        orientation="h",
        sort="desc",
        n_bars=8,
        title="League Points Leaders",
        figsize=(6, 4),
        period_length=1500,
    )

    file = File(output_filename, filename="racing_bars.mp4")
    return file


def LeagueMetagame(league: League) -> list[MetagameResult]:
    """Displays the metagame of a league"""
    return GetLeagueMetagame(league)


async def ViewLeague(bot: commands.Bot, interaction: Interaction) -> str:
    """View a league"""
    league = await SelectLeague(bot, interaction)
    return f"""{league.name}
  -------------------
  Start Date: {league.start_date.strftime("%m/%d/%Y")}
  End Date: {league.end_date.strftime("%m/%d/%Y")}
  Cuts to Top: {league.top_cut}
  Description: {league.description}"""


async def EditLeague(bot: commands.Bot, interaction: Interaction):
    """Edit a league"""
    await SelectLeague(bot, interaction, isEdit=True)


async def CreateLeague(bot: commands.Bot, interaction: Interaction):
    """Create a league"""
    objects = GetObjectsFromInteraction(interaction)

    if (not objects.store and not objects.hub) or not objects.game or not objects.format:
        raise KnownError("Insufficient mapping to complete this command")

    if objects.store:
        modal = LeagueInputModal(bot, objects.store, objects.game, objects.format)
        await interaction.response.send_modal(modal)
    if objects.hub and objects.format:
        modal = HubLeagueInputModal(bot, objects.hub, objects.game, objects.format)
        await interaction.response.send_modal(modal)
