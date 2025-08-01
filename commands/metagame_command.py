from discord import app_commands, Interaction
from discord.ext import commands
from services.metagame_services import GetMyMetagame
from output_builder import BuildTableOutput
from discord_messages import Error

class MetagameCommand(commands.Cog):
  @app_commands.command(name="metagame",
                        description="Get the metagame for this format")
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
      data, title, headers, limited_format = GetMyMetagame(interaction, start_date, end_date)
      if data is None or len(data) == 0:
        await interaction.followup.send('No metagame data found for this store and format')
      output = BuildTableOutput(title, headers, data, limited_format)
      await interaction.followup.send(output)
    except Exception as exception:
      await Error(interaction, exception)
      print('Error in GetTheMetagame:', exception)
      await interaction.followup.send("Something unexpected went wrong. It's been reported. Please try again in a few hours.")

async def setup(bot):
  await bot.add_cog(MetagameCommand(bot))
