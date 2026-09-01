from data.event_details_data import GetAllEventsStats
from tuple_conversions import OutputToBuild, Game, Store, Format


def GetEventStats(store: Store, game: Game, format: Format) -> OutputToBuild:
    data = GetAllEventsStats(store, game, format)
    title = "Event Statistics"
    headers = [
        "Event Date",
        "Archetypes Submitted",
        "Players Attended",
        "Archetypes Percent",
        "Distinct Users Submitted",
        "Users Percent",
    ]
    return OutputToBuild(title, headers, data)
