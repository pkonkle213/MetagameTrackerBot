from discord import app_commands
from discord.ext import commands
import discord
import settings

TARGET_GUILDS = [settings.BOTGUILD.id]

class LeaveAGuild(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    
  @app_commands.command(name='leavethisguild',
              description='Makes the bot leave a specific guild by its ID.')
  @app_commands.guilds(*[discord.Object(id=guild_id) for guild_id in TARGET_GUILDS])
  async def leavethisguild(self, interaction:discord.Interaction, guild_id: str):
    """
    Makes the bot leave a specific guild by its ID.
    Usage: !leaveguild <guild_id>
    """
    guild = self.bot.get_guild(int(guild_id))
    if guild is None:
      await interaction.response.send_message(f"Guild with ID `{guild_id}` not found.")
      return
  
    try:
      await guild.leave()
      await interaction.response.send_message(f"Successfully left the guild: `{guild.name}` (ID: `{guild.id}`).")
    except discord.Forbidden:
      await interaction.response.send_message(f"I don't have permission to leave `{guild.name}` (ID: `{guild.id}`).")
    except Exception as e:
      await interaction.response.send_message(f"An error occurred while trying to leave `{guild.name}`: `{e}`")

async def setup(bot):
  await bot.add_cog(LeaveAGuild(bot))