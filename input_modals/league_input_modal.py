import discord
from tuple_conversions import League

class LeagueInputModal(discord.ui.Modal, title="League Input"):
  def __init__(self, league:League | None = None):
    super().__init__()

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

    self.start_date = discord.ui.Label(
      text="Start Date (MM/DD/YYYY)",
      component=discord.ui.TextInput(
        placeholder="Enter the start date of the league",
        default=league.start_date.strftime("%m/%d/%Y") if league else None,
        required=True,
        max_length=10,
      )
    )
    self.add_item(self.start_date)

    self.end_date = discord.ui.Label(
      text="End Date (MM/DD/YYYY)",
      component=discord.ui.TextInput(
        placeholder="Enter the end date of the league",
        default=league.end_date.strftime("%m/%d/%Y") if league else None,
        required=True,
        max_length=10,
      )
    )
    self.add_item(self.end_date)

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

  async def on_submit(self, interaction: discord.Interaction):
    self.submitted_name = self.league_name.component.value
    self.submitted_start_date = self.start_date.component.value
    self.submitted_end_date = self.end_date.component.value
    self.submitted_top_cut = self.top_cut.component.value
    self.submitted_description = self.description.component.value
    self.is_submitted = True
    await interaction.response.defer(thinking=True)

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