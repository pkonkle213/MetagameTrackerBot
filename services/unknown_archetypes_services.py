from discord import Interaction
from data.archetype_data import GetUnknownArchetypes
from interaction_data import GetInteractionData
from services.date_functions import BuildDateRange
from checks import isSubmitter

def GetAllUnknown(interaction:Interaction, start_date, end_date):
  game, format, store, user_id = GetInteractionData(interaction, game=True, format=True, store=True)
  date_start, date_end = BuildDateRange(start_date, end_date, format, 4 if isSubmitter(interaction.guild, interaction.user, 'MTSubmitter') else 2)
  data = GetUnknownArchetypes(store.DiscordId,
    game.ID,
    format.ID,
    date_start,
    date_end)
  title = f'Unknown Archetypes from {date_start} to {date_end}'
  headers = ['Date', 'Player Name']
  return data, title, headers