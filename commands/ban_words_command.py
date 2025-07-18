import discord
from discord.ext import commands
from discord import app_commands
from custom_errors import KnownError
from services.ban_word_services import AddBadWord
from discord_messages import Error

class BanWord(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @app_commands.command(name='addword',
    description='Add a banned word')
  @app_commands.checks.has_role('MTSubmitter')
  @app_commands.guild_only()
  async def BadWord(self,
                    interaction: discord.Interaction,
                    word:str):
    """
    Parameters
    ----------
    word: string
      The inappropriate word or phrase to ban
    """
    await interaction.response.defer()
    try:
      if len(word) < 3:
        await interaction.response.send_message('Word must be at least 3 characters long')
      else:
        await interaction.response.defer(ephemeral=True)
        check = AddBadWord(interaction, word)
        if check:
          await interaction.followup.send('Word added and offending archetypes disabled')
        else:
          await interaction.followup.send('Something went wrong. Please try again later.', ephemeral=True)
    except KnownError as exception:
      await interaction.followup.send(exception.message, ephemeral=True)
    except Exception as exception:
      await interaction.followup.send("Something unexpected went wrong. It's been reported. Please try again in a few hours.", ephemeral=True)
      await Error(self.bot, exception)

async def setup(bot):
  await bot.add_cog(BanWord(bot))
