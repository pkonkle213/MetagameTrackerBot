import os
import pytz
import pathlib
import io
from datetime import datetime
import pandas as pd
import typing
import settings
from checks import isSubmitter
from custom_errors import KnownError
from data_translation import ConvertMessageToData, ConvertCSVToData
from tuple_conversions import Data, Standing, Game
from discord import app_commands, Interaction, Attachment
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

  async def ConvertCSVToDataErrors(self,
                       interaction_objects:Data,
                       interaction:Interaction,
                       csv_file:Attachment):
    save_path, file_name = self.BuildFilePath(interaction, csv_file.filename)
    
    csv_data = await csv_file.read()
    df = pd.read_csv(io.StringIO(csv_data.decode('utf-8')), na_values=['FALSE','False'])
    if df is None or df.empty:
      raise KnownError("The file is empty. Please try again.")
    
    await csv_file.save(pathlib.Path(save_path))
    
    data, errors = ConvertCSVToData(df, interaction_objects.Game)
    #TODO: Add the round number
    filename_split = csv_file.filename.split('-')
    round_number = filename_split[4]
    date = "/".join([filename_split[3][2:4], filename_split[3][4:6], filename_split[3][0:2]])
    print('Date from file:', date)
    return data, errors, round_number, date

  def BuildFilePath(self, interaction:Interaction, prev_filename:str):
    if not interaction.guild:
      raise KnownError("This command can only be used in a server.")
    #Save the file to the server
    timezone = pytz.timezone('US/Eastern')
    timestamp = datetime.now(timezone).strftime("%Y%m%d_%H%M%S")
    file_name = f"{timestamp}_{prev_filename}" if prev_filename != '' else 'ModalInput'
    
    folder_name = f'{interaction.guild.id} - {interaction.guild.name}'
    
    BASE_DIR = pathlib.Path(__file__).parent.parent
    SAVE_DIRECTORY = BASE_DIR / "imported_files" / folder_name
    SAVE_DIRECTORY.mkdir(parents=True, exist_ok=True)
    save_path = os.path.join(SAVE_DIRECTORY, file_name)

    return save_path, file_name

  async def ConvertModalToDataErrors(self,
                       interaction_objects:Data,
                       interaction:Interaction):
    #Get the data from the user
    modal = SubmitDataModal()
    await interaction.response.send_modal(modal)
    await modal.wait()
    
    if not modal.is_submitted:
      raise KnownError("SubmitData modal was dismissed or timed out. Please try again.")

    submission = '\n'.join([f'Date:{modal.submitted_date}',
                            f'Round:{modal.submitted_round}'
                            f'Message:{modal.submitted_message}'])

    save_path, file_name = self.BuildFilePath(interaction, '')

    with open(save_path, 'w') as file:
      file.write(submission)    
    
    #Convert the data to the appropriate format
    data, errors = ConvertMessageToData(modal.submitted_message,
                                        interaction_objects.Game)
    round_number = modal.submitted_round
    date = modal.submitted_date
    return data, errors, round_number, date
  
  @app_commands.command(name="data",
                        description="Submitting your event's data")
  @app_commands.checks.has_role('MTSubmitter')
  @app_commands.guild_only()
  async def SubmitDataCommand(self,
                              interaction: Interaction,
                              csv_file: typing.Optional[Attachment] = None):
    try:
      #Checks to ensure data can be submitted in the current channel
      interaction_objects = SubmitCheck(interaction)

      if csv_file:
        if not csv_file.filename.endswith('.csv'):
          raise KnownError("Please upload a file with a '.csv' extension.")
        data, errors, round_number, date = await self.ConvertCSVToDataErrors(interaction_objects,
                                                                       interaction,
                                                                       csv_file)
      
      else:
        data, errors, round_number, date = await self.ConvertModalToDataErrors(interaction_objects,
                                                                         interaction)
                                                                         
                                                                         
        #TODO: This now needs to work for both CSVs and Modal input
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

    except KnownError as exception:
      await interaction.followup.send(exception.message, ephemeral=True)
    except Exception as exception:
      await Error(self.bot, interaction, exception)

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
