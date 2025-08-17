import discord
from custom_errors import KnownError
import settings
from discord.ext import commands
from discord import app_commands
from data_translation import ConvertMessageToData, Participant
from discord_messages import MessageChannel
from services.command_error_service import Error
from text_modal import SubmitDataModal
from services.add_results_services import SubmitData

class SubmitDataCommand(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @app_commands.command(name="submitdata",
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
  await MessageChannel(bot, message, settings.BOTGUILD.id, settings.ERRORCHANNELID)

async def setup(bot):
  await bot.add_cog(SubmitDataCommand(bot))