import discord.ui.select
from discord.ext import commands
from services.command_error_service import Error
import discord
from tuple_conversions import Store, Hub, Game, Format
from data.data_hubs_data import GetPossibleHubs

class StoreProfileModal(discord.ui.Modal, title='Update Store Profile'):
  is_submitted = False
  
  def __init__(
    self,
    bot:commands.Bot,
    store: Store,
    game: Game | None,
    format: Format | None
  ) -> None:
    super().__init__()
    self.bot = bot
    

    possible_hubs = GetPossibleHubs(store, game, format)
    self.select_hubs = [discord.SelectOption(label=hub.hub_name, value=str(hub.discord_id)) for hub in possible_hubs]

    self.store_name = discord.ui.Label(
      text="Store Name",
      component=discord.ui.TextInput(
        placeholder="Store name",
        default=store.store_name if store else "",
        required=True
      )
    )
    self.add_item(self.store_name)
    
    self.store_address = discord.ui.Label(
      text="Store Address",
      component=discord.ui.TextInput(
        placeholder="Store address",
        default=store.store_address if store else "",
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

    if len(self.select_hubs) > 0:
      self.approved_hubs = discord.ui.Label(
        text="Approved Hubs",
        component=discord.ui.Select(
          placeholder="Select hubs",
          options=self.select_hubs,
          min_values=0,
          max_values=len(self.select_hubs),
          required=False
        )
      )
      self.add_item(self.approved_hubs)

  async def on_submit(self, interaction: discord.Interaction) -> None:
    self.submitted_hubs:list[int] = []
    if len(self.select_hubs) > 0:
      self.submitted_hubs = CreateHubList(self.approved_hubs.component.values)
      
    self.submitted_store_name = self.store_name.component.value
    self.submitted_store_address = self.store_address.component.value
    self.submitted_melee_id =  self.melee_id.component.value if self.melee_id.component.value else None
    self.submitted_melee_secret = self.melee_secret.component.value if self.melee_secret.component.value else None
    self.is_submitted = True
    self.new_interaction = interaction
    await interaction.response.defer(thinking=True, ephemeral=True)

  async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
    await Error(self.bot, interaction, error)
  
  async def on_timeout(self) -> None:
    self.is_submitted = False

def CreateHubList(hub_ids: list[str]) -> list[int]:
  return [int(id) for id in hub_ids]
  