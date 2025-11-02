import discord
from settings import BOTGUILDID
from discord.ext import commands
from discord import app_commands, Interaction
from services.demonstration_functions import NewDemo
from services.command_error_service import Error

TARGET_GUILDS = [BOTGUILDID]

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
    
  @Demo.error
  async def Errors(self,
                   interaction: discord.Interaction,
                   error: app_commands.AppCommandError):
    await Error(self.bot, interaction, error)

async def setup(bot):
  await bot.add_cog(NewDemoCommand(bot))