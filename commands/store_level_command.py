from discord.ext import commands
from discord import app_commands, Interaction
from services.store_level_check_service import CheckMyStoreLevel
from output_builder import BuildTableOutput
import settings
import discord

TARGET_GUILDS = [settings.TESTSTOREGUILD.id]

class CheckStoreLevel(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @app_commands.command(name="check_store_level",
                        description="Check the level of your store")
  @app_commands.checks.has_role("MTSubmitter")
  @app_commands.guild_only()
  @app_commands.guilds(*[discord.Object(id=guild_id) for guild_id in TARGET_GUILDS])
  async def CheckStoreLevel(self, interaction: Interaction):
    await interaction.response.defer()
    try:
      data, title, headers = CheckMyStoreLevel(interaction)
      output = BuildTableOutput(title, headers, data)
      await interaction.followup.send(output, ephemeral=True)
    except Exception as exception:
      await interaction.followup.send(f"Something went wrong: {exception}")

async def setup(bot):
  await bot.add_cog(CheckStoreLevel(bot))