import discord
from discord.ext import commands
from discord import app_commands, Interaction
from checks import isSubmitter
from commands.claim_archetype_command import MessageStoreFeed
import settings

TARGET_GUILDS = [settings.TESTSTOREGUILD.id, 1210746744602890310]

class ATest(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
  
  @app_commands.command(name="atest",
                        description="Tests something stupid!")
  @app_commands.guild_only()
  @app_commands.guilds(*[discord.Object(id=guild_id) for guild_id in TARGET_GUILDS])
  async def Testing(self, interaction: Interaction):
    await interaction.followup.send("Testing!")
    
async def setup(bot):
  await bot.add_cog(ATest(bot))
