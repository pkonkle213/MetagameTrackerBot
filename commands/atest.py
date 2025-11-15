import discord
from discord.ext import commands
from discord import app_commands, Interaction
import settings
from timedposts.automated_check_events import GetEventsWithUnkown

TARGET_GUILDS = [settings.TESTGUILDID]
                 
class ATest(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
  
  @app_commands.command(name="atest",
                        description="Tests something stupid!")
  @app_commands.guild_only()
  @app_commands.guilds(*[discord.Object(id=guild_id) for guild_id in TARGET_GUILDS])
  #@app_commands.checks.has_role('MTSubmitter')
  async def Testing(self,
                    interaction: Interaction):
    await interaction.response.defer(ephemeral=True)
    await GetEventsWithUnkown(self.bot)
    await interaction.followup.send("Testing?")
  
  @Testing.error
  async def on_tree_error(self,
                          interaction: Interaction,
                          error: app_commands.AppCommandError):
    await interaction.response.send_message(str(error))

async def setup(bot):
  await bot.add_cog(ATest(bot))
