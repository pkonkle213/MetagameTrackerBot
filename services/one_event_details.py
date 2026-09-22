from data.event_data import GetEventDetails
from tuple_conversions import OutputToBuild, MetagameResult, Event
from data.metagame_data import OneEventMetagame

def OneEventDetails(
    event: Event,
) -> OutputToBuild:
    data = GetEventDetails(event.id)
    title = f"{event.event_name} Results ({len(data)} attended)"
    headers = ["Archetype", "Wins", "Losses", "Draws"]
    return OutputToBuild(title, headers, data)


def OneEventMeta(event: Event) -> tuple[str, list[str], list[MetagameResult]]:
    data = OneEventMetagame(event)
    title = f"{event.event_name}'s Metagame"
    headers = ["Archetype", "Metagame %", "Win %"]
    return title, headers, data
