from next_text_modal import SubmitArchetypeModal
import typing
import discord
from discord.ext import commands
from discord import app_commands, Interaction
import settings

TARGET_GUILDS = [settings.TESTGUILDID]
                 
class ATest(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @app_commands.command(name="atest",
                        description="Tests something stupid!")
  @app_commands.guild_only()
  @app_commands.guilds(*[discord.Object(id=guild_id) for guild_id in TARGET_GUILDS])
  @app_commands.checks.has_role('MTSubmitter') #TODO: Find a way to check the role, idk why this doesn't get caught
  async def Testing(self,
                    interaction: discord.Interaction):
    modal = SubmitArchetypeModal()
    await interaction.response.send_modal(modal)
    return await interaction.followup.send("Testing.")

  @Testing.error
  async def on_tree_error(self,
                          interaction: Interaction,
                          error: app_commands.AppCommandError):
    await interaction.response.send_message(str(error))

async def setup(bot):
  await bot.add_cog(ATest(bot))
