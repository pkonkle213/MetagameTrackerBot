import discord
from discord.ext import commands
from discord import app_commands, Interaction
import settings
from services.demonstration_functions import NewDemo

TARGET_GUILDS = [settings.TESTSTOREGUILD.id]

class NewDemoCommand(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @app_commands.command(name="demo",
  description="Set up the database for a demonstration")
  @app_commands.guilds(*[discord.Object(id=guild_id) for guild_id in TARGET_GUILDS])
  async def Demo(self, interaction: Interaction):
    await interaction.response.defer()
    NewDemo()
    await interaction.followup.send('All set up!')

async def setup(bot):
  await bot.add_cog(NewDemoCommand(bot))