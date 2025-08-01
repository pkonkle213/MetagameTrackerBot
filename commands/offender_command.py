from discord.ext import commands
from discord import app_commands, Interaction
from services.ban_word_services import Offenders
from output_builder import BuildTableOutput
from discord_messages import Error

class BannedWordsOffenders(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @app_commands.command(name='offenders',
  description='See who has been flagged for bad words/phrases')
  @app_commands.checks.has_role('MTSubmitter')
  async def StoreOffenders(self, interaction: Interaction):
    await interaction.response.defer(ephemeral=True)
    try:
      data, title, headers = Offenders(interaction)
      output = BuildTableOutput(title, headers, data)
      await interaction.followup.send(output)
    except Exception as exception:
      await interaction.followup.send("Something unexpected went wrong. It's been reported. Please try again in a few hours.", ephemeral=True)
      await Error(self.bot, exception)

async def setup(bot):
  await bot.add_cog(BannedWordsOffenders(bot))