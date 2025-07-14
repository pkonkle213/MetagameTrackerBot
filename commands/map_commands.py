from discord.ext import commands
from discord import app_commands, Interaction
from services.formats import AddStoreFormatMap, GetFormatOptions
from services.game_mapper import AddStoreGameMap, GetGameOptions
from select_menu_bones import SelectMenu
from discord_messages import Error

class MappingCommands(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @app_commands.command(name='mapgame',
                        description='Map your category to a game')
  @app_commands.checks.has_role("MTSubmitter")
  @app_commands.guild_only()
  async def AddGameMap(self, interaction: Interaction):
    await interaction.response.defer(ephemeral=True)
    try:
      message = 'Please select a game'
      placeholder = 'Choose a game'
      dynamic_options = GetGameOptions()
      result = await SelectMenu(interaction, message, placeholder, dynamic_options)
      output = AddStoreGameMap(interaction, result[0])
      await interaction.followup.send(output, ephemeral=True)
    except Exception as exception:
      await interaction.followup.send("Something unexpected went wrong. It's been reported. Please try again in a few hours.", ephemeral=True)
      await Error(self.bot, exception)

  @app_commands.command(name='mapformat',
                    description='Map your channel to a format')
  @app_commands.checks.has_role("MTSubmitter")
  @app_commands.guild_only()
  async def AddFormatMap(self, interaction: Interaction):
    await interaction.response.defer(ephemeral=True)
    try:
      dynamic_options = GetFormatOptions(interaction)
      if dynamic_options is None or len(dynamic_options) == 0:
        await interaction.followup.send('No formats found for this game')
      else:
        message = 'Please select a format'
        placeholder = 'Choose a format'
        result = await SelectMenu(interaction, message, placeholder, dynamic_options)
        output = AddStoreFormatMap(interaction, result[0])
        await interaction.followup.send(output, ephemeral=True)
    except Exception as exception:
      await interaction.followup.send("Something unexpected went wrong. It's been reported. Please try again in a few hours.", ephemeral=True)
      await Error(self.bot, exception)
    
async def setup(bot):
  await bot.add_cog(MappingCommands(bot))