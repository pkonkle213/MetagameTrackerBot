from discord.ext import commands
from discord import app_commands
import discord

#This command is for family use, not for public use
class CleanUpCommand(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  TARGET_GUILDS = [1221914147634020402]

  @app_commands.command(name='cleanup', description='Clean up the guild')
  @app_commands.guilds(*[discord.Object(id=guild_id) for guild_id in TARGET_GUILDS])
  async def CleanUp(self, interaction):
    await interaction.response.send_message('Cleaning up the guild...')
    userId = 762427840238321685 #Evil ex-girlfriend
    try:
      messages = [msg async for msg in interaction.channel.history(limit=10, oldest_first=False)]
      for message in messages:
        if message.author.id == userId:
          await message.delete()
      await interaction.followup.send('Clean up complete!')
    except Exception as exception:
      await interaction.followup.send(f'Error: {exception}')

async def setup(bot):
  await bot.add_cog(CleanUpCommand(bot))