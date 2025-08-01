import discord
from custom_errors import KnownError
import settings
from discord.ext import commands
from discord import app_commands
from data_translation import ConvertMessageToParticipants, Participant
from discord_messages import MessageChannel, ErrorMessage
from text_modal import SubmitDataModal
from services.add_results_services import SubmitData

#TODO: As a user, I would like to know why someone wasn't added to database
#I'd like a report with reasons why and identification of rows/tables failed

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
        data = ConvertMessageToParticipants(modal.submitted_message)
        if data is None:
          await interaction.followup.send("Unable to submit due to not recognizing the form data. Please try again", ephemeral=True)
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
          await ErrorMessage(self.bot, modal.submitted_message)
        else:
          date = modal.submitted_date
  
          message_type = 'participants' if isinstance(data[0], Participant) else 'tables'
    
          await interaction.followup.send(f"Attempting to add {len(data)} {message_type} to event", ephemeral=True)
          msg  = f"""
          Guild name: {interaction.guild.name}
          Guild id: {interaction.guild.id}
          Channel name: {interaction.channel.name}
          Channel id: {interaction.channel.id}
          Author name: {interaction.user.name}
          Author id: {interaction.user.id}
          Date: {date}
          Message content:\n{modal.submitted_message}
          """
          await MessageChannel(self.bot, msg, settings.BOTGUILD.id, settings.BOTEVENTINPUTID)
          output, event_created = await SubmitData(interaction, data, date)
          await interaction.followup.send(output, ephemeral=True)
          if event_created:
            await MessageChannel(self.bot,
                                 f"New data for {event_created.strftime('%B %d')}'s event have been submitted! Use the `/claim` command to input your archetype!",
                                 interaction.guild_id,
                                 interaction.channel_id)
    except KnownError as exception:
      await interaction.followup.send(exception.message, ephemeral=True)
    except Exception as exception:
      await interaction.followup.send("Something unexpected went wrong. It's been reported. Please try again in a few hours.", ephemeral=True)
      await ErrorMessage(self.bot, exception)


async def setup(bot):
  await bot.add_cog(SubmitDataCommand(bot))