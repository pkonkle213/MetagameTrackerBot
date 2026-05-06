from discord.ext import commands
from discord import app_commands, Interaction
from services.top_players_services import GetTopPlayers
from output_builder import BuildTableOutput
from services.command_error_service import Error
from checks import IsStore

class StoreTopPlayers(commands.Cog):
  def __init__(self, bot:commands.Bot):
    self.bot = bot

  @app_commands.command(name="leaderboard",
                        description="Get the top players of the format")
  @app_commands.guild_only()
  @IsStore()
  @app_commands.checks.cooldown(1, 60.0, key=lambda i: (i.guild_id, i.user.id))
  async def Leaderboard(self,
                       interaction: Interaction,
                       start_date: str = '',
                       end_date: str = ''):
    """
    Parameters
    ----------
    start_date: string
      Beginning of Date Range (MM/DD/YYYY)
    end_date: string
      End of Date Range (MM/DD/YYYY)
    """
    await interaction.response.defer(thinking=False)
    table = GetTopPlayers(
      interaction,
      start_date,
      end_date
      )

    if len(table.data) == 0:
      await interaction.followup.send('No players found for this game or format')
    else:
      output = BuildTableOutput(table.title, table.headers, table.data)
      await interaction.followup.send(output)
  
  @Leaderboard.error
  async def Errors(self,
                   interaction: Interaction,
                   error: app_commands.AppCommandError):
    await Error(self.bot, interaction, error)

async def setup(bot:commands.Bot):
  await bot.add_cog(StoreTopPlayers(bot))