from discord import Embed

from data.personal_matchup_data import GetPersonalMatchups
from services.command_error_service import KnownError
from services.date_functions import BuildDateRange
from tuple_conversions import (
    InteractionObjects,
    OpponentArchetype,
    PersonalArchetype,
    PersonalMatchupRows,
)


async def PersonalMatchups(
    start_date: str, end_date: str, objects: InteractionObjects | None, user_id: int
) -> list[Embed]:
    if not objects or not objects.store or not objects.game or not objects.format:
        raise KnownError("No Store, Game, or Format Found")
    date_start, date_end = BuildDateRange(start_date, end_date, objects.format)

    data = await GetPersonalMatchups(
        user_id,
        objects.store.discord_id,
        objects.game,
        objects.format,
        date_start,
        date_end,
    )

    archetypes = BuildPersonalMatchups(data)
    outputs = BuildMatchupsOutput(archetypes)
    return outputs


def BuildPersonalMatchups(
    matchups: list[PersonalMatchupRows],
) -> list[PersonalArchetype]:
    active_archetype = 0
    new_matchups: list[PersonalArchetype] = []
    for row in matchups:
        opponent = OpponentArchetype(
            row.opponent_archetype, row.total_matches, row.win_percent
        )
        if row.player_archetype_rank != active_archetype:
            active_archetype = max(active_archetype, row.player_archetype_rank)
            new_matchups.append(
                PersonalArchetype(
                    row.player_archetype,
                    [opponent],
                )
            )
        else:
            new_matchups[active_archetype - 1].matchups.append(opponent)

    return new_matchups


def BuildMatchupsOutput(archetypes: list[PersonalArchetype]) -> list[Embed]:
    archetype_output: list[Embed] = []
    for archetype in archetypes:
        title = f"{archetype.archetype} - Win Percentages"
        description: list[str] = []
        for matchup in archetype.matchups:
            description.append(
                f"{matchup.archetype_name} - {matchup.win_percent}% ({matchup.total_matches} match{'es' if matchup.total_matches > 1 else ''})"
            )
        body = "\n".join(description)
        output = Embed(title=title, description=body)
        archetype_output.append(output)

    return archetype_output
