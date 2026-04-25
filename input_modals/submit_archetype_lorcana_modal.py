import discord
from discord.ext import commands
from tuple_conversions import Game, Format, Event, Store
from services.command_error_service import KnownError

LORCANA_INKS = [
  discord.SelectOption(label="Amber", value="Amber"),
  discord.SelectOption(label="Amethyst", value="Amethyst"),
  discord.SelectOption(label="Emerald", value="Emerald"),
  discord.SelectOption(label="Ruby", value="Ruby"),
  discord.SelectOption(label="Sapphire", value="Sapphire"),
  discord.SelectOption(label="Steel", value="Steel")
]

class LorcanaSubmitArchetypeModal(discord.ui.Modal, title='Submit Archetype'):
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

    #TODO: How do I present the player's previous archetypes?
    #Known: All lorcana archetypes are listed as INK/INK - ARCHETYPE

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

    self.archetype_name = ui.Label(
      text="Archetype Name",
      component=ui.TextInput(
        placeholder="Enter The Archetype Name",
        required=False
      )
    )
    self.add_item(self.new_archetype)

  async def on_submit(self, interaction: discord.Interaction) -> None:
    ...

  async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
    await interaction.followup.send(f'Oops! Something went wrong: {error}', ephemeral=True)
    self.is_submitted = False

  async def on_timeout(self) -> None:
    self.is_submitted = False