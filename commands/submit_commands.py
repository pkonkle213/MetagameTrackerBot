import typing
import settings
from services.convert_and_save_input import ConvertCSVToDataErrors, ConvertModalToDataErrors
from checks import isSubmitter
from custom_errors import KnownError
from tuple_conversions import  Standing
from discord import app_commands, Interaction, Attachment
from discord.ext import commands
from discord_messages import MessageChannel
from interaction_objects import GetObjectsFromInteraction
from services.add_results_services import SubmitCheck, SubmitData
from services.command_error_service import Error

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

  @app_commands.command(name="data",
                        description="Submitting your event's data")
  @app_commands.checks.has_role('MTSubmitter')
  @app_commands.guild_only()
  async def SubmitDataCommand(self,
                              interaction: Interaction,
                              csv_file: typing.Optional[Attachment] = None):
    #Checks to ensure data can be submitted in the current channel
    interaction_objects = SubmitCheck(interaction)
    
    if csv_file:
      await interaction.response.defer(ephemeral=True)          
      if not csv_file.filename.endswith('.csv'):
        raise KnownError("Please upload a file with a '.csv' extension.")
      data, errors, round_number, date = await ConvertCSVToDataErrors(interaction_objects,
                                                                     interaction,
                                                                     csv_file)
    
    else:
    
      data, errors, round_number, date = await ConvertModalToDataErrors(interaction_objects,
                                                                      interaction)

    if data is None:
      await NewDataMessage(self.bot, interaction, True)
      raise KnownError("Unable to submit due to not recognizing the form data. Please try again.")
  
    #Advise user of submission process starting
    message_type = 'standings' if isinstance(data[0], Standing) else 'pairings'
    await interaction.followup.send(f"Attempting to add {len(data)} {message_type} to event", ephemeral=True)
      
    #Inform user of any errors in submitted data
    if len(errors) > 0:
      await interaction.followup.send('Errors:\n' + '\n'.join(errors), ephemeral=True)
      
    #Inform me of the new event being added
    await NewDataMessage(self.bot, interaction, False)

    #Submit the data to the database. Returning event for an announcement
    output, event_created = SubmitData(interaction_objects,
                                       data,
                                       date,
                                       round_number,
                                       False) #modal.submitted_is_event_complete)
    if output is None:
      raise KnownError("Unable to submit data. Please try again.")
        
    await interaction.followup.send(output, ephemeral=True)
    if event_created:
      await MessageChannel(self.bot,
                           f"New data for {event_created.strftime('%B %-d')}'s event has been submitted! Use the appropriate `/claim` command to input your archetype!",
                             interaction.guild_id,
                             interaction.channel_id)

  @SubmitDataCommand.error
  @SubmitCheck.error
  async def Errors(self,
                   interaction: Interaction,
                   error: app_commands.AppCommandError):
    await Error(self.bot, interaction, error)

async def NewDataMessage(bot:commands.Bot,
                         interaction:Interaction,
                         isError:bool):
  message = f"""
  {'Could not submit data due to error' if isError else 'Successfully received new data'}
    Guild name: {interaction.guild.name}
    Guild id: {interaction.guild.id}
    Channel name: {interaction.channel.name}
    Channel id: {interaction.channel.id}
    Author name: {interaction.user.name}
    Author id: {interaction.user.id}
    """
  await MessageChannel(bot, message, settings.BOTGUILDID, settings.BOTEVENTINPUTID)

async def setup(bot):
  await bot.add_cog(SubmitDataChecker(bot))
