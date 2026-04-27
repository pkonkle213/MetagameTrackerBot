from services.submit_archetype_service import SubmitArchetype
import discord
from discord import ui
from discord.ext import commands
from tuple_conversions import Game, Format, Event, Store
from services.command_error_service import KnownError

MAGIC_MANA = [
  discord.SelectOption(label="White", value="White"),
  discord.SelectOption(label="Blue", value="Blue"),
  discord.SelectOption(label="Black", value="Black"),
  discord.SelectOption(label="Red", value="Red"),
  discord.SelectOption(label="Green", value="Green")
]

class MagicLimitedSubmitArchetypeModal(discord.ui.Modal, title='Submit Archetype'):
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

  async def on_submit(self, interaction: discord.Interaction) -> None:
    submitted_player_name = self.player_name_input.component.value
    submitted_event:Event = GetEvent(self.previous_events, self.event_select.component.values[0])
    submitted_archetype = BuildArchetype(self.main_colors.component.values, self.splash_colors.component.values)
    await interaction.response.defer(thinking=False)
    await SubmitArchetype(self.bot,
      interaction,
      submitted_player_name,
      submitted_event,
      submitted_archetype,
      self.game,
      self.format)

  async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
    await interaction.followup.send(f'Oops! Something went wrong: {error}', ephemeral=True)
    self.is_submitted = False

  async def on_timeout(self) -> None:
    self.is_submitted = False

def BuildArchetype(drafted_colors:list[str], splashed_colors:list[str]) -> str:
  colors = ""
  for color in drafted_colors:
    colors += ConvertMagicColor(color)

  if len(splashed_colors) == 0:
    return colors

  for color in splashed_colors:
    letter = ConvertMagicColor(color)
    if letter in colors:
      raise KnownError('You cannot splash a color you drafted. Please try again.')
    colors += letter.lower()

  if len(colors) > 5:
    raise KnownError('Too many colors selected, please try again.')

  return colors

def ConvertMagicColor(color:str) -> str:
  match color:
   case 'White':
     return 'W'
   case 'Blue':
     return 'U'
   case 'Black':
     return 'B'
   case 'Red':
     return 'R'
   case 'Green':
     return 'G'
   case _:
     raise KnownError('Color not recognized. Please try again.')

def GetEvent(
  past_events:list[Event],
  event_id:str
) -> Event:
  for event in past_events:
    if event.id == int(event_id):
      return event
  raise Exception('No event found?')
