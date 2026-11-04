from discord import Interaction
from discord.ext import commands

from custom_errors import KnownError
from data.archetype_data import (
    BulkAddArchetypes,
    GetOpponentArchetypes,
    OpponentArchetype,
)
from input_modals.opponent_archetype_modal import OpponentArchetypeModal
from services.mass_archetype_workflow import SelectEvent
from services.submit_archetype_service import NotifyArchetypeSubmission
from tuple_conversions import Event, Format, Game, PlayerArchetype, Store, ViewButtonEnum
from views.confirm_event import ConfirmEvent


async def SubmitOpponentArchetypes(
    bot: commands.Bot,
    interaction: Interaction,
    store: Store,
    game: Game,
    format: Format,
) -> None:
    event, active_interaction = await SelectEvent(interaction, store, game, format)
    if event is None:
        await interaction.followup.send("Canceled!", ephemeral=True)
        return
    if active_interaction is None:
        raise KnownError("Event selection did not return an interaction.")
    if interaction.guild is None:
        raise KnownError("This command must be used in a server.")

    opponents = await GetOpponentArchetypes(
        event.id, interaction.user.id, interaction.guild_id
    )
    if not opponents:
        raise KnownError("No opponents were found for you in this event.")

    final_interaction = await SubmitOpponentArchetypeBatch(
        bot, interaction, active_interaction, event, opponents, store
    )
    if final_interaction is None:
        await interaction.followup.send("Canceled!", ephemeral=True)


async def SubmitOpponentArchetypeBatch(
    bot: commands.Bot,
    interaction: Interaction,
    active_interaction: Interaction,
    event: Event,
    opponents: list[OpponentArchetype],
    store: Store,
) -> Interaction | None:
    batch = opponents[:5]
    remaining_opponents = opponents[5:]

    modal = OpponentArchetypeModal(batch)
    await active_interaction.response.send_modal(modal)
    await modal.wait()

    if not modal.is_submitted or modal.interaction is None:
        raise KnownError("Opponent archetypes were not submitted.")

    changed: list[PlayerArchetype] = modal.new_archetypes
    if changed:
        await BulkAddArchetypes(
            event,
            changed,
            interaction.user.id,
            interaction.user.name,
            interaction.guild_id,
            interaction.guild.name if interaction.guild else "",
            is_submitter=False,
        )
        for archetype in changed:
            event = await NotifyArchetypeSubmission(
                bot,
                interaction,
                event,
                archetype.player_name,
                archetype.archetype_played,
                store,
                "",
            )
        status = f"Saved {len(changed)} changed opponent archetype(s)."
    else:
        status = "No opponent archetypes changed in this batch."

    if remaining_opponents:
        continuation = ConfirmEvent()
        await modal.interaction.followup.send(
            f"{status} Continue to the next batch?",
            view=continuation,
            ephemeral=True,
        )
        await continuation.wait()

        if continuation.action == ViewButtonEnum.Cancel.value:
            return None
        if continuation.action != ViewButtonEnum.Continue.value:
            raise KnownError("Opponent archetype batch continuation timed out.")
        if continuation.interaction is None:
            raise KnownError("Opponent archetype continuation was not received.")

        return await SubmitOpponentArchetypeBatch(
            bot,
            interaction,
            continuation.interaction,
            event,
            remaining_opponents,
            store,
        )

    await modal.interaction.followup.send(status, ephemeral=True)
    return modal.interaction
