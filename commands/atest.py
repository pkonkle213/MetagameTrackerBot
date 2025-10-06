import discord
from discord.ext import commands
from discord import app_commands, Interaction
import settings

TARGET_GUILDS = [settings.TESTGUILDID]
                 
class ATest(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @commands.Cog.listener()
  async def TestingError(self, interaction:Interaction, error:app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingRole):
      await interaction.followup.send("1st attempt to catch the error")
    else:
      await interaction.followup.send("2nd attempt to catch the error")
 
  @app_commands.command(name="atest",
                        description="Tests something stupid!")
  @app_commands.guild_only()
  @app_commands.guilds(*[discord.Object(id=guild_id) for guild_id in TARGET_GUILDS])
  #@app_commands.checks.has_role('MTSubmitter')
  async def Testing(self, interaction: Interaction):
    await interaction.response.send_message("Hi! Testing!")
    
"""
  @Testing.error
  async def OtherError(self, interaction:Interaction, error:app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingRole):
      await interaction.followup.send("3rd attempt to catch the error")
    else:
      await interaction.followup.send("4th attempt to catch the error")
    """
async def setup(bot):
  await bot.add_cog(ATest(bot))
