import logging

import pandas as pd
from discord import Interaction

from custom_errors import KnownError
from tuple_conversions import DataConverted

logger = logging.getLogger(__name__)


def EnsureConvertedResults(data: DataConverted) -> None:
    if not data.pairings_data and not data.standings_data:
        raise KnownError(
            "No usable event results were found in the submitted data. "
            "Check the input and try again."
        )


def _failure_message(error: Exception, input_type: str) -> str:
    if isinstance(error, KnownError):
        reason = error.message
    elif isinstance(error, UnicodeError):
        reason = "The file must use UTF-8 text encoding."
    elif isinstance(error, pd.errors.ParserError):
        reason = "The CSV could not be read. Check its formatting and try again."
    elif isinstance(error, IndexError):
        reason = (
            "The submitted data or CSV filename is incomplete or incorrectly "
            "formatted. Check it and try again."
        )
    elif isinstance(error, ValueError):
        reason = (
            "The submitted data or CSV filename contains an invalid value. "
            "Check it and try again."
        )
    else:
        logger.error(
            "Unexpected error processing %s event data",
            input_type,
            exc_info=(type(error), error, error.__traceback__),
        )
        reason = "An unexpected error occurred. Please try again."

    return (
        f"Could not process your {input_type} submission: {reason} "
        "No event results were saved."
    )


async def ReportSubmissionFailure(
    interaction: Interaction, error: Exception, input_type: str
) -> None:
    message = _failure_message(error, input_type)
    try:
        await interaction.followup.send(message, ephemeral=True)
    except Exception:
        logger.exception("Failed to notify the submitter about a %s error", input_type)
