from discord import Interaction
from discord.ext import commands
from input_modals.submit_event_modal import SubmitEventModal
from tuple_conversions import Format, Game, Store, Event
from data.event_data import CreateEvent

async def GetEvent(bot:commands.Bot, interaction:Interaction, store:Store, game:Game, format:Format) -> tuple[int, int]:
  modal = SubmitEventModal(store, game, format)
  await interaction.response.send_modal(modal)
  try:
    await modal.wait()
  except:
    raise Exception('Unable to find the event')

  selected_event = modal.submitted_event
  data_submission_type = modal.data_submission_type
  if not selected_event or not data_submission_type:
    raise Exception('No event or input type selected')
    
  event_id = selected_event.id
  input_type = data_submission_type

  print('selected event:', selected_event)
  if event_id == 0:
    event_id = CreateEvent(selected_event, interaction.user.id)

  print('New event submitted:', event_id)
  return event_id, input_type