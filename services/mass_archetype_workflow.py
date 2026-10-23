from discord import Interaction

from custom_errors import KnownError
from data.archetype_data import BulkAddArchetypes
from data.event_data import GetPlayersInEvent
from input_modals.event_selector import EventSelector
from input_modals.mass_archetype_modal import MassArchetypeSubmit
from output_builder import BuildTableOutput
from tuple_conversions import (
    Event,
    Format,
    Game,
    PlayerArchetype,
    Store,
    ViewButtonEnum,
)
from views.confirm_event import ConfirmEvent


async def SubmitMassArchetypes(
    interaction: Interaction,
    store: Store,
    game: Game,
    format: Format,
) -> None:
    """Coordinate selecting an event, reviewing player batches, and saving them."""
    event, active_interaction = await SelectMassArchetypeEvent(
        interaction, store, game, format
    )
    if event is None:
        await interaction.followup.send("Canceled!", ephemeral=True)
        return

    players = await GetPlayersInEvent(event.id)
    if not players:
        raise KnownError("No players found for this event.")

    for start in range(0, len(players), 5):
        batch = players[start : start + 5]
        active_interaction = await SubmitArchetypeBatch(
            interaction, active_interaction, event, batch
        )
        if active_interaction is None:
            await interaction.followup.send("Canceled!", ephemeral=True)
            return

    await interaction.followup.send(
        "All archetypes have been submitted!", ephemeral=True
    )


async def SelectMassArchetypeEvent(
    interaction: Interaction, store: Store, game: Game, format: Format
) -> tuple[Event | None, Interaction | None]:
    selector = await EventSelector.create(store, game, format)
    await interaction.response.send_modal(selector)
    await selector.wait()

    if not selector.is_submitted:
        raise KnownError("Event selection was not submitted.")

    event = selector.event
    if event is None:
        raise KnownError("No event found.")

    confirmation = ConfirmEvent()
    await interaction.followup.send(
        f"You selected {event.event_date.strftime('%m/%d')} - "
        f"{event.event_name}. Is this correct?",
        view=confirmation,
        ephemeral=True,
    )
    await confirmation.wait()

    if confirmation.action == ViewButtonEnum.Cancel.value:
        return None, None
    if confirmation.action != ViewButtonEnum.Continue.value:
        raise KnownError("Event selection confirmation timed out.")
    if confirmation.interaction is None:
        raise KnownError("Event selection confirmation was not received.")

    return event, confirmation.interaction


async def SubmitArchetypeBatch(
    interaction: Interaction,
    active_interaction: Interaction,
    event: Event,
    players: list[PlayerArchetype],
) -> Interaction | None:
    modal = MassArchetypeSubmit(players)
    await active_interaction.response.send_modal(modal)
    await modal.wait()

    if not modal.is_submitted or modal.interaction is None:
        raise KnownError("Archetype batch was not submitted.")

    output = BuildTableOutput(
        "Please confirm the new archetypes:",
        ["Name", "Archetype"],
        modal.new_archetypes,
    )
    confirmation = ConfirmEvent()
    for message in output:
        await interaction.followup.send(message)
    await interaction.followup.send(
        "Are these correct?", view=confirmation, ephemeral=True
    )
    await confirmation.wait()

    if confirmation.action == ViewButtonEnum.Cancel.value:
        return None
    if confirmation.action != ViewButtonEnum.Continue.value:
        raise KnownError("Archetype batch confirmation timed out.")
    if confirmation.interaction is None:
        raise KnownError("Archetype batch confirmation was not received.")

    await BulkAddArchetypes(
        event,
        modal.new_archetypes,
        interaction.user.id,
        interaction.user.name,
        interaction.guild_id,
        interaction.guild.name if interaction.guild else "",
    )
    return confirmation.interaction
