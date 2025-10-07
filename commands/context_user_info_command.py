from discord.ext import commands
from discord import app_commands, Interaction, Member

from custom_errors import KnownError
from services.user_info_services import GetUserData

class UserInfoCommand(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

    self.user_info_context_menu = app_commands.ContextMenu(
      name='Get User Info',  # This is the name displayed in Discord
      callback=self.GetUserInfo # The function to call when the command is used
    )
    # Add the context menu to the bot's command tree
    self.bot.tree.add_command(self.user_info_context_menu)

  @app_commands.guild_only()
  async def GetUserInfo(self, interaction: Interaction, member: Member):
    """Callback for the 'Get User Info' context menu command."""
    await interaction.response.defer(ephemeral=True)
    try:
      (player_name,
       win_percent,
       last_played,
       top_decks) = GetUserData(interaction, member)

      output = f"Player Name: {player_name}\nWin %: {win_percent}\nLast Played: {last_played[1].title()} ({last_played[0].strftime('%-m/%-d/%Y')})\nMost Played Decks:\n"
      for deck in top_decks:
        output += f"\t{deck[0]} - {deck[2]}%\n"
      await interaction.followup.send(output, ephemeral=True)
    except KnownError as error:
      await interaction.followup.send(error.message, ephemeral=True)
    except Exception as error:
      await interaction.followup.send(f"An error occurred: {error}", ephemeral=True) #TODO: Fix

async def setup(bot):
  await bot.add_cog(UserInfoCommand(bot))