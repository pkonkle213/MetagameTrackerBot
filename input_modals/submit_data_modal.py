from typing import NamedTuple
from custom_errors import KnownError
from services.date_functions import GetToday
import discord
from data.data_input_menus import GetPreviousEvents, GetEventTypes
from tuple_conversions import Format, Game, Store

class PredictEvent(NamedTuple):
  ID: int
  Date: str
  Name: str
  TypeID: int
  Data: str | None

class SubmitDataModal(discord.ui.Modal, title='Submit Data'):
  is_submitted = False

  def __init__(self, store:Store, game:Game, format:Format, data:bool = True):
    super().__init__()
    today = GetToday().strftime('%m/%d/%Y')
    self.previous_events = GetPreviousEvents(store, game, format)
    self.data = data
    event_types = GetEventTypes()
      
    default_event_name = f'{format.FormatName}'
  
    past_events = []
    for i in range(len(self.previous_events)):
      option = self.previous_events[i]
      label = f"{option[1]} - {option[2]}"
      if i == 0:
        past_events.append(discord.SelectOption(label=label, value=option[0], default=True))
      else:
        past_events.append(discord.SelectOption(label=label, value=option[0]))
    past_events.append(discord.SelectOption(label='Create A New Event', value='0'))
    
    event_types = [
      discord.SelectOption(label=type[1], value=type[0]) for type in event_types
    ]
  
    self.continue_event = discord.ui.Label(
      text="Continue?",
      component=discord.ui.Select(
        placeholder="Is this a continuation of an event?",
        required=True,
        options=past_events,
        max_values=1,
        min_values=1
      )
    )
    self.add_item(self.continue_event)
  
    self.date_input = discord.ui.Label(
      text="New Event Date",
      component=discord.ui.TextInput(
        placeholder='MM/DD/YYYY',
        default=today,
        required=False,
        max_length=10)
    )
    self.add_item(self.date_input)
  
    self.name_input = discord.ui.Label(
      text="New Event Name",
      component=discord.ui.TextInput(
        placeholder='Short Description of Event',
        default=default_event_name,
        required=False,
        max_length=20)
    )
    self.add_item(self.name_input)
  
    self.event_type = discord.ui.Label(
      text="New Event Type",
      component=discord.ui.Select(
        placeholder="What type of event",
        required=False,
        options=event_types,
        max_values=1,
        min_values=1)
    )
    self.add_item(self.event_type)

    if data:
      self.message_input = discord.ui.Label(
        text="Event Data",
        component=discord.ui.TextInput(
          style=discord.TextStyle.paragraph,
          placeholder='Paste your data here',
          required=True,
          max_length=2000  # Max length for text input
        ))
      self.add_item(self.message_input)

  async def on_submit(self, interaction: discord.Interaction):
    self.submitted_event = SetEventDateAndName(
      self.continue_event.component.values[0],
      self.previous_events,
      self.date_input.component.value,
      self.name_input.component.value,
      self.event_type.component.values[0] if self.event_type.component.values else None,
      self.message_input.component.value if self.data else None
    )
    self.is_submitted = True
    await interaction.response.defer()
  
  async def on_error(
    self,
    interaction: discord.Interaction,
    error: Exception
  ) -> None:
    await interaction.followup.send(f'Oops! Something went wrong: {error}',
                    ephemeral=True)
    self.is_submitted = False

  async def on_timeout(self) -> None:
    self.is_submitted = False

def SetEventDateAndName(
  continued_event,
  previous_events, 
  date_input, 
  name_input, 
  event_type, 
  data_message
) -> PredictEvent:
  event = None
  
  if continued_event == '0':
    event = PredictEvent(0,
                         date_input,
                         name_input,
                         event_type,
                         data_message)
  else:
    for prev_event in previous_events:
      if prev_event[0] == int(continued_event):
        event = PredictEvent(prev_event[0],
                             prev_event[1],
                             prev_event[2],
                             event_type,
                             data_message)
  if not event:
    raise KnownError('Event not found')
  return event