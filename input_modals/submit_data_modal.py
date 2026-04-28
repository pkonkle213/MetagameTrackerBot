import discord
from datetime import date
from custom_errors import KnownError
from services.date_functions import ConvertToDate, GetToday
from discord.ext import commands
from data.data_input_menus import GetPreviousEvents, GetEventTypes
from tuple_conversions import Event, Format, Game, Store, EventInput, DataConverted
from services.convert_and_save_input import ConvertData
from services.add_results_services import SubmitData
from discord_messages import MessageChannel
from services.message_hubs_services import MessageHubs
import settings

class ConfirmStandings(discord.ui.View):
  def __init__(self, data:EventInput):
    super().__init__(timeout=60)
    self.is_submitted = False
    self.data = data

  @discord.ui.button(label="Confirm & Submit", style=discord.ButtonStyle.success)
  async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
    await interaction.response.edit_message(content="Submitting data...", view=None)
    for child in self.children: child.disabled = True
    self.stop()
  

class SubmitDataModal(discord.ui.Modal, title='Submit Data'):
  def __init__(
    self,
    bot: commands.Bot,
    store:Store,
    game:Game,
    format:Format,
    data:bool,
    csv_file:discord.Attachment | None,
    melee_tournament_id:str
  ):
    super().__init__()
    today = GetToday().strftime('%m/%d/%Y')
    self.bot = bot
    self.data = data
    self.store = store
    self.game = game
    self.format = format
    self.csv_file = csv_file
    self.melee_tournament_id = melee_tournament_id
    
    event_types = GetEventTypes(store.discord_id)

    default_event_name = f'{format.format_name.title()} Weekly'

    #TODO: Could this be cleaned up a little bit?
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
    submitted_event = SetEventInfo(
      self.continue_event.component.values[0],
      self.previous_events,
      self.date_input.component.value,
      self.name_input.component.value,
      self.event_type.component.values[0] if self.event_type.component.values else None
    )
    
    data_input = await ConvertData(
      submitted_event,
      self.message_input.component.value, 
      self.csv_file,
      self.melee_tournament_id,
      self.store,
      self.game,
      self.format
    )

    event_input = EventInput(
      submitted_event.id,
      submitted_event.custom_event_id,
      submitted_event.event_date,
      submitted_event.event_name,
      submitted_event.event_type_id,
      data_input.round_number if data_input.round_number else 0,
      data_input.pairings_data,
      data_input.standings_data,
      data_input.archetypes,
      data_input.errors,
      self.store.discord_id,
      self.game.id,
      self.format.id
    )

    if data_input.standings_data and len(data_input.standings_data) > 0:
      view = ConfirmStandings(event_input)
      await interaction.response.send_message(
        content="This is standings data, which does not contribute to matchups. Please confirm you want to submit this data.",
        view=view,
        ephemeral=True
      )
      await view.wait()
    else:
      await interaction.response.defer(thinking=False)

    output, event = SubmitData(event_input, interaction.user.id)
    
    if not output:
      raise KnownError("Unable to submit data. Please try again later.")

    await interaction.followup.send(output, ephemeral=True)
    
    if event:
      await MessageChannel(
        self.bot,
        f"New data for {event.event_date.strftime('%B %-d')}'s {event.event_name} event has been submitted! Use the `/submit archetype` command to input your archetype!",
        interaction.guild_id,
        interaction.channel_id
      )
      try:
        await MessageHubs(self.bot, self.store, event)
      except Exception as e:
        await MessageChannel(self.bot, f"Issue messaging hubs: {e}", settings.BOTGUILDID, settings.ERRORCHANNELID)
    
  
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
      0,
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
          0,
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

def SetPastEventsOptions(previous_events, default_id) -> list[discord.SelectOption]:
  past_events = []
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