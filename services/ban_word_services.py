from tuple_conversions import OutputToBuild
from custom_errors import KnownError
from typing import Any
from pyparsing import Word
from data.interaction_data import GetObjectsFromInteraction
from data.ban_word_data import (
    AddWord,
    GetWord,
    MatchDisabledArchetypes,
    DisableMatchingWords,
    AddBadWordBridge,
    CheckStoreBannedWords,
    GetOffenders,
)
from discord import Interaction


async def AddBadWord(interaction: Interaction, bad_word: str) -> None:
    word = await GetWord(bad_word)
    if not word:
        word = await AddWord(bad_word)

    discord_id = interaction.guild_id
    if not discord_id:
        raise KnownError("Only able to ban words from stores")

    bridge_check = await AddBadWordBridge(discord_id, word.id)
    if bridge_check is None:
        raise KnownError("Unable to ban the word for this store")

    await DisableMatchingWords(discord_id, bad_word.upper())


async def ContainsBadWord(discord_id: int, archetype: str) -> bool:
    return await CheckStoreBannedWords(discord_id, archetype)


async def CanSubmitArchetypes(discord_id: int, user_id: int) -> bool:
    offenses = await MatchDisabledArchetypes(discord_id, user_id)
    return offenses < 3


async def Offenders(interaction: Interaction) -> OutputToBuild:
    objects = await GetObjectsFromInteraction(interaction)
    if not objects.store:
        raise KnownError("This command is only available to stores")
    offenders = await GetOffenders(objects.game, objects.format, objects.store)
    headers = [
        "Date Submitted",
        "Submitter",
        "Submitter ID",
        "Event Date",
        "Player Name",
        "Archetype Played",
    ]
    if not objects.format:
        headers.insert(5, "Format")
    if not objects.game:
        headers.insert(5, "Game")
    title = "Those who have been flagged for bad words/phrases"
    return OutputToBuild(title, headers, offenders)
