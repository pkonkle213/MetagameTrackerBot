from custom_errors import KnownError
from discord import app_commands, Interaction
from discord.ext import commands
from services.metagame_services import GetMyMetagame
from output_builder import BuildTableOutput
from services.command_error_service import Error

class MetagameCommand(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @app_commands.command(name="metagame",
                        description="Get the metagame for this format")
  @app_commands.checks.cooldown(1, 60.0, key=lambda i: (i.guild_id, i.user.id))
  async def ViewMetagame(self,
                   interaction: Interaction,
                   start_date: str = '',
                   end_date: str = ''):
    """
    Parameters
    ----------
    start_date: string
      The start date of the metagame (MM/DD/YYYY)
    end_date: string
      The end date of the metagame (MM/DD/YYYY)
    """
    await interaction.response.defer()
    try:
      data, title, headers, archetype_column = GetMyMetagame(interaction, start_date, end_date)
      if data is None or len(data) == 0:
        await interaction.followup.send('No metagame data found for this store and format')
      else:
        output = BuildTableOutput(title, headers, data, archetype_column)
        await interaction.followup.send(output)
    except KnownError as exception:
      await interaction.followup.send(exception.message, ephemeral=True)
    except Exception as exception:
      await Error(self.bot, interaction, exception)

async def setup(bot):
  await bot.add_cog(MetagameCommand(bot))
