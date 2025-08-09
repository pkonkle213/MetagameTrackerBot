from discord.ext import commands
from discord import app_commands, Interaction
import settings
from services.claim_result_services import ClaimResult, CheckEventPercentage, OneEvent
from custom_errors import KnownError
from discord_messages import MessageChannel, MessageUser, Error
from output_builder import BuildTableOutput
from services.input_services import ConvertInput

class ClaimArchetype(commands.GroupCog, name='claim'):
  def __init__(self, bot):
    self.bot = bot

  @app_commands.command(name='limited',
                        description='Enter the deck archetype for a player and their last played limited event')
  @app_commands.guild_only()
  async def ClaimLimited(self, interaction: Interaction, player_name: str,
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
  async def ClaimConstructed(self, interaction: Interaction, player_name: str,
                             archetype: str, date: str):
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
      await interaction.followup.send('Unable to submit the archetype. Please try again later.')
    else:
      message_parts =  f'Submitter: {interaction.user.display_name}'
      message_parts += f'Archetype submitted: {archetype_submitted[3]}'
      message_parts += f'Player: {archetype_submitted[2].title()}'
      message_parts += f'Date: {date}'
      message_parts += f'Store Discord Name: {interaction.guild.name}'
      message_parts += f'Format channel name: {interaction.channel.name}'
      message_parts += f'Format channel id: {interaction.channel_id}'
      message = '\n'.join(message_parts)
      #TODO: As a store, I'd like to utilize a channel to see the stream of claims coming in
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
    phil_message_parts =  f'Error in Claim: {exception.message}'
    phil_message_parts += f'player_name = {player_name}'
    phil_message_parts += f'user_name = {interaction.user.display_name}'
    phil_message_parts += f'archetype = {archetype}'
    phil_message_parts += f'date = {date}'
    phil_message_parts += f'Discord guild name = {interaction.guild.name}'
    phil_message_parts += f'Discord channel name = {interaction.channel.name}'
    
    phil_message = '\n'.join(phil_message_parts)
    await interaction.followup.send(exception.message, ephemeral=True)
    await MessageUser(bot, phil_message, settings.PHILID)
  except Exception as exception:
    await interaction.followup.send("Something unexpected went wrong. It's been reported. Please try again in a few hours.",
                                    ephemeral=True)
    await Error(bot, exception)

async def MessageStoreFeed(bot, message, interaction):
  try:
    ...
  except Exception:
    ...

async def setup(bot):
  await bot.add_cog(ClaimArchetype(bot))
