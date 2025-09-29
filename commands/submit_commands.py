import settings
from checks import isSubmitter
from custom_errors import KnownError
from data_translation import ConvertMessageToData
from tuple_conversions import Standing
from discord import app_commands, Interaction
from discord.ext import commands
from discord_messages import MessageChannel
from interaction_objects import GetObjectsFromInteraction
from services.add_results_services import SubmitCheck, SubmitData
from services.command_error_service import Error
from text_modal import SubmitDataModal

class SubmitDataChecker(commands.GroupCog, name='submit'):
  """A group of commands to submit data"""
  def __init__(self, bot):
    self.bot = bot

  @app_commands.command(name="check",
    description="To test if you can submit data")
  @app_commands.guild_only()
  @app_commands.checks.has_role('MTSubmitter')
  async def SubmitCheck(self, interaction: Interaction):
    await interaction.response.defer(ephemeral=True)
    try:
      issues = ['Issues I detect:']
      interactionData = GetObjectsFromInteraction(interaction)
      game = interactionData.Game
      format = interactionData.Format
      store = interactionData.Store
      if not store:
        issues.append('- Store not registered')
      if not isSubmitter(interaction.guild, interaction.user, 'MTSubmitter'):
        issues.append("- You don't have the MTSubmitter role.")
      if not game:
        issues.append('- Category not mapped to a game')
      if not game.HasFormats and not format:
        issues.append('- Channel not mapped to a format')
      
      if len(issues) == 1:
        await interaction.followup.send('Everything looks good. Please reach out to Phil to test your data')
      else:
        await interaction.followup.send('\n'.join(issues))
    except KnownError as exception:
      await interaction.followup.send(exception.message, ephemeral=True)
    except Exception as exception:
      await Error(self.bot, interaction, exception)

  @app_commands.command(name="data",
                        description="Submitting your event's data")
  @commands.has_role('MTSubmitter')
  @app_commands.guild_only()
  async def SubmitDataCommand(self, interaction: Interaction):
    try:
      #Checks to ensure data can be submitted in the current channel
      interaction_objects = SubmitCheck(interaction)

      #Get the data from the user
      modal = SubmitDataModal()
      await interaction.response.send_modal(modal)
      await modal.wait()

      if not modal.is_submitted:
        raise KnownError("SubmitData modal was dismissed or timed out. Please try again.")

      #Convert the data to the appropriate format
      data, errors = ConvertMessageToData(interaction, modal.submitted_message, interaction_objects.Game)
      if data is None:
        await AddDataMessage(self.bot,
                              modal.submitted_date,
                              modal.submitted_message,
                             interaction,
                             settings.ERRORCHANNELID,
                             True)
        raise KnownError("Unable to submit due to not recognizing the form data. Please try again.")

      #Advise user of submission process starting
      message_type = 'standings' if isinstance(data[0], Standing) else 'pairings'
      await interaction.followup.send(f"Attempting to add {len(data)} {message_type} to event", ephemeral=True)
      
      #Inform user of any errors in submitted data
      if len(errors) > 0:
        await interaction.followup.send('Errors:\n' + '\n'.join(errors), ephemeral=True)
      
      #Inform me of the new event being added
      await AddDataMessage(self.bot,
                           modal.submitted_date,
                           modal.submitted_message,
                           interaction,
                           settings.BOTEVENTINPUTID,
                           False)

      #Submit the data to the database. Returning event for an announcement
      output, event_created = SubmitData(interaction_objects,
                                         data,
                                         modal.submitted_date)
      if output is None:
        raise KnownError("Unable to submit data. Please try again.")
        
      await interaction.followup.send(output, ephemeral=True)
      if event_created:
        print('New event created')
        print('GuildId:', interaction.guild_id)
        print('ChannelId:', interaction.channel_id)
        await MessageChannel(self.bot,
                             f"New data for {event_created.strftime('%B %-d')}'s event have been submitted! Use the appropriate `/claim` command to input your archetype!",
                             interaction.guild_id,
                             interaction.channel_id)
        print('Channel message sent')
    except KnownError as exception:
      await interaction.followup.send(exception.message, ephemeral=True)
    except Exception as exception:
      await Error(self.bot, interaction, exception)

async def AddDataMessage(bot, date, message, interaction, channel_id, isError):
  message = f"""
  {'Could not submit data due to error' if isError else 'Submitted data'}
    Guild name: {interaction.guild.name}
    Guild id: {interaction.guild.id}
    Channel name: {interaction.channel.name}
    Channel id: {interaction.channel.id}
    Author name: {interaction.user.name}
    Author id: {interaction.user.id}
    Date: {date}
    Message content:\n{message}
    """
  await MessageChannel(bot, message, settings.BOTGUILDID, channel_id)

async def setup(bot):
  await bot.add_cog(SubmitDataChecker(bot))
