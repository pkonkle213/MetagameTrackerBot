import discord
from discord.ext import commands
from data.data_input_menus import GetEventTypes, GetPreviousEvents
from services.date_functions import ConvertToDate, GetToday
from tuple_conversions import Event, EventInput, EventType, Format, Game, Store
from custom_errors import KnownError

class SubmitEventModal(discord.ui.Modal, title='Select Event'):
    def __init__(
        self,
        bot: commands.Bot,
        store: Store,
        game: Game,
        format: Format
    ):
        super().__init__()
        today = GetToday().strftime('%m/%d/%Y')
        self.bot = bot
        self.store = store
        self.game = game
        self.format = format

        event_types = GetEventTypes(store.discord_id, game, format)
        default_type = 'League' if event_types[0].id < 0 else 'Weekly'
        default_event_name = f'{format.format_name.title()} {default_type}'

        self.previous_events = GetPreviousEvents(store, game, format)
        default_id = FindDefaultEvent(self.previous_events)
        past_events = SetPastEventsOptions(self.previous_events, default_id)
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
                max_length=10
            )
        )
        self.add_item(self.date_input)
    
        self.name_input = discord.ui.Label(
            text="New Event Name",
            component=discord.ui.TextInput(
                placeholder='Short Description of Event',
                default=default_event_name,
                required=False,
                max_length=50
            )
        )
        self.add_item(self.name_input)
    
        self.event_type = discord.ui.Label(
            text="New Event Type",
            component=discord.ui.Select(
                placeholder="What type of event",
                required=True,
                options=list_event_types,
                max_values=1,
                min_values=1
                )
        )
        self.add_item(self.event_type)

    async def on_submit(self, interaction: discord.Interaction):
        submitted_event = SetEventInfo(
            self.continue_event.component.values[0],
            self.previous_events,
            self.date_input.component.value,
            self.name_input.component.value,
            self.event_type.component.values[0] if self.event_type.component.values else None
        )

def SetEventInfo(
  continued_event_id: str,
  previous_events: list[Event],
  date_input:str, 
  name_input:str, 
  event_type:int
) -> EventInput:
  event = None
  
  if continued_event_id == '0':
    date = ConvertToDate(date_input)
    event = EventInput(
      0,
      None,
      date,
      name_input,
      event_type,
      0,
      None,
      None,
      None,
      None,
      0,
      0,
      0)
  else:
    for prev_event in previous_events:
      if prev_event[0] == int(continued_event_id):
        event = EventInput(
          prev_event.id,
          prev_event.custom_event_id,
          prev_event.event_date,
          prev_event.event_name,
          prev_event.event_type_id,
          0,
          None,
          None,
          None,
          None,
          0,
          0,
          0
        )
    if not event:
      raise KnownError('Event not found')
  return event

def SetEventTypes(event_types:list[EventType]) -> list[discord.SelectOption]:
  types:list[discord.SelectOption] = []
  for i in range(len(event_types)):
    if i == 0:
      types.append(discord.SelectOption(label=event_types[i].name, value=str(event_types[i][0]), default=True))
    else:
      types.append(discord.SelectOption(label=event_types[i].name, value=str(event_types[i][0])))
  
  return types
      

def FindDefaultEvent(previous_events: list[Event]) -> int:
  today = GetToday()
  if len(previous_events) == 0:
    return 0

  for event in previous_events:
    if event.created_at.date() == today:
      return event.id
  
  return 0

def SetPastEventsOptions(previous_events: list[Event], default_id: int) -> list[discord.SelectOption]:
  past_events: list[discord.SelectOption] = []
  for i in range(len(previous_events)):
    option = previous_events[i]
    label = f"{option.event_date.strftime('%m/%d')} - {option.event_name}"
    value = str(option.id)
    if option.id == default_id:
      past_events.append(discord.SelectOption(label=label, value=value, default=True))
    else:
      past_events.append(discord.SelectOption(label=label, value=value))

  past_events.append(discord.SelectOption(label='Create A New Event', value='0', default=True if default_id == 0 else False))
  return past_events