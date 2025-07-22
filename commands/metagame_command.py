from discord import app_commands, Interaction
from services.metagame_services import GetMyMetagame
from output_builder import BuildTableOutput
from discord_messages import Error

class MetagameGroup(app_commands.Group):
  @app_commands.command(name="combined",
                        description="Get the metagame sorted by a combined metric")
  async def Combined(self,
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
    output = await GetTheMetagame(interaction, start_date, end_date, 4)
    await interaction.followup.send(output)
  
  @app_commands.command(name="metashare",
                        description="Get the metagame sorted by metagame share")
  async def Metashare(self,
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
    output = await GetTheMetagame(interaction, start_date, end_date, 2)
    await interaction.followup.send(output)

async def GetTheMetagame(interaction, start_date, end_date, sort_order):
  try:
    data, title, headers, limited_format = GetMyMetagame(interaction, start_date, end_date, sort_order)
    if data is None or len(data) == 0:
      return 'No metagame data found for this store and format'
    return BuildTableOutput(title, headers, data, limited_format)
  except Exception as exception:
    await Error(interaction, exception)
    return "Something unexpected went wrong. It's been reported. Please try again in a few hours."

async def setup(bot):
  bot.tree.add_command(MetagameGroup(name='metagame'))
