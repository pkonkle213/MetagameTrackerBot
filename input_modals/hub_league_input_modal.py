from custom_errors import KnownError
from services.date_functions import ConvertToDate
import discord
from datetime import date
from discord_messages import MessageChannel
from discord.ext import commands
from tuple_conversions import League, Store, Game, Format, Hub, Region
from services.league_input_modal_services import CreateLeagueInput, UpdateLeagueInput
from data.hub_leagues_data import GetAllowedStores, UpdateAssociatedStores

#TODO: When the league is being edited, the stores already associated with the league should be selected by default
class HubLeagueInputModal(discord.ui.Modal, title="League Input"):
  def __init__(
    self,
    bot:commands.Bot,
    hub:Hub,
    game:Game,
    format:Format,
    region:Region,
    league:League | None = None
  ):
    super().__init__()
    self.bot = bot
    self.league = league
    self.hub = hub
    self.game = game
    self.format = format
    self.region = region
    
    self.allowed_stores = GetAllowedStores(hub, game, format, region)
    select_stores = [discord.SelectOption(label=store.store_name, value=str(store.discord_id)) for store in self.allowed_stores]

    self.league_name = discord.ui.Label(
      text="League Name",
      component=discord.ui.TextInput(
        placeholder="Enter the name of the league",
        default=league.name if league else None,
        required=True,
        max_length=100,
      ),
    )
    self.add_item(self.league_name)

    self.date_range = discord.ui.Label(
      text="Date Range (MM/DD/YYYY-MM/DD/YYYY)",
      component=discord.ui.TextInput(
        placeholder="Enter the start date of the league",
        default=f"{league.start_date.strftime("%m/%d/%Y")} - {league.end_date.strftime("%m/%d/%Y")}" if league else None,
        required=True,
        max_length=23,
      )
    )
    self.add_item(self.date_range)

    self.top_cut = discord.ui.Label(
      text="Cut To How Many Players",
      component=discord.ui.TextInput(
        placeholder="Number of Players",
        default=str(league.top_cut) if league else None,
        required=True,
        max_length=2,
      )
    )
    self.add_item(self.top_cut)

    self.description = discord.ui.Label(
      text="Description",
      component=discord.ui.TextInput(
        style=discord.TextStyle.paragraph,
        placeholder="Enter a description of the league",
        default=league.description if league else None,
        required=False,
        max_length=2000
      )
    )
    self.add_item(self.description)

    self.associated_stores = discord.ui.Label(
      text="Associated Stores",
      component=discord.ui.Select(
        placeholder="Select Participating Stores",
        options = select_stores,
        min_values=0,
        max_values=len(self.allowed_stores),
        required=False
      )
    )
    self.add_item(self.associated_stores)

  async def on_submit(self, interaction: discord.Interaction):
    league_name = self.league_name.component.value
    start_date, end_date = self.date_range.component.value.split("-")[0:2]
    top_cut = self.top_cut.component.value
    description = self.description.component.value

    if self.league:
      league = UpdateLeagueInput(
        self.league.id,
        league_name,
        start_date,
        end_date,
        top_cut,
        description,
        interaction.user.id
      )
    else:
      league = CreateLeagueInput(
        self.hub.discord_id,
        self.game,
        self.format,
        league_name,
        start_date,
        end_date,
        top_cut,
        description,
        interaction.user.id
      )

    store_ids = [int(store_id) for store_id in self.associated_stores.component.values]
    UpdateAssociatedStores(league.id, store_ids)

    title = "New league created!" if not self.league else "League updated!"
    output = f'''{title}
    -------------------
    League Name: {league.name}
    Start Date: {league.start_date.strftime("%m/%d/%Y")}
    End Date: {league.end_date.strftime("%m/%d/%Y")}
    Cuts to Top: {league.top_cut}
    Description: {league.description}'''

    await MessageChannel(self.bot, output, interaction.guild_id, interaction.channel_id)   
    await interaction.response.send_message(title, ephemeral=True)
    self.submitted = True

  async def on_error(
    self,
    interaction: discord.Interaction,
    error: Exception
  ) -> None:
    await interaction.followup.send(f'Something went wrong: {error}',
                    ephemeral=True)
    self.is_submitted = False

  async def on_timeout(self) -> None:
    self.is_submitted = False
