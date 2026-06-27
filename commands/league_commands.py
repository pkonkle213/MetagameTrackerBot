from services.command_error_service import KnownError
from services.command_error_service import Error
from discord.ext import commands
from discord import app_commands, Interaction
from services.league_services import (
  CreateLeague,
  EditLeague,
  ViewLeague,
  SelectLeague,
  LeagueMetagame,
  LeagueLeaderboard,
  FindPlayerStanding,
  LeagueTimeLapse
)
from output_builder import BuildTableOutput
from checks import IsPaidStore


class LeaguesCommands(commands.GroupCog, name="league"):
  """A group of commands for managing Leagues"""

  def __init__(self, bot: commands.Bot):
    self.bot = bot

  @app_commands.command(name="create", description="Create a new league")
  @app_commands.guild_only()
  @IsPaidStore()
  @app_commands.checks.has_role("MTSubmitter")
  async def CreateLeague(self, interaction: Interaction):
    await CreateLeague(self.bot, interaction)

  @app_commands.command(name="edit", description="Exit a league")
  @app_commands.guild_only()
  @IsPaidStore()
  @app_commands.checks.has_role("MTSubmitter")
  async def EditLeague(self, interaction: Interaction):
    await EditLeague(self.bot, interaction)

  @app_commands.command(name="view", description="View a league")
  @app_commands.guild_only()
  @IsPaidStore()
  @app_commands.checks.has_role("MTSubmitter")
  async def ViewLeague(self, interaction: Interaction):
    output = await ViewLeague(self.bot, interaction)
    await interaction.followup.send(output)

  @app_commands.command(
    name="leaderboard", description="Display the top players in a league"
  )
  @app_commands.guild_only()
  @IsPaidStore()
  @app_commands.checks.cooldown(1, 60.0, key=lambda i: (i.guild_id, i.user.id))
  async def TopPlayers(self, interaction: Interaction):
    league = await SelectLeague(self.bot, interaction)
    data = LeagueLeaderboard(league)
    title = f"Top Players for {league.name}"
    headers = ["Player Name", "Points", "Win %"]
    output = BuildTableOutput(title, headers, data)
    await interaction.followup.send(output)

  @app_commands.command(
    name="leaderboard_race", description="Display the top players in a league"
  )
  @app_commands.guild_only()
  @IsPaidStore()
  @app_commands.checks.cooldown(1, 60.0, key=lambda i: (i.guild_id, i.channel.id))
  async def LeaderboardRace(self, interaction: Interaction):
    league = await SelectLeague(self.bot, interaction)
    data = LeagueTimeLapse(league)    
    await interaction.followup.send(file=data)

  @app_commands.command(
    name="metagame", description="Display the metagame of a league"
  )
  @app_commands.guild_only()
  @IsPaidStore()
  @app_commands.checks.cooldown(1, 60.0, key=lambda i: (i.guild_id, i.user.id))
  async def LeagueMeta(self, interaction: Interaction):
    league = await SelectLeague(self.bot, interaction)
    data = LeagueMetagame(league)
    title = f"Metagame for {league.name}"
    headers = ["Archetype Name", "Meta %", "Win %"]
    output = BuildTableOutput(title, headers, data)
    await interaction.followup.send(output)

  @app_commands.command(
    name="my_status",
    description="Shows how you compare to the top players in a league",
  )
  @IsPaidStore()
  @app_commands.guild_only()
  @app_commands.checks.cooldown(1, 60.0, key=lambda i: (i.guild_id, i.user.id))
  async def MyStatus(self, interaction: Interaction):
    league = await SelectLeague(self.bot, interaction)
    if not interaction.guild_id:
      raise KnownError("This command can only be used in a server")
    data = FindPlayerStanding(league, interaction.user.id, interaction.guild_id)
    title = f"Your Status for {league.name}"
    headers = ["Points", "Win %", "Rank"]
    output = BuildTableOutput(title, headers, [data])
    await interaction.followup.send(output, ephemeral=True)

  @CreateLeague.error
  @EditLeague.error
  @ViewLeague.error
  @TopPlayers.error
  @LeaderboardRace.error
  @LeagueMeta.error
  @MyStatus.error
  async def Errors(
    self, interaction: Interaction, error: app_commands.AppCommandError
  ):
    await Error(self.bot, interaction, error)


async def setup(bot: commands.Bot):
  await bot.add_cog(LeaguesCommands(bot))
