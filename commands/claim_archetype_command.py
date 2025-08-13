from discord.ext import commands
from discord import app_commands, Interaction
from data.store_data import GetClaimFeed
import settings
from services.claim_result_services import ClaimResult, CheckEventPercentage, OneEvent
from custom_errors import KnownError
from discord_messages import MessageChannel, MessageUser, Error
from output_builder import BuildTableOutput
from services.input_services import ConvertInput

#TODO: I think the AddTheArchetype function should be moved to the services folder
class ClaimArchetype(commands.GroupCog, name='claim'):
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
    await AddTheArchetype(self.bot, interaction, player_name, date)

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
    archetype = ConvertInput(archetype)
    await AddTheArchetype(self.bot, interaction, player_name, date, archetype)


async def AddTheArchetype(bot, interaction, player_name, date, archetype=''):
  try:
    archetype_submitted, event = await ClaimResult(interaction,
                                                   player_name,
                                                   archetype,
                                                   date)
    if archetype_submitted is None:
      #This would be due to a connection error with the database
      await interaction.followup.send('Unable to submit the archetype. Please try again later.')
    else:
      message = BuildMessage(interaction, date, archetype_submitted)
      await MessageStoreFeed(bot, message, interaction)
      await MessageChannel(bot,
                           message,
                           settings.BOTGUILD.id,
                           settings.CLAIMCHANNEL)
      await interaction.followup.send(f"Thank you for submitting the archetype for {event.EventDate.strftime('%B %d')}'s event!",
                                      ephemeral=True)
      #TODO: This should return a tuple of a message, a boolean to indicate if a follow up message should be sent to the channel, and a boolean to indicate if the event is fully reported and a snapshot of the event should be sent
      followup = CheckEventPercentage(event)
      if followup:
        if followup[1]:
          title, headers, data = OneEvent(event)
          output = BuildTableOutput(title, headers, data)
          await MessageChannel(bot,
                               output,
                               interaction.guild_id,
                               interaction.channel_id)
        else:
          await MessageChannel(bot,
                               followup[0],
                               interaction.guild_id,
                               interaction.channel_id)
  except ValueError:
    await interaction.followup.send("The date provided doesn't match the MM/DD/YYYY formatting. Please try again",
                                    ephemeral=True)
  except KnownError as exception:
    await interaction.followup.send(exception.message, ephemeral=True)
    message = BuildMessage(interaction, date, None, exception.message, player_name, archetype)
    await MessageStoreFeed(bot, message, interaction)      
  except Exception as exception:
    await  interaction.followup.send("Something unexpected went wrong. It's been reported. Please try again in a few hours.",
                                    ephemeral=True)
    await Error(bot, exception)

def BuildMessage(interaction, date, archetype_submitted=None, error_message=None, player_name='', archetype=''):
  message_parts = []
  message_parts.append(f'Submitter: {interaction.user.display_name}')
  if not archetype_submitted:
    message_parts.append(f'Ran into an error: {error_message}')
  message_parts.append(f'Archetype submitted: {archetype_submitted.Archetype if archetype_submitted else archetype}')
  message_parts.append(f'For player name: {player_name if not archetype_submitted else archetype_submitted.PlayerName}')
  message_parts.append(f'For date: {date}')
  message_parts.append(f'For channel name: {interaction.channel.name}')
  return '\n'.join(message_parts)  

async def MessageStoreFeed(bot, message, interaction):
  try:
    #Message the store feed channel
    channel_id = GetClaimFeed(interaction.guild_id,
                              interaction.channel.category.id)
    await MessageChannel(bot,
                         message,
                         interaction.guild_id,
                         channel_id)
  except Exception as exception:
    #If none listed or found, message the bot guild
    await MessageUser(bot, exception, settings.PHILID)
    await MessageChannel(bot,message, settings.BOTGUILD.id, settings.CLAIMCHANNEL)
  
async def setup(bot):
  await bot.add_cog(ClaimArchetype(bot))
