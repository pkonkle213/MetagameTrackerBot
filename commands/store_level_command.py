from custom_errors import KnownError
from services.command_error_service import Error, MissingRoleError
from discord.ext import commands
from discord import app_commands, Interaction
from services.store_level_check_service import CheckMyStoreLevel, GetLevelDetails
from output_builder import BuildTableOutput
import settings
import discord

TARGET_GUILDS = [settings.TESTGUILDID]

class CheckStoreLevel(commands.GroupCog, name='level'):
  """Group of commands to check the level of your store"""
  def __init__(self, bot):
    self.bot = bot

  @app_commands.command(name="check",
                        description="Check the level of your store")
  @app_commands.checks.has_role("MTSubmitter")
  @app_commands.guild_only()
  @app_commands.checks.cooldown(1, 60.0, key=lambda i: (i.guild_id, i.user.id))
  @app_commands.guilds(*[discord.Object(id=guild_id) for guild_id in TARGET_GUILDS])
  async def CheckStoreLevel(self, interaction: Interaction):
    await interaction.response.defer(ephemeral=True)
    try:
      level = CheckMyStoreLevel(interaction)
      await interaction.followup.send(f"As of tomorrow, your store is level {level}", ephemeral=True)
    except KnownError as exception:
      await interaction.followup.send(exception.message, ephemeral=True)
    except Exception as exception:
      await Error(self.bot, interaction, exception)

  @app_commands.command(name="details",
    description="Check the information about your store's events")
  @app_commands.checks.has_role("MTSubmitter")
  @app_commands.guild_only()
  @app_commands.checks.cooldown(1, 60.0, key=lambda i: (i.guild_id, i.user.id))
  @app_commands.guilds(*[discord.Object(id=guild_id) for guild_id in TARGET_GUILDS])
  async def LevelDetails(self, interaction: Interaction):
    try:
      await interaction.response.defer(ephemeral=True)
      data, title, headers = GetLevelDetails(interaction)
      output = BuildTableOutput(title, headers, data)
      await interaction.followup.send(output, ephemeral=True)
    except Exception as exception:
      await interaction.followup.send(f"Something went wrong: {exception}", ephemeral=True)

  @CheckStoreLevel.error
  async def CheckStoreLevelError(self, interaction, error):
    await MissingRoleError(interaction, error)
  
  @LevelDetails.error
  async def LevelDetailsError(self, interaction, error):
    await MissingRoleError(interaction, error)


async def setup(bot):
  await bot.add_cog(CheckStoreLevel(bot))