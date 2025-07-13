from discord.ext import commands
from discord import app_commands, Interaction
from services.ban_word import Offenders
from output_builder import BuildTableOutput

class BannedWordsOffenders(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @app_commands.command(name='offenders',
  description='See who has been flagged for bad words/phrases')
  @app_commands.checks.has_role('MTSubmitter')
  async def StoreOffenders(self, interaction: Interaction):
    await interaction.response.defer(ephemeral=True)
    data, title, headers = Offenders(interaction)
    output = BuildTableOutput(title, headers, data)
    await interaction.followup.send(output)

async def setup(bot):
  await bot.add_cog(BannedWordsOffenders(bot))