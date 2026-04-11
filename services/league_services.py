from select_menu_bones import SelectMenu
from tuple_conversions import League
from services.date_functions import ConvertToDate
from interaction_objects import GetObjectsFromInteraction
from data.league_data import InsertLeague, GetLeagues
from custom_errors import KnownError
from discord.ext import commands
from discord import Interaction
from input_modals.league_input_modal import LeagueInputModal

async def EditLeague(bot: commands.Bot, interaction: Interaction) -> League:
  """Helps the store edit a league"""
  store, game, format = GetObjectsFromInteraction(interaction)

  if not store or not game or not format:
    raise KnownError("No store, game, or format found. Leagues must be created in a format mapped channel")

  leagues = GetLeagues(store.discord_id, game.id, format.id)
  if not leagues or len(leagues) == 0:
    raise KnownError("No leagues found for this game and format")

  result = await SelectMenu(interaction, "Please select a league to edit", "Choose a league", leagues)

  #TODO: Can't send a modal after the SelectMenu is done. Need to figure out how to do this.
  modal = LeagueInputModal(result[0])
  await interaction.response.send_modal(modal)
  await modal.wait()

  if not modal.is_submitted:
    raise KnownError("LeagueInput modal was dismissed or timed out. Please try again.")

  league_name = modal.submitted_name
  description = modal.submitted_description
  print('League name:', league_name)

  return result[0]
  

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