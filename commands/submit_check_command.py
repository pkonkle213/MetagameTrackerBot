from discord.ext import commands
from discord import app_commands, Interaction
from checks import isSubmitter
from interaction_data import GetInteractionData
from discord_messages import Error

class SubmitDataChecker(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @app_commands.command(name="submitcheck",
    description="To test if you can submit data")
  @app_commands.guild_only()
  @app_commands.checks.has_role('MTSubmitter')
  async def SubmitCheck(self, interaction: Interaction):
    await interaction.response.defer(ephemeral=True)
    try:
      issues = ['Issues I detect:']
      game, format, store, userId = GetInteractionData(interaction)
      if not store:
        issues.append('- Store not registered')
      if not store.ApprovalStatus:
        issues.append('- Store not approved for data submission')
      if not isSubmitter(interaction.guild, interaction.user, 'MTSubmitter'):
        issues.append("- You don't have the MTSubmitter role.")
      if not game:
        issues.append('- Category not mapped to a game')
      if not format:
        issues.append('- Channel not mapped to a format')
      
      if len(issues) == 1:
        await interaction.followup.send('Everything looks good. Please reach out to Phil to test your data')
      else:
        await interaction.followup.send('\n'.join(issues))
    except Exception as exception:
      await interaction.followup.send("Something unexpected went wrong. It's been reported. Please try again in a few hours.", ephemeral=True)
      await Error(self.bot, exception)

async def setup(bot):
  await bot.add_cog(SubmitDataChecker(bot))
