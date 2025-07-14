from discord.ext import commands
from discord import app_commands, Interaction
from services.metagame import GetMyMetagame
from output_builder import BuildTableOutput
from discord_messages import Error

class MetagameCommand(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @app_commands.command(name="metagame",
                    description="Get the metagame")
  async def Metagame(self, interaction: Interaction,
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
      data, title, headers = GetMyMetagame(interaction, start_date, end_date)
      output = ''
      if data is None:
        output = 'No metagame data found for this store and format'
      else:
        output = BuildTableOutput(title, headers, data)
        await interaction.followup.send(output)
    except Exception as exception:
      await interaction.followup.send("Something unexpected went wrong. It's been reported. Please try again in a few hours.", ephemeral=True)
      await Error(self.bot, exception)

async def setup(bot):
  await bot.add_cog(MetagameCommand(bot))
