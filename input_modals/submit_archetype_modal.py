from typing import Tuple
import discord
from tuple_conversions import Event, Game, Format, Store
from discord import ui, Interaction
from services.date_functions import GetToday
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
    archetype_options = []
    for i in range(len(self.archetypes)):
      option = self.archetypes[i]
      if i == 0:
        archetype_options.append(discord.SelectOption(label=option, value=option, default=True))
      else:
        archetype_options.append(discord.SelectOption(label=option, value=option))
    archetype_options.append(discord.SelectOption(label='New Archetype', value='0'))
    
    self.event_select = ui.Label(
        text="Event",
        component=ui.Select(
          options=past_events,
          required=True
        )
    )
    self.add_item(self.event_select)
  
    self.player_name = ui.Label(
      text="Player Name",
      component=ui.TextInput(
        placeholder="Player name",
        default=self.player_name,
        required=True
      )
    )
    self.add_item(self.player_name)
  
    if self.game.GameName.upper() == 'LORCANA':
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
    
    if IsMagicLimited(self):
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
          placeholder="Enter A New One",
          required=False
        )
      )
      self.add_item(self.new_archetype)

  # handling the submission
  async def on_submit(self, interaction: Interaction) -> None:
    if self.game.GameName.upper() == 'LORCANA':
      self.submitted_inks = self.inks.component.values
    if IsMagicLimited(self):
      self.submitted_main_colors = self.main_colors.component.values
      self.submitted_splash_colors = self.splash_colors.component.values
    else:
      self.submitted_archetype:str = DetermineArchetype(self)

    self.submitted_event:Event = GetEvent(self.previous_events, self.event_select.component.values[0])
    self.submitted_player_name:str = self.player_name.component.value
    self.is_submitted:bool = True
    await interaction.response.defer()

  async def on_error(self, interaction: Interaction, error: Exception) -> None:
    await interaction.followup.send(f'Oops! Something went wrong: {error}', ephemeral=True)
    self.is_submitted = False

  async def on_timeout(self) -> None:
    self.is_submitted = False

def DetermineArchetype(self) -> str:
  print("Archetype_select values:", self.archetype_select.component.values)
  print("New archetype value:", self.new_archetype.component.value)

  archetype = ''
  if not self.archetype_select.component.values:
    archetype = self.new_archetype.component.value
  elif self.archetype_select.component.values[0] == '0':
    archetype = self.new_archetype.component.value
  else:
    archetype = self.archetype_select.component.values[0]

  print('Archetype selected:', archetype)
  return archetype

def GetEvent(
  past_events:list[Event],
  event_id:str
) -> Event:
  for event in past_events:
    if event.id == int(event_id):
      print('Event selected:', event)
      return event
  raise Exception('No event found?')

def IsMagicLimited(self) -> bool:
  return self.game.GameName.upper() == 'MAGIC' and self.format and self.format.IsLimited