import discord
from discord.ext import commands
from discord import app_commands, Interaction
from services.personal_matchups import PersonalMatchups
from output_builder import BuildTableOutput
from discord_messages import Error

#GetTier2Stores
TARGET_GUILDS = [1,2]

class PersonalMatchupsCommand(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @app_commands.command(name='personalmatchups',
  description='See your matchups against archetypes in this format')
  @app_commands.guild_only()
  #@app_commands.guilds(*[discord.Object(id=guild_id) for guild_id in TARGET_GUILDS])
  async def PersonalMatchupReport(self,
                                  interaction: Interaction,
                start_date: str = '',
                end_date: str = ''):
    await interaction.response.defer(ephemeral=True)
    try:
      data, title, headers = PersonalMatchups(interaction, start_date, end_date)
      output = BuildTableOutput(title, headers, data)
      await interaction.followup.send(output)
    except Exception as exception:
      await interaction.followup.send("Something unexpected went wrong. It's been reported. Please try again in a few hours.", ephemeral=True)
      await Error(self.bot, exception)

async def setup(bot):
  await bot.add_cog(PersonalMatchupsCommand(bot))