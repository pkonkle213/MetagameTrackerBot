import discord
from discord.ext import commands
from discord import app_commands, Interaction
from custom_errors import KnownError
from services.ban_word_services import AddBadWord, Offenders
from services.command_error_service import Error
from services.store_level_service import LEVEL1STORES, LEVEL2STORES
from output_builder import BuildTableOutput

class BannedWordCommands(commands.GroupCog, name='bannedwords'):
  """A group of commands for managing banned words"""
  def __init__(self, bot):
    self.bot = bot

  @app_commands.command(name='add',
                        description='Add a banned word')
  @app_commands.guild_only()
  @app_commands.guilds(*[discord.Object(id=guild_id) for guild_id in LEVEL1STORES])
  @app_commands.checks.has_role('MTSubmitter')
  async def BadWord(self,
                    interaction: Interaction,
                    word:str):
    """
    Parameters
    ----------
    word: string
      The inappropriate word or phrase to ban
    """
    await interaction.response.defer(ephemeral=True)
    try:
      if len(word) < 3:
        await interaction.followup.send('Word must be at least 3 characters long')
      else:
        check = AddBadWord(interaction, word)
        if check:
          await interaction.followup.send('Word added and offending archetypes disabled')
        else:
          await interaction.followup.send('Something went wrong. Please try again later.', ephemeral=True)
    except KnownError as exception:
      await interaction.followup.send(exception.message, ephemeral=True)
    except Exception as exception:
      await Error(self.bot, interaction, exception)

  @app_commands.command(name='offenders',
                        description='See who has been flagged for bad words/phrases')
  @app_commands.checks.has_role('MTSubmitter')
  @app_commands.guilds(*[discord.Object(id=guild_id) for guild_id in LEVEL2STORES])
  @app_commands.checks.cooldown(1, 60.0, key=lambda i: (i.guild_id, i.user.id))
  async def StoreOffenders(self, interaction: Interaction):
    await interaction.response.defer(ephemeral=True)
    try:
      data, title, headers = Offenders(interaction)
      output = BuildTableOutput(title, headers, data)
      await interaction.followup.send(output)
    except KnownError as exception:
      await interaction.followup.send(exception.message, ephemeral=True)
    except Exception as exception:
      await Error(self.bot, interaction, exception)

async def setup(bot):
  await bot.add_cog(BannedWordCommands(bot))
