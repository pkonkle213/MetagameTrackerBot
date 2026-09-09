import pandas as pd

from custom_errors import KnownError
from incoming_message_conversions.csv_carde_io import (
    ConvertToPairings,
    ConvertToStandings,
)
from incoming_message_conversions.magic_companion import (
    CompanionPairings,
    CompanionStandings,
)
from tuple_conversions import DataConverted


def ConvertCSVToData(dataframe: pd.DataFrame) -> DataConverted:
    errors = None
    standings_data = None
    pairings_data = None

    pairings_data, errors = ConvertToPairings(dataframe)

    if pairings_data is None:
        standings_data, errors = ConvertToStandings(dataframe)

    if pairings_data is None and standings_data is None:
        raise KnownError("Unable to parse data. Please try again.")

    return DataConverted(pairings_data, standings_data, errors, None, None)


def ConvertMessageToData(message: str) -> DataConverted:
    errors = None
    standings_data = None
    pairings_data = None

    # magic - companion - standings - 4 spaces
    standings_data, errors = CompanionStandings(message, "    ")

    if standings_data is None:
        # magic - companion - standings - tab
        standings_data, errors = CompanionStandings(message, "\t")

    if standings_data is None:
        # magic - companion - pairings
        pairings_data, errors = CompanionPairings(message)

    if standings_data is None and pairings_data is None:
        raise KnownError("Unable to parse data. Please try again.")

    return DataConverted(pairings_data, standings_data, errors, None, None)
