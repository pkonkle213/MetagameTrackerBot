from services.input_services import ConvertInput
import discord
from tuple_conversions import Event, Game, Format, Store
from discord import ui, Interaction
from data.data_input_menus import GetPreviousEvents
from data.player_name_data import GetUserArchetypes, GetUserName

LORCANA_INKS = [
  discord.SelectOption(label="Amber", value="Amber"),
  discord.SelectOption(label="Amethyst", value="Amethyst"),
  discord.SelectOption(label="Emerald", value="Emerald"),
  discord.SelectOption(label="Ruby", value="Ruby"),
  discord.SelectOption(label="Sapphire", value="Sapphire"),
  discord.SelectOption(label="Steel", value="Steel")
]

MAGIC_MANA = [
  discord.SelectOption(label="White", value="White"),
  discord.SelectOption(label="Blue", value="Blue"),
  discord.SelectOption(label="Black", value="Black"),
  discord.SelectOption(label="Red", value="Red"),
  discord.SelectOption(label="Green", value="Green")
]

class SubmitArchetypeModal(discord.ui.Modal, title='Submit Archetype'):
  is_submitted = False

  def __init__(self, store:Store, game: Game, format: Format, userId: int) -> None:
    super().__init__()
    self.game = game
    self.format = format

    self.player_name = GetUserName(store, userId)
    
    self.previous_events:list[Event] = GetPreviousEvents(store, game, format, archetypes=True)
    past_events:list[discord.SelectOption] = []
    for i in range(len(self.previous_events)):
      option = self.previous_events[i]
      label = f"{option.event_date.strftime('%m/%d')} - {option.event_name}"
      value = str(option.id)
      if i == 0:
        past_events.append(discord.SelectOption(label=label, value=value, default=True))
      else:
        past_events.append(discord.SelectOption(label=label, value=value))

    self.archetypes = GetUserArchetypes(store, userId, game, format)
    archetype_options = [discord.SelectOption(label=archetype, value=archetype) for archetype in self.archetypes] if self.archetypes else [discord.SelectOption(label="Please enter an archetype", value="0")]
    
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
        default=self.player_name if self.player_name else '',
        required=True
      )
    )
    self.add_item(self.player_name_input)
  
    if self.game.game_name.upper() == 'LORCANA':
      self.inks = ui.Label(
        text="Deck Inks",
        component=ui.Select(
          placeholder="Choose up to two inks...",
          required=True,
          options=LORCANA_INKS,
          max_values=2,
          min_values=1
        )
      )
      self.add_item(self.inks)
    
    if IsMagicLimited(self.game, self.format):
      self.main_colors = ui.Label(
        text="Main Colors",
        component=ui.Select(
          placeholder="Choose up to five colors...",
          required=True,
          options=MAGIC_MANA,
          max_values=5,
          min_values=1)
      )
      self.add_item(self.main_colors)

      self.splash_colors = ui.Label(
        text="Splash Colors",
        component=ui.Select(
          placeholder="Choose up to five colors...",
          required=False,
          options=MAGIC_MANA,
          max_values=5)
      )
      self.add_item(self.splash_colors)
    else:
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
    if self.game.game_name.upper() == 'LORCANA':
      self.submitted_inks = self.inks.component.values
    if IsMagicLimited(self.game, self.format):
      self.submitted_main_colors = self.main_colors.component.values
      self.submitted_splash_colors = self.splash_colors.component.values
    else:
      self.submitted_archetype:str = DetermineArchetype(self)

    self.submitted_event:Event = GetEvent(self.previous_events, self.event_select.component.values[0])
    self.submitted_player_name:str = ConvertInput(self.player_name_input.component.value)
    self.is_submitted:bool = True
    await interaction.response.defer(thinking=False)

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

def IsMagicLimited(
  game: Game,
  format:Format
) -> bool:
  return game.game_name.upper() == 'MAGIC' and format and format.is_limited