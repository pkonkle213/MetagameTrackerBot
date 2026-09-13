from data.event_data import GetEventDetails
from tuple_conversions import OutputToBuild, Event


def OneEventDetails(
    event: Event,
) -> OutputToBuild:
    data = GetEventDetails(event.id)
    title = f"{event.event_name} Results ({len(data)} attended)"
    headers = ["Archetype", "Wins", "Losses", "Draws"]
    return OutputToBuild(title, headers, data)
