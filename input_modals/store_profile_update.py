import discord

from tuple_conversions import Store

class StoreProfileModal(discord.ui.Modal, title='Update Store Profile'):
  def __init__(self, store: Store) -> None:
    super().__init__()

    self.store_name = discord.ui.Label(
      text="Store Name",
      component=discord.ui.TextInput(
        placeholder="Store name",
        default=store.StoreName,
        required=True
      )
    )
    self.add_item(self.store_name)

    self.owners_name = discord.ui.Label(
      text="Owner's Name",
      component=discord.ui.TextInput(
        placeholder="Owner's name",
        default=store.OwnerName,
        required=True
      )
    )
    self.add_item(self.owners_name)

    self.store_address = discord.ui.Label(
      text="Store Address",
      component=discord.ui.TextInput(
        placeholder="Store address",
        required=False
      )
    )
    self.add_item(self.store_address)

    self.melee_id = discord.ui.Label(
      text="Melee ClientId",
      component=discord.ui.TextInput(
        placeholder="Melee ID",
        required=False
      )
    )
    self.add_item(self.melee_id)

    self.melee_secret = discord.ui.Label(
      text="Melee Secret",
      component=discord.ui.TextInput(
        placeholder="Melee Secret",
        required=False
      )
    )
    self.add_item(self.melee_secret)

  async def on_submit(self, interaction: discord.Interaction) -> None:
    self.submitted_store_name = self.store_name.component.value
    self.submitted_owners_name = self.owners_name.component.value
    self.submitted_store_address = self.store_address.component.value
    self.submitted_melee_id =  self.melee_id.component.value if self.melee_id.component else None
    self.submitted_melee_secret = self.melee_secret.value if self.melee_secret else None
    self.is_submitted = True
    await interaction.response.defer()

  async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
    await interaction.followup.send(f'Oops! Something went wrong: {error}', ephemeral=True)
    self.is_submitted = False
  
  async def on_timeout(self) -> None:
    self.is_submitted = False