from custom_errors import KnownError
from discord_messages import MessageChannel
from discord import Interaction
from discord.ext import commands
from collections.abc import Callable
from input_modals.submit_event_modal import SubmitEventModal
from tuple_conversions import Format, Game, Store, Event, ViewButtonEnum
from views.confirm_event import ConfirmEvent

# Name update: SelectOrCreateEvent
async def EventForData(
    bot: commands.Bot,
    interaction: Interaction,
    store: Store,
    game: Game,
    format: Format,
    modal_factory: Callable[[Event, int], object] | None = None,
) -> tuple[Event | None, int | None, Interaction | None, bool, object | None]:
    modal = SubmitEventModal(store, game, format)
    await interaction.response.send_modal(modal)
    await modal.wait()
    
    selected_event = modal.submitted_event
    data_submission_type = modal.data_submission_type
    if not selected_event or not data_submission_type:
        raise Exception("No event or input type selected")

    input_type = data_submission_type

    #TODO: This could instead be a property of modal 
    if input_type == 1:
        input_name = "Manual"
    elif input_type == 2:
        input_name = "CSV"
    else:
        input_name = "Melee"

    if selected_event.event_type_id == 1:
        event_type_name = "Weekly"
    elif selected_event.event_type_id == 2:
        event_type_name = "Tournament"
    else:
        event_type_name = "League"

    event_output = f"""```
Event Name: {selected_event.event_name}
Event Date: {selected_event.event_date.strftime("%m/%d/%Y")}
Event Type: {event_type_name}
Data Submission Type: {input_name}```"""

    next_modal = modal_factory(selected_event, input_type) if modal_factory else None
    view = ConfirmEvent(next_modal=next_modal)
    await interaction.followup.send(
        f"{event_output}\nIs this correct?", view=view, ephemeral=True
    )
    await view.wait()

    if view.action == ViewButtonEnum.Cancel.value:
        return None, None, None, False, None

    is_created = selected_event.id == 0
    return selected_event, input_type, view.interaction, is_created, next_modal
