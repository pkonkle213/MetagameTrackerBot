import discord
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
    raise KnownError('This has yet to be fully implemented')
    self.game = game
    self.format = format
  
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
    ...

  async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
    await interaction.followup.send(f'Oops! Something went wrong: {error}', ephemeral=True)
    self.is_submitted = False

  async def on_timeout(self) -> None:
    self.is_submitted = False