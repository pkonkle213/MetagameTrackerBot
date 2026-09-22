from input_modals.submit_archetype_general_modal import SubmitArchetypeModal
from input_modals.submit_archetype_magic_limited_modal import (
    MagicLimitedSubmitArchetypeModal,
)
from input_modals.submit_archetype_lorcana_modal import LorcanaSubmitArchetypeModal
from tuple_conversions import Event, Game, Format, Store, GameEnum, Hub
from discord import Interaction
from discord.ext import commands


async def GetArchetypeModal(
    bot: commands.Bot,
    userId: int,
    events: list[Event],
    interaction: Interaction,
    store: Store | None,
    hub: Hub | None,
    game: Game,
    format: Format,
    player_name: str,
    player_archetypes: list[str],
    is_submitter: bool
) -> None:
    """Determines which modal to use based on the game and format"""
    # TODO: Probably needs to be a case statement for the future
    if game.id == GameEnum.Magic.value and format.is_limited:
        modal = MagicLimitedSubmitArchetypeModal(
            bot, game, format, userId, events, player_name, player_archetypes
        )
    elif game.id == GameEnum.Lorcana.value:
        modal = LorcanaSubmitArchetypeModal(
            bot, game, format, userId, events, player_name, player_archetypes
        )
    else:
        modal = SubmitArchetypeModal(
            bot,
            store,
            hub,
            game,
            format,
            userId,
            events,
            player_name,
            player_archetypes,
            is_submitter,
        )
    await interaction.response.send_modal(modal)
    await modal.wait()
