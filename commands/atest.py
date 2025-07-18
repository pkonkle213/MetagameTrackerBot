import discord
from discord.ext import commands
from discord import app_commands, Interaction
from custom_errors import KnownError
from discord_messages import Error
import settings
from timedposts.automated_updates import UpdateDataGuild

#TODO: This is an interesting way to get Level 2 stores, if they exist in the future
TARGET_GUILDS = [settings.TESTSTOREGUILD.id]

class ATest(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
  
  @app_commands.command(name="atest",
                        description="Tests something stupid!")
  @app_commands.guild_only()
  @app_commands.guilds(*[discord.Object(id=guild_id) for guild_id in TARGET_GUILDS])
  async def Testing(self, interaction: Interaction):
    await UpdateDataGuild(self.bot)
  
async def setup(bot):
  await bot.add_cog(ATest(bot))
