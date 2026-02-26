import discord

from data.data_input_menus import GetPreviousEvents
from tuple_conversions import Event, Format, Game, Store

class EventSelector(discord.ui.Modal, title='Select Event'):
  def __init__(self, store:Store, game:Game, format:Format):
    super().__init__()
    self.previous_events = GetPreviousEvents(store, game, format, archetypes=True)

    past_events = []
    for i in range(len(self.previous_events)):
      option = self.previous_events[i]
      label = f"{option.event_date.strftime('%m/%d')} - {option.event_name}"
      value = str(option.id)
      if i == 0:
        past_events.append(discord.SelectOption(label=label, value=value, default=True))
      else:
        past_events.append(discord.SelectOption(label=label, value=value))

    self.selected_event = discord.ui.Label(
      text="Select an Event",
      component=discord.ui.Select(
        placeholder="Select an event",
        required=True,
        options=past_events,
        max_values=1,
        min_values=1
      )
    )
    self.add_item(self.selected_event)

  async def on_submit(self, interaction: discord.Interaction):
    self.event = GetEvent(self.selected_event.component.values[0], self.previous_events)
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

def GetEvent(event_id:int, previous_events:list[Event]) -> Event:
  for event in previous_events:
    if event.id == int(event_id):
      return event

  raise Exception('No event found?')