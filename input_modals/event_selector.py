import discord

from custom_errors import KnownError
from data.data_input_menus import GetPreviousEvents
from tuple_conversions import Event, Format, Game, Store

class EventSelector(discord.ui.Modal, title='Select Event'):
  def __init__(self):
    super().__init__()

  @classmethod
  async def create(
    cls,
    store:Store,
    game:Game,
    format:Format,
    event_type: int = 0,
  ):
    modal = cls()
    modal.previous_events = await GetPreviousEvents(
      store, game, format, event_type=event_type, archetypes=True
    )

    if len(modal.previous_events) == 0:
      raise KnownError('No events submitted in the last 2 weeks.')
    
    past_events = []
    for i in range(len(modal.previous_events)):
      option = modal.previous_events[i]
      label = f"{option.event_date.strftime('%m/%d')} - {option.event_name}"
      value = str(option.id)
      if i == 0:
        past_events.append(discord.SelectOption(label=label, value=value, default=True))
      else:
        past_events.append(discord.SelectOption(label=label, value=value))

    modal.selected_event = discord.ui.Label(
      text="Select an Event",
      component=discord.ui.Select(
        placeholder="Select an event",
        required=True,
        options=past_events,
        max_values=1,
        min_values=1
      )
    )
    modal.add_item(modal.selected_event)
    return modal

  async def on_submit(self, interaction: discord.Interaction):
    self.event = GetEvent(self.selected_event.component.values[0], self.previous_events)
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

def GetEvent(event_id:int, previous_events:list[Event]) -> Event:
  for event in previous_events:
    if event.id == int(event_id):
      return event

  raise Exception('No event found?')