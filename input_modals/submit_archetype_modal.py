import discord
from tuple_conversions import Game, Format
from discord import ui, Interaction
from services.date_functions import GetToday

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

#TODO: If the game is Magic/Limited, archetype is not needed and colors should be selectable
class SubmitArchetypeModal(discord.ui.Modal, title='Submit Archetype'):
  def __init__(self, game: Game, format: Format) -> None:
    super().__init__()
    self.game = game
    self.format = format
    self.today = GetToday().strftime('%m/%d/%Y')
    
    self.date = ui.Label(
        text="Event Date",
        component=ui.TextInput(
          placeholder='MM/DD/YYYY',
          default=self.today,
          required=True
        )
    )
    self.add_item(self.date)
  
    self.player_name = ui.Label(
      text="Player Name",
      component=ui.TextInput(
        placeholder="Player name",
        required=True
      )
    )
    self.add_item(self.player_name)
  
    if self.game.Name.upper() == 'LORCANA':
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
      self.archetype = ui.Label(
        text="Archetype",
        component=ui.TextInput(
          placeholder="Archetype played",
          required=True
        )
      )
      self.add_item(self.archetype)

  # handling the submission
  async def on_submit(self, interaction: Interaction) -> None:
    if self.game.Name.upper() == 'LORCANA':
      self.submitted_inks = self.inks.component.values
    if IsMagicLimited(self):
      self.submitted_main_colors = self.main_colors.component.values
      self.submitted_splash_colors = self.splash_colors.component.values
    else:
      self.submitted_archetype = self.archetype.component.value
    self.submitted_date = self.date.component.value
    self.submitted_player_name = self.player_name.component.value
    await interaction.response.defer()

  async def on_error(self, interaction: Interaction, error: Exception) -> None:
    await interaction.followup.send(f'Oops! Something went wrong: {error}', ephemeral=True)
    self.is_submitted = False

  async def on_timeout(self) -> None:
    self.is_submitted = False

def IsMagicLimited(self) -> bool:
  return self.game.Name.upper() == 'MAGIC' and self.game.HasFormats and self.format and self.format.IsLimited