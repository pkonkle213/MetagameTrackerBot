from services.tournament_predictions_services import PredictMyTop8
from checks import isPaidUser
from discord import app_commands, Interaction
from discord.ext import commands
from services.tournament_predictions_services import NumRounds, PredictTop8
from services.command_error_service import Error

"""
Things I want to predict:
1) Rounds based upon attendance
2) Records for the Top 8
3) Your probability to make Top 8 based upon your win %
...10) Total EV for the tournament
"""

class PredictionCommands(commands.GroupCog, name='predict'):
  """A group of commands to predict tournament outcomes"""

  def __init__(self, bot):
    self.bot = bot

  @app_commands.command(name="tournament",
                        description="Predict tournament details")
  @app_commands.checks.cooldown(1, 60.0, key=lambda i: (i.guild_id, i.user.id))
  @app_commands.guild_only()
  async def PredictTournament(self, interaction: Interaction, players:int):
    """
    Parameters:
    ----------

    players: int
      The number of players in the tournament
    """
    await interaction.response.defer(thinking=True)
    rounds = NumRounds(players)
    output = f"There will be {rounds} rounds in this tournament"

    top8 = PredictTop8(players, rounds)
    output += f"\n\nThe top 8 may feature (assuming no draws):\n{top8}"
    await interaction.followup.send(output)

  @app_commands.command(name='my_chances',
                       description="Predict your chances of making top 8")
  @app_commands.checks.cooldown(1, 60.0, key=lambda i: (i.guild_id, i.user.id))
  @app_commands.guild_only()
  @isPaidUser()
  async def PredictTop8(self, interaction: Interaction, players:int):
    """
    Parameters:
    ----------

    players: int
      The number of players in the tournament
    """
    await interaction.response.defer(thinking=True)
    rounds = NumRounds(players)
    output = f"There will be {rounds} rounds in this tournament"

    top8 = PredictMyTop8(interaction.user.id, players, rounds)

  @PredictTournament.error
  async def Errors(self, interaction: Interaction,
                   error: app_commands.AppCommandError):
    await Error(self.bot, interaction, error)

async def setup(bot):
  await bot.add_cog(PredictionCommands(bot))