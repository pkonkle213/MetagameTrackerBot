from input_modals.league_input_modal import LeagueInputModal
from discord.ext import commands
import discord
from data.league_data import GetActiveLeagues
from custom_errors import KnownError
from tuple_conversions import Event, Format, Game, Store, League

class ConfirmView(discord.ui.View):
  def __init__(
    self,
    bot:commands.Bot,
    store:Store,
    game:Game,
    format:Format,
    league:League
  ):
    super().__init__()
    self.league = league
    self.bot = bot
    self.store = store
    self.game = game
    self.format = format

  @discord.ui.button(
    label="Continue To Edit",
    style=discord.ButtonStyle.green
  )
  async def ConfirmLeague(self,
                         interaction:discord.Interaction,
                         button: discord.ui.Button):
    modal = LeagueInputModal(self.bot, self.store, self.game, self.format, league=self.league)
    await interaction.response.send_modal(modal)    

class LeagueSelector(discord.ui.Modal, title='Select League'):
  def __init__(self,
               bot:commands.Bot,
               store:Store,
               game:Game,
               format:Format,
               leagues:list[League],
               isEdit:bool = False
              ):
    super().__init__()
    self.isEdit = isEdit
    self.bot = bot
    self.leagues = leagues
    self.store = store
    self.game = game
    self.format = format
    self.is_submitted = False

    if len(self.leagues) == 0:
       raise KnownError('No leagues found for this store, game, and format')

    current_leagues = [discord.SelectOption(label=league.name, value=str(league.id)) for league in self.leagues]
    self.selected_league = discord.ui.Label(
      text="Select a League",
      component=discord.ui.Select(
        placeholder="Select a league",
        required=True,
        options=current_leagues,
        max_values=1,
        min_values=1
      )
    )
    self.add_item(self.selected_league)

  async def on_submit(self, interaction: discord.Interaction):
    self.league = GetLeague(self.selected_league.component.values[0], self.leagues)
    self.is_submitted=True
    if not self.isEdit:
      await interaction.response.defer()
    else:
      await interaction.response.send_message(
        content=f"You selected {self.league.name}. Please fill out the form to edit the league.",
        view=ConfirmView(self.bot, self.store, self.game, self.format, self.league),
        ephemeral=True
      )
  
  async def on_error(
    self,
    interaction: discord.Interaction,
    error: Exception
  ) -> None:
    await interaction.followup.send(f'Oops! Something went wrong: {error}',
                    ephemeral=True)
    self.is_submitted = False

  async def on_timeout(self) -> None:
    self.is_submitted = False

def GetLeague(league_id:int, all_leagues:list[League]) -> League:
  for league in all_leagues:
    if league.id == int(league_id):
      return league

  raise Exception('No league found?')