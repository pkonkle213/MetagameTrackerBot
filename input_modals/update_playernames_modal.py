from tuple_conversions import Store
from discord import ui, Interaction
from data.update_player_names_data import UpdatePlayerNames
from services.input_services import ConvertInput

class UpdatePlayerNamesModal(ui.Modal, title="Update Player Names"):
  def __init__(self, store):
    super().__init__()
    self.store:Store = store

    self.old_name = ui.Label(
      text="Old Name",
      component=ui.TextInput(placeholder="Old Name", required=True),
    )
    self.add_item(self.old_name)

    self.new_name = ui.Label(
      text="New Name",
      component=ui.TextInput(placeholder="New Name", required=True),
    )
    self.add_item(self.new_name)

  async def on_submit(self, interaction: Interaction) -> None:
    await interaction.response.defer(thinking=True, ephemeral=True)
    old_name = ConvertInput(self.old_name.component.value)
    new_name = ConvertInput(self.new_name.component.value)
    count = UpdatePlayerNames(
      self.store,
      old_name,
      new_name
    )