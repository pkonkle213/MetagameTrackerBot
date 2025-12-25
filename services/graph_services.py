import pandas as pd
import matplotlib.pyplot as plt
from services.date_functions import BuildDateRange
from interaction_objects import GetObjectsFromInteraction
from custom_errors import KnownError
from discord import Interaction
from data.metagame_data import GetMetagame

def MetagameScatterPlot(interaction:Interaction, start_date: str, end_date: str):
  """Creates a scatter plot of the metagame for a given format"""
  store, game, format = GetObjectsFromInteraction(interaction)
  if store is None:
     raise KnownError('This server is not mapped to a store. Please contact your store owner to have them map the server.')
  if game is None:
    raise KnownError('This category is not mapped to a game. Please contact your store owner to have them map the category.')
  if format is None:
    raise KnownError('This channel is not mapped to a format. Please contact your store owner to have them map the channel.')
    
  date_start, date_end = BuildDateRange(start_date, end_date, format)

  data = GetMetagame(game, format, date_start, date_end, store)
  if data is None:
    raise KnownError('No data found for the given format and date range.')

  dataframe = pd.DataFrame(data, columns=['Archetype', 'Metagame Percent', 'Win Percent'])  # type: ignore[arg-type]

  fig = plt.figure()
  ax = fig.add_subplot()

  
    
  #For the rest, I believe there's some code written in _nonfunctioning/experiment_dataplot.py that I can use as an example