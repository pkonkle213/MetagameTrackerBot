import discord
from data.data_input_menus import GetEventTypes, GetPreviousEvents
from services.date_functions import ConvertToDate, GetToday
from tuple_conversions import Event, EventType, Format, Game, Store, DataInputEnum

class SubmitEventModal(discord.ui.Modal, title='Select Event'):
  def __init__(
    self,
    store: Store,
    game: Game,
    format: Format
  ):
    super().__init__()
    self.submitted_event: Event | None = None
    self.data_submission_type = None
    today = GetToday().strftime('%m/%d/%Y')
    self.store = store
    self.game = game
    self.format = format

    event_types = GetEventTypes(store.discord_id, game, format)
    if event_types[0].id < 0:
      default_type = 'League'
      num_events = f' - Week {event_types[0].num_events + 1}'
    else:
      default_type = 'Weekly'
      num_events = ''
    
    default_event_name = f'{format.format_name.title()} {default_type}' + num_events

    self.previous_events = GetPreviousEvents(store, game, format)
    default_id = FindDefaultEvent(self.previous_events)
    past_events = SetPastEventsOptions(self.previous_events, default_id)
    list_event_types = SetEventTypes(event_types)

    #TODO: Select the default way to submit data based on the game
    self.data_types:list[discord.SelectOption] = [discord.SelectOption(label=type.name, value=str(type.value)) for type in DataInputEnum]

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

    self.data_input = discord.ui.Label(
      text='How will data be submitted?',
      component=discord.ui.Select(
        placeholder='Select a method',
        min_values=1,
        max_values=1,
        required=True,
        options=self.data_types
      )
    )
    self.add_item(self.data_input)

  async def on_submit(self, interaction:discord.Interaction):
    #TODO: Add a view to double check that this is correct (also enabling the next modal)
    self.submitted_event = SetEventInfo(
      int(self.continue_event.component.values[0]),
      self.previous_events,
      self.date_input.component.value,
      self.name_input.component.value,
      self.event_type.component.values[0] if self.event_type.component.values else None,
      self.store,
      self.game,
      self.format
    )
    self.data_submission_type = int(self.data_input.component.values[0])
    await interaction.response.defer(thinking=False, ephemeral=True)

def SetEventInfo(
  continued_event_id: int,
  previous_events: list[Event],
  date_input:str, 
  name_input:str, 
  event_type:int,
  store:Store,
  game:Game,
  format:Format,
) -> Event:
  if continued_event_id == 0:
    date = ConvertToDate(date_input)
    return Event(
      0,
      None,
      None,
      store.discord_id,
      date,
      game.id,
      format.id,
      0,
      event_type,
      name_input,
      0,
      0,
      None,
      False
    )
  else:
    for prev_event in previous_events:
      if prev_event[0] == continued_event_id:
        return prev_event
  raise Exception('Cannot find matching event nor create a new one')

def SetEventTypes(event_types:list[EventType]) -> list[discord.SelectOption]:
  types:list[discord.SelectOption] = []
  for i in range(len(event_types)):
    if i == 0:
      types.append(discord.SelectOption(label=event_types[i].name, value=str(event_types[i].id), default=True))
    else:
      types.append(discord.SelectOption(label=event_types[i].name, value=str(event_types[i].id)))
  
  return types
      
def FindDefaultEvent(previous_events: list[Event]) -> int:
  today = GetToday()
  if len(previous_events) == 0:
    return 0

  for event in previous_events:
    if event.created_at and event.created_at.date() == today:
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