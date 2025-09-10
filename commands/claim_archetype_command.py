from discord.ext import commands
from discord import app_commands, Interaction
from data.store_data import GetClaimFeed
import settings
from custom_errors import KnownError
from discord_messages import MessageChannel
from services.input_services import ConvertInput
from services.command_error_service import Error
from services.claim_result_services import AddTheArchetype

class ClaimArchetype(commands.GroupCog, name='claim'):
  """A group of commands to claim the archetype for a player"""
  def __init__(self, bot):
    self.bot = bot

  @app_commands.command(name='limited',
                        description='Enter the deck archetype for a player and their last played limited event')
  @app_commands.guild_only()
  async def ClaimLimited(self,
                         interaction: Interaction,
                         player_name: str,
                         date: str):
    """
      Parameters
      ----------
      player_name: string
        Your name in Companion
      date: string
        Date of event (MM/DD/YYYY)
      """
    await interaction.response.defer(ephemeral=True)
    try:
      private_output, feed_output, public_output, full_event = await AddTheArchetype(self.bot, interaction, player_name, date)
      await interaction.followup.send(private_output, ephemeral=True)
      await MessageStoreFeed(self.bot, feed_output, interaction)
      if public_output:
        await MessageChannel(self.bot,
                            public_output,
                            interaction.guild_id,
                            interaction.channel_id)
      if full_event:
        await MessageChannel(self.bot,
                             full_event,
                             interaction.guild_id,
                             interaction.channel_id)
    except KnownError as exception:
      await interaction.followup.send(exception.message, ephemeral=True)
    except Exception as exception:
      await Error(self.bot, interaction, exception)

  @app_commands.command(name='constructed',
                        description='Enter the deck archetype for a player and their last played constructed event')
  @app_commands.guild_only()
  async def ClaimConstructed(self,
                             interaction: Interaction,
                             player_name: str,
                             archetype: str,
                             date: str):
    """
    Parameters
    ----------
    player_name: string
      Your name in Companion
    archetype: string
      The deck archetype you played
    date: string
      Date of event (MM/DD/YYYY)
    """
    await interaction.response.defer(ephemeral=True)
    try:
      archetype = ConvertInput(archetype)
      private_output, feed_output, public_output, full_event = await AddTheArchetype(self.bot, interaction, player_name, date, archetype)
      await interaction.followup.send(private_output, ephemeral=True)
      await MessageStoreFeed(self.bot, feed_output, interaction)
      if public_output:
        await MessageChannel(self.bot,
                            public_output,
                            interaction.guild_id,
                            interaction.channel_id)
      if full_event:
        await MessageChannel(self.bot,
                             full_event,
                             interaction.guild_id,
                             interaction.channel_id)
    except ValueError:
      await interaction.followup.send("The date provided doesn't match the MM/DD/YYYY formatting. Please try again", ephemeral=True)
    except KnownError as exception:
      await interaction.followup.send(exception.message, ephemeral=True)
    except Exception as exception:
      await Error(self.bot, interaction, exception)

async def MessageStoreFeed(bot, message, interaction):
  try:
    #Message the store feed channel specific to the game
    channel_id = GetClaimFeed(interaction.guild_id,
                              interaction.channel.category.id)
    await MessageChannel(bot,
                         message,
                         interaction.guild_id,
                         channel_id)
  except Exception:
    #If none listed or found, message the bot guild
    await MessageChannel(bot,
                         message,
                         settings.BOTGUILDID,
                         settings.CLAIMCHANNEL)

async def setup(bot):
  await bot.add_cog(ClaimArchetype(bot))
