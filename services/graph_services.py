import pandas as pd
import matplotlib.pyplot as plt
from services.date_functions import BuildDateRange
from interaction_objects import GetObjectsFromInteraction
from custom_errors import KnownError
from discord import Interaction, File
from data.metagame_data import GetMetagame


def MetagameScatterPlot(interaction: Interaction, start_date: str,
                        end_date: str) -> File:
  """Creates a scatter plot of the metagame for a given format"""
  store, game, format = GetObjectsFromInteraction(interaction)
  if store is None:
    raise KnownError(
        'This server is not mapped to a store. Please contact your store owner to have them map the server.'
    )
  if game is None:
    raise KnownError(
        'This category is not mapped to a game. Please contact your store owner to have them map the category.'
    )
  if format is None:
    raise KnownError(
        'This channel is not mapped to a format. Please contact your store owner to have them map the channel.'
    )

  date_start, date_end = BuildDateRange(start_date, end_date, format)

  data = GetMetagame(game, format, date_start, date_end, store)
  print('Data:', data)
  if data is None:
    raise KnownError('No data found for the given format and date range.')

  dataframe = pd.DataFrame(
      data, columns=['Archetype', 'Metagame Percent',
                     'Win Percent'])  # type: ignore[arg-type]

  fig = plt.figure()
  ax = fig.add_subplot()

  ax.scatter(dataframe["Metagame Percent"],
             dataframe["Win Percent"],
             color='blue',
             marker='o')
  ax.set_xlabel('Metagame Percent')
  ax.set_ylabel('Win Percent')
  ax.set_title('Metagame Between ' + date_start.strftime('%-m/%-d/%Y') +
               ' and ' + date_end.strftime('%-m/%-d/%Y'))
  ax.legend(labels=dataframe["Archetype"])

  #TODO: This should be a more specific path/filename, probably using Replit's internal storage.
  file_path = "metagame.png"
  fig.savefig(file_path)

  with open(file_path, "rb") as f:
    pic = File(f, filename=file_path)

  return pic
