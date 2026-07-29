from output_builder import BuildTableOutput
from tuple_conversions import DataConverted

def BuildReviewOutput(data: DataConverted) -> str:
  if data.standings_data:
    title = "Data Received"
    headers = ["Player Name","Wins","Losses","Draws"]
    table_data = data.standings_data
    output = BuildTableOutput(title, headers, table_data)
  if data.pairings_data:
    title = "Data Received"
    headers = ["Round","Player 1 Name","Player 1 Wins","Player 2 Wins","Player 2 Name"]
    table_data = data.pairings_data
    output = BuildTableOutput(title, headers, table_data)

  return output