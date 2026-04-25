from services.input_services import ConvertInput
import discord
from tuple_conversions import Event, Game, Format, Store
from discord import ui, Interaction
from data.data_input_menus import GetPreviousEvents
from data.player_name_data import GetUserArchetypes, GetUserName
from discord.ext import commands
from services.submit_archetype_service import SubmitArchetype

class SubmitArchetypeModal(discord.ui.Modal, title='Submit Archetype'):
  def __init__(
    self,
    bot: commands.Bot,
    game: Game,
    format: Format,
    userId: int,
    events: list[Event],
    player_name: str,
    prev_archetypes: list[str]
  ):
    super().__init__()
    self.bot = bot
    self.game = game
    self.format = format

    self.previous_events = events
    past_events:list[discord.SelectOption] = []
    for i in range(len(events)):
      option = events[i]
      label = f"{option.event_date.strftime('%m/%d')} - {option.event_name}"
      value = str(option.id)
      if i == 0:
        past_events.append(discord.SelectOption(label=label, value=value, default=True))
      else:
        past_events.append(discord.SelectOption(label=label, value=value))

    archetype_options = [discord.SelectOption(label=archetype, value=archetype) for archetype in prev_archetypes] if len(prev_archetypes) > 0 else [discord.SelectOption(label="Please enter an archetype", value="0")]
    
    self.event_select = ui.Label(
        text="Event",
        component=ui.Select(
          options=past_events,
          required=True
        )
    )
    self.add_item(self.event_select)
  
    self.player_name_input = ui.Label(
      text="Player Name",
      component=ui.TextInput(
        placeholder="Player name",
        default=player_name if player_name else '',
        required=True
      )
    )
    self.add_item(self.player_name_input)
  
    self.archetype_select = ui.Label(
      text="Choose An Archetype",
      component=ui.Select(
        required=False,
        options=archetype_options,
        max_values=1        
      )
    )
    self.add_item(self.archetype_select)
    
    self.new_archetype = ui.Label(
      text="Or...",
      component=ui.TextInput(
        placeholder="Enter A New Archetype",
        required=False
      )
    )
    self.add_item(self.new_archetype)

  # handling the submission
  async def on_submit(self, interaction: Interaction) -> None:
    submitted_archetype:str = DetermineArchetype(self)
    submitted_event:Event = GetEvent(self.previous_events, self.event_select.component.values[0])
    submitted_player_name:str = ConvertInput(self.player_name_input.component.value)
    await interaction.response.defer(thinking=False)
    await SubmitArchetype(self.bot,
                          interaction,
                          submitted_player_name,
                          submitted_event,
                          submitted_archetype,
                          self.game,
                          self.format)

  async def on_error(self, interaction: Interaction, error: Exception) -> None:
    await interaction.followup.send(f'Oops! Something went wrong: {error}', ephemeral=True)
    self.is_submitted = False

  async def on_timeout(self) -> None:
    self.is_submitted = False

def DetermineArchetype(self) -> str:
  archetype = ''
  if not self.archetype_select.component.values:
    archetype = self.new_archetype.component.value
  elif self.archetype_select.component.values[0] == '0':
    archetype = self.new_archetype.component.value
  else:
    archetype = self.archetype_select.component.values[0]

  archetype = ConvertInput(archetype)
  return archetype

def GetEvent(
  past_events:list[Event],
  event_id:str
) -> Event:
  for event in past_events:
    if event.id == int(event_id):
      return event
  raise Exception('No event found?')
  