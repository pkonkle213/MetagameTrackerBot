import discord
from discord.ext import commands
import settings
from timedposts.automated_updates import UpdateDataGuild

class ForceDataGuildUpdate(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @discord.app_commands.command(name="force_update",
                                description="Force an update of the data guild")
  @discord.app_commands.guilds(settings.BOTGUILDID)
  async def ForceUpdate(self, interaction: discord.Interaction):
    await interaction.response.defer(thinking=False)
    try:
      await UpdateDataGuild(self.bot)
      await interaction.followup.send("Data guild updated!")
    except Exception as exception:
      await interaction.followup.send(f"Error updating data guild: {exception}", ephemeral=True)

async def setup(bot):
  await bot.add_cog(ForceDataGuildUpdate(bot))