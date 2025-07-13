import discord
from discord.ext import commands
from discord import app_commands
from services.ban_word import AddBadWord

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
    if len(word) < 3:
      await interaction.response.send_message('Word must be at least 3 characters long')
    else:
      await interaction.response.defer(ephemeral=True)
      check = AddBadWord(interaction, word)
      if check:
        await interaction.followup.send('Word added and offending archetypes disabled')
      else:
        await interaction.followup.send('Something went wrong. Please try again later.', ephemeral=True)

async def setup(bot):
  await bot.add_cog(BanWord(bot))
