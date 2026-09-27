from discord import Embed
from discord import Interaction
from data.personal_matchup_data import GetPersonalMatchups
from data.interaction_data import GetObjectsFromInteraction
from services.command_error_service import KnownError
from services.date_functions import BuildDateRange
from tuple_conversions import (
    OutputToBuild,
    PersonalMatchupRows,
    PersonalArchetype,
    OpponentArchetype,
)


async def PersonalMatchups(
    interaction: Interaction, start_date: str, end_date: str
) -> list[Embed]:
    objects = await GetObjectsFromInteraction(interaction)
    if not objects.store or not objects.game or not objects.format:
        raise KnownError("No Store, Game, or Format Found")
    user_id = interaction.user.id
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
            row.opponent_archetype, row.total_games, row.win_percent
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
        title = f"{archetype.archetype}"
        description = ""
        for matchup in archetype.matchups:
            description += f"{matchup.archetype_name} - {matchup.win_percent} ({matchup.total_games} games)"
        output = Embed(title=title, description=description)
        archetype_output.append(output)

    return archetype_output
