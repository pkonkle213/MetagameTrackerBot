from data.event_data import GetEventDetails
from tuple_conversions import OutputToBuild, MetagameResult, Event
from data.metagame_data import OneEventMetagame


async def OneEventDetails(event: Event) -> OutputToBuild:
    data = await GetEventDetails(event.id)
    title = f"{event.event_name} Results ({len(data)} attended)"
    headers = ["Archetype", "Wins", "Losses", "Draws"]
    return OutputToBuild(title, headers, data)


async def OneEventMeta(event: Event) -> OutputToBuild:
    data = await OneEventMetagame(event)
    title = f"{event.event_name}'s Metagame"
    headers = ["Archetype", "Metagame %", "Win %"]
    return OutputToBuild(title, headers, data)
