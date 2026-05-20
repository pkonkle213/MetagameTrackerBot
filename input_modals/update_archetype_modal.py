from tuple_conversions import Store, Game, Format
from discord.ext import commands
from discord import ui, Interaction
from services.update_archetype_service import UpdateArchetypes


class UpdateArchetypeModal(ui.Modal, title="Update Archetypes"):
  def __init__(self, bot: commands.Bot, store: Store, game: Game, format: Format):
    super().__init__()
    self.bot = bot
    self.store = store
    self.game = game
    self.format = format

    self.old_archetype = ui.Label(
      text="Old Archetype",
      component=ui.TextInput(placeholder="Old Archetype", required=True),
    )
    self.add_item(self.old_archetype)

    self.new_archetype = ui.Label(
      text="New Archetype",
      component=ui.TextInput(placeholder="New Archetype", required=True),
    )
    self.add_item(self.new_archetype)

  async def on_submit(self, interaction: Interaction) -> None:
    count = UpdateArchetypes(
      self.store,
      self.game,
      self.format,
      self.old_archetype.component.value,
      self.new_archetype.component.value,
      interaction
    )
    await interaction.response.defer(thinking=True, ephemeral=True)
    if count < 1:
      await interaction.followup.send(
        f"No archetypes updated", ephemeral=True
      )
    else:
      await interaction.followup.send(
        f"{count} archetypes updated", ephemeral=True
      )

  async def on_error(self, interaction: Interaction, error: Exception) -> None:
    await interaction.followup.send(
      f"Oops! Something went wrong: {error}", ephemeral=True
    )
