from output_builder import BuildTableOutput
from data.metagame_data import GetLeagueMetagame
from input_modals.league_selector import LeagueSelector, ConfirmView
from tuple_conversions import Store, Game, Format, League, MetagameResult, TopPlayers, PlayerStanding
from services.date_functions import ConvertToDate
from interaction_objects import GetObjectsFromInteraction
from data.league_data import InsertLeague, GetLeagues, GetLeagueLeaderboard, GetPlayerStanding
from custom_errors import KnownError
from discord.ext import commands
from discord import Interaction
from typing import Tuple
from input_modals.league_input_modal import LeagueInputModal

async def SelectLeague(
  bot:commands.Bot,
  interaction: Interaction,
  isEdit:bool = False
) -> Tuple[Store, Game, Format, League]:
  """Selects a league from the database"""
  objects = GetObjectsFromInteraction(interaction)

  if not objects.store or not objects.game or not objects.format:
    raise KnownError("No store, game, or format found. Leagues must be created in a format mapped channel")

  leagues = GetLeagues(objects.store.discord_id, objects.game.id, objects.format.id)
  if not leagues or len(leagues) == 0:
    raise KnownError("No leagues found for this game and format")

  modal = LeagueSelector(bot, objects.store, objects.game, objects.format, leagues, isEdit=isEdit)
  await interaction.response.send_modal(modal)
  await modal.wait()

  if not modal.is_submitted:
    raise KnownError("League Selector modal was dismissed or timed out. Please try again.")

  league = modal.league
  
  return objects.store, objects.game, objects.format, league

def PlayerStanding(league:League, user_id:int, discord_id:int) -> PlayerStanding:
  """Displays the player's standing in a league"""
  return GetPlayerStanding(league, user_id, discord_id)

def LeagueLeaderboard(league:League) -> list[TopPlayers]:
  """Displays the leaderboard of a league"""
  return GetLeagueLeaderboard(league)

def LeagueMetagame(league:League) -> list[MetagameResult]:
  """Displays the metagame of a league"""
  return GetLeagueMetagame(league)

async def EditLeague(bot:commands.Bot, interaction: Interaction):
  """Helps the store edit a league"""
  await SelectLeague(bot, interaction, isEdit=True)

async def CreateLeague(bot: commands.Bot, interaction: Interaction):
  """Helps the store create a league"""
  objects = GetObjectsFromInteraction(interaction)

  if not objects.store or not objects.game or not objects.format:
    raise KnownError("No store, game, or format found. Leagues must be created in a format mapped channel")

  modal = LeagueInputModal(bot, objects.store, objects.game, objects.format)
  await interaction.response.send_modal(modal)
  