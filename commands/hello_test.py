import discord
from discord.ext import commands
from discord import app_commands, Interaction
import settings

#TODO: This is an interesting way to get Level 2 stores, if they exist in the future
TARGET_GUILDS = [settings.TESTSTOREGUILD.id]

class ATest(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
  
  @app_commands.command(name="hello",
                        description="Says hello!")
  @app_commands.guild_only()
  @app_commands.guilds(*[discord.Object(id=guild_id) for guild_id in TARGET_GUILDS])
  async def hello(self, interaction: Interaction):
    await interaction.response.send_message(f"Hello, {interaction.user.display_name}!")
  
async def setup(bot):
  await bot.add_cog(ATest(bot))
