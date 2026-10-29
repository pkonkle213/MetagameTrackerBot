from output_builder import BuildTableOutput
from tuple_conversions import DataConverted

def BuildReviewOutput(data: DataConverted) -> list[str]:
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

  if data.errors:
    for error in data.errors:
      output.append(f'\n`{error}`')

  if (
    data.event_name is not None
    and data.event_date is not None
    and data.custom_event_id is not None
  ):
    output.append(
      f"\nMelee event details: {data.event_name} "
      f"({data.event_date:%m/%d/%Y}, ID {data.custom_event_id})"
    )

  return output