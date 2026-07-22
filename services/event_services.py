from discord import Interaction
from discord.ext import commands
from input_modals.submit_event_modal import SubmitEventModal
from tuple_conversions import Format, Game, Store, Event


async def GetEvent(bot:commands.Bot, interaction:Interaction, store:Store, game:Game, format:Format) -> Event:
    # This should present a modal similar to what is now the data modal (but not the data)
    # 1) Continue dropdown
    # 2) New Event Date - default to today
    # 3) New Event Name - default to '{format.name} {event_type.name}'
    # 4) New Event Type - default to league if there's an active league and store is_paid, otherwise default to weekly
    # 5) How data will be coming in.
    #       CSV - default if lorcana, riftbound
    #       Melee - default if star wars unlimited
    #       Text - default if magic

    # It needs to figure out if the event for the data is new or a continuation of a previous event
    modal = SubmitEventModal(store, game, format)
    await interaction.response.send_modal(modal)
    try:
        await modal.wait()
    except:
        raise Exception('Unable to find the event')

    selected_event = modal.submitted_event

    print('selected event:', selected_event)
    # If new, create it

    ...