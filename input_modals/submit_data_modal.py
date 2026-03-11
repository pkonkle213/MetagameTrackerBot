from datetime import date
from typing import NamedTuple
from custom_errors import KnownError
from services.date_functions import ConvertToDate, GetToday
import discord
from data.data_input_menus import GetPreviousEvents, GetEventTypes
from tuple_conversions import Event, Format, Game, Store

class PredictEvent(NamedTuple):
  ID: int
  Date: date
  Name: str
  TypeID: int
  Data: str | None

class SubmitDataModal(discord.ui.Modal, title='Submit Data'):
  is_submitted = False

  def __init__(self, store:Store, game:Game, format:Format, data:bool = True):
    super().__init__()
    today = GetToday().strftime('%m/%d/%Y')
    self.data = data
    event_types = GetEventTypes()

    default_event_name = f'{format.format_name.title()} Weekly'

    self.previous_events = GetPreviousEvents(store, game, format)
    default_id = FindDefaultEvent(self.previous_events)
    past_events = []
    for i in range(len(self.previous_events)):
      option = self.previous_events[i]
      label = f"{option.event_date.strftime('%m/%d')} - {option.event_name}"
      value = str(option.id)
      if option.id == default_id:
        past_events.append(discord.SelectOption(label=label, value=value, default=True))
      else:
        past_events.append(discord.SelectOption(label=label, value=value))

    past_events.append(discord.SelectOption(label='Create A New Event', value='0', default=True if default_id == 0 else False))
    
    list_event_types = SetEventTypes(event_types)
  
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
        max_length=50)
    )
    self.add_item(self.name_input)
  
    self.event_type = discord.ui.Label(
      text="New Event Type",
      component=discord.ui.Select(
        placeholder="What type of event",
        required=False,
        options=list_event_types,
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
    await interaction.response.defer(thinking=False)
  
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
  previous_events: list[Event], 
  date_input:str, 
  name_input:str, 
  event_type:int, 
  data_message:str
) -> PredictEvent:
  event = None
  
  if continued_event == '0':
    date = ConvertToDate(date_input)
    #TODO: Clean up name_input here to remove special characters
    event = PredictEvent(0,
                         date,
                         name_input,
                         event_type,
                         data_message)
  else:
    for prev_event in previous_events:
      if prev_event[0] == int(continued_event):
        event = PredictEvent(prev_event.id,
                             prev_event.event_date,
                             prev_event.event_name,
                             prev_event.event_type_id,
                             data_message)
  if not event:
    raise KnownError('Event not found')
  return event

def SetEventTypes(event_types) -> list[discord.SelectOption]:
  types = []
  for i in range(len(event_types)):
    if i == 0:
      types.append(discord.SelectOption(label=event_types[i][1], value=str(event_types[i][0]), default=True))
    else:
      types.append(discord.SelectOption(label=event_types[i][1], value=str(event_types[i][0])))
  
  return types
      

def FindDefaultEvent(previous_events) -> int:
  today = GetToday().strftime('%m/%d/%Y')
  for event in previous_events:
    if event.event_date.strftime('%m/%d/%Y') == today:
      return event.id
  
  return 0