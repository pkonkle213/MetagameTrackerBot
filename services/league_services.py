from output_builder import BuildTableOutput
from data.metagame_data import GetLeagueMetagame
from select_menu_bones import SelectMenu
from tuple_conversions import Store, Game, Format, League, MetagameResult, TopPlayers
from services.date_functions import ConvertToDate
from interaction_objects import GetObjectsFromInteraction
from data.league_data import InsertLeague, GetLeagues, GetLeagueLeaderboard
from custom_errors import KnownError
from discord.ext import commands
from discord import Interaction
from typing import Tuple
from input_modals.league_input_modal import LeagueInputModal

#TODO: Upgrade the select menu to be league specific.
async def SelectLeague(bot: commands.Bot, interaction: Interaction) -> Tuple[Store, Game, Format, League]:
  """Selects a league from the database"""
  store, game, format = GetObjectsFromInteraction(interaction)

  if not store or not game or not format:
    raise KnownError("No store, game, or format found. Leagues must be created in a format mapped channel")

  leagues = GetLeagues(store.discord_id, game.id, format.id)
  if not leagues or len(leagues) == 0:
    raise KnownError("No leagues found for this game and format")

  league = await SelectMenu(interaction, "Please select a league", "Choose a league", leagues)
  
  return store, game, format, league[0]

def LeagueLeaderboard(league:League) -> list[TopPlayers]:
  """Displays the leaderboard of a league"""
  return GetLeagueLeaderboard(league)

def LeagueMetagame(league:League) -> list[MetagameResult]:
  """Displays the metagame of a league"""
  return GetLeagueMetagame(league)

async def EditLeague(bot: commands.Bot, interaction: Interaction) -> League:
  """Helps the store edit a league"""
  store, game, format, league = await SelectLeague(bot, interaction)

  #TODO: Can't send a modal after the SelectMenu is done. Need to figure out how to do this.
  modal = LeagueInputModal(league)
  await interaction.response.send_modal(modal)
  await modal.wait()

  if not modal.is_submitted:
    raise KnownError("LeagueInput modal was dismissed or timed out. Please try again.")

  league_name = modal.submitted_name
  description = modal.submitted_description
  print('League name:', league_name)

  return modal  

async def CreateLeague(bot: commands.Bot, interaction: Interaction) -> League:
  """Helps the store create a league"""
  store, game, format = GetObjectsFromInteraction(interaction)

  if not store or not game or not format:
    raise KnownError("No store, game, or format found. Leagues must be created in a format mapped channel")

  modal = LeagueInputModal()
  await interaction.response.send_modal(modal)
  await modal.wait()

  if not modal.is_submitted:
    raise KnownError("LeagueInput modal was dismissed or timed out. Please try again.")

  league_name = modal.submitted_name
  description = modal.submitted_description
  
  try:
    start_date = ConvertToDate(modal.submitted_start_date)
    end_date = ConvertToDate(modal.submitted_end_date)
    top_cut = int(modal.submitted_top_cut)
  except Exception as e:
    raise KnownError('Error creating league. Please ensure all fields are filled out with the correct formatting.')
    
  if start_date > end_date:
    raise KnownError('Start date must be before end date')

  league = InsertLeague(league_name, description, start_date, end_date, top_cut, store.discord_id, game.id, format.id, interaction.user.id)
  return league