import discord
import settings
from checks import isSubmitter
from custom_errors import KnownError
from data_translation import ConvertMessageToData, Participant
from discord import app_commands, Interaction
from discord.ext import commands
from discord_messages import MessageChannel
from interaction_data import GetInteractionData
from services.add_results_services import SubmitData
from services.command_error_service import Error
from text_modal import SubmitDataModal

#TODO: Instead of this, I'd like to make error reporting better when submitting data
class SubmitDataChecker(commands.GroupCog, name='submit'):
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
      game, format, store, userId = GetInteractionData(interaction)
      if not store:
        issues.append('- Store not registered')
      if not isSubmitter(interaction.guild, interaction.user, 'MTSubmitter'):
        issues.append("- You don't have the MTSubmitter role.")
      if not game:
        issues.append('- Category not mapped to a game')
      if not format:
        issues.append('- Channel not mapped to a format')
      
      if len(issues) == 1:
        await interaction.followup.send('Everything looks good. Please reach out to Phil to test your data')
      else:
        await interaction.followup.send('\n'.join(issues))
    except Exception as exception:
      await Error(self.bot, interaction, exception)

  @app_commands.command(name="data",
                        description="Submitting your event's data")
  @commands.has_role('MTSubmitter')
  @app_commands.guild_only()
  async def SubmitDataCommand(self, interaction: discord.Interaction):
    try:
      modal = SubmitDataModal()
      await interaction.response.send_modal(modal)
      await modal.wait()

      if not modal.is_submitted:
        await interaction.followup.send("SubmitData modal was dismissed or timed out. Please try again", ephemeral=True)
      else:
        data = ConvertMessageToData(modal.submitted_message)
        if data is None:
          await interaction.followup.send("Unable to submit due to not recognizing the form data. Please try again", ephemeral=True)
          await AddDataMessage(self.bot, modal, interaction, settings.ERRORCHANNELID)
        else:
          message_type = 'participants' if isinstance(data[0], Participant) else 'tables'

          await interaction.followup.send(f"Attempting to add {len(data)} {message_type} to event", ephemeral=True)
          await AddDataMessage(self.bot, modal, interaction, settings.BOTEVENTINPUTID)
          output, event_created = await SubmitData(interaction, data, modal.submitted_date)
          await interaction.followup.send(output, ephemeral=True)
          if event_created:
            await MessageChannel(self.bot,
                                 f"New data for {event_created.strftime('%B %d')}'s event have been submitted! Use the `/claim` command to input your archetype!",
                                 interaction.guild_id,
                                 interaction.channel_id)
    except KnownError as exception:
      await interaction.followup.send(exception.message, ephemeral=True)
    except Exception as exception:
      await Error(self.bot, interaction, exception)

async def AddDataMessage(bot, modal, interaction, channel_id):
  message = f"""
    Guild name: {interaction.guild.name}
    Guild id: {interaction.guild.id}
    Channel name: {interaction.channel.name}
    Channel id: {interaction.channel.id}
    Author name: {interaction.user.name}
    Author id: {interaction.user.id}
    Date: {modal.submitted_date}
    Message content:\n{modal.submitted_message}
    """
  await MessageChannel(bot, message, settings.BOTGUILDID, settings.ERRORCHANNELID)

async def setup(bot):
  await bot.add_cog(SubmitDataChecker(bot))
