from discord_messages import MessageChannel
from discord import Interaction
from discord.ext import commands
from input_modals.submit_event_modal import SubmitEventModal
from tuple_conversions import Format, Game, Store, Event, ViewButtonEnum
from data.event_data import CreateEvent, GetEvent
from views.confirm_event import ConfirmEvent

async def EventForData(
  bot:commands.Bot,
  interaction:Interaction,
  store:Store,
  game:Game,
  format:Format
) -> tuple[Event | None, int | None, Interaction | None, bool]:
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
    
  input_type = data_submission_type

  view = ConfirmEvent()

  #TODO: This should probably loop through the enum so they're not magical strings
  if input_type == 1:
    input_name = 'Manual'
  elif input_type == 2:
    input_name = 'CSV'
  else:
    input_name = 'Melee'

  #TODO: This should probably loop through the enum so they're not magical strings
  if selected_event.event_type_id == 1:
    event_type_name = 'Weekly'
  elif selected_event.event_type_id == 2:
    event_type_name = 'Tournament'
  else:
    event_type_name = 'League'
    
  event_output = f'''```
Event Name: {selected_event.event_name}
Event Date: {selected_event.event_date.strftime('%m/%d/%Y')}
Event Type: {event_type_name}
Data Submission Type: {input_name}```'''
  await interaction.followup.send(f'{event_output}\nIs this correct?', view=view, ephemeral=True)
  await view.wait()

  if view.action == ViewButtonEnum.Cancel.value:
    return None, None, None

  is_created = False
  if selected_event.id == 0:
    event_id = CreateEvent(selected_event, interaction.user.id)
    event = GetEvent(event_id)
    is_created = True
  else:
    event = selected_event

  return event, input_type, view.interaction, is_created