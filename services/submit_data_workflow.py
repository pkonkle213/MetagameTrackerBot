from discord import Interaction
from discord.ext import commands

from custom_errors import KnownError
from data.event_data import CompleteEvent
from discord_messages import MessageChannel
from input_modals.submit_csv_modal import SubmitCSVDataModal
from input_modals.submit_data_modal import SubmitManualDataModal
from input_modals.submit_melee_modal import SubmitMeleeDataModal
from services.add_results_services import AddPairingResults, AddStandingResults
from services.convert_and_save_input import BuildFilePath
from services.message_hubs_services import MessageHubs
from services.submit_data_services import BuildReviewOutput
from tuple_conversions import (
    DataInputEnum,
    DataConverted,
    Event,
    Format,
    Game,
    ReportedAsEnum,
    Store,
    ViewButtonEnum,
)
from views.confirm_data import ConfirmData


def BuildDataModal(
    input_type: int,
    event: Event,
    store: Store,
    game: Game,
    format: Format,
) -> SubmitManualDataModal | SubmitCSVDataModal | SubmitMeleeDataModal:
    match input_type:
        case DataInputEnum.Manual.value:
            save_path = BuildFilePath(store, game, format, "ManualInput.txt")
            return SubmitManualDataModal(event, save_path)
        case DataInputEnum.CSV.value:
            save_path = BuildFilePath(store, game, format, "CSVInput.txt")
            return SubmitCSVDataModal(event, save_path)
        case DataInputEnum.Melee.value:
            save_path = BuildFilePath(store, game, format, "MeleeInput.txt")
            return SubmitMeleeDataModal(store, event, save_path)
        case _:
            raise KnownError("Unknown input type")


def BuildDataReview(
    data: DataConverted,
    event: Event,
    input_type: int,
    store: Store,
    game: Game,
    format: Format,
) -> tuple[str, ConfirmData]:
    output = BuildReviewOutput(data)
    next_modal = BuildDataModal(input_type, event, store, game, format)
    view = ConfirmData(
        next_modal=next_modal,
        is_standings=bool(data.standings_data),
    )

    if data.standings_data:
        output += (
            "\n:rotating_light::rotating_light:This is standings data and will "
            "limit the data used for other commands:rotating_light::rotating_light:"
        )

    if data.pairings_data and event.reported_as == ReportedAsEnum.Standings.value:
        output += (
            "\n:rotating_light::rotating_light:This will overwrite the standings "
            "data that exists for this event:rotating_light::rotating_light:"
        )

    return output, view


async def SaveDataSubmission(
    event: Event,
    data: DataConverted,
    submitter_id: int,
) -> None:
    if data.standings_data:
        await AddStandingResults(event, data.standings_data, submitter_id)
    elif data.pairings_data:
        await AddPairingResults(event, data.pairings_data, submitter_id)


async def NotifyNewEventSubmission(
    bot: commands.Bot,
    interaction: Interaction,
    store: Store,
    event: Event,
) -> None:
    store_message = (
        f"New data for {event.event_date.strftime('%B %-d')}'s "
        f"{event.event_name} event has been submitted! Use the "
        "`/submit archetype` command to input an archetype!"
    )
    event_date = event.event_date.strftime("%B %d")
    hub_message = (
        f"New event submitted for {store.store_name}: "
        f"{event.event_name} ({event_date}). Waiting for archetypes..."
    )
    await MessageChannel(
        bot,
        store_message,
        interaction.guild_id,
        interaction.channel_id,
    )
    await MessageHubs(bot, store, event, hub_message)


async def SubmitEventDataWorkflow(
    bot: commands.Bot,
    interaction: Interaction,
    store: Store,
    game: Game,
    format: Format,
    event: Event,
    input_type: int,
    active_interaction: Interaction,
    submitter_id: int,
    is_new_event: bool,
) -> None:
    modal = None
    while True:
        if modal is None:
            modal = BuildDataModal(input_type, event, store, game, format)
            await active_interaction.response.send_modal(modal)
        modal_timed_out = await modal.wait()
        if modal_timed_out:
            await active_interaction.followup.send(
                "Data entry timed out. No data from this step was added to "
                "the event results.",
                ephemeral=True,
            )
            return

        data = modal.converted_data
        output, view = BuildDataReview(
            data, event, input_type, store, game, format
        )
        review_message = await modal.interaction.followup.send(
            f"{output}\nPlease select continue if the data is accurate",
            ephemeral=True,
            view=view,
        )
        confirmation_timed_out = await view.wait()
        if confirmation_timed_out:
            await review_message.edit(
                content=(
                    "Confirmation timed out. This submission was not added "
                    "to the event results."
                ),
                view=None,
            )
            return

        confirm_response = view.action
        active_interaction = view.interaction
        if not active_interaction:
            raise KnownError("No interaction found after confirmation")

        if confirm_response == ViewButtonEnum.Cancel.value:
            await active_interaction.response.edit_message(
                content="Data submission for this round canceled!",
                view=None,
            )
            break

        await SaveDataSubmission(event, data, submitter_id)

        if confirm_response in (
            ViewButtonEnum.DoneComplete.value,
            ViewButtonEnum.DoneIncomplete.value,
        ):
            if confirm_response == ViewButtonEnum.DoneComplete.value:
                await CompleteEvent(event.id)

            if is_new_event:
                await NotifyNewEventSubmission(bot, interaction, store, event)
            break

        modal = view.next_modal
