from discord.ext import commands
from discord import app_commands, Interaction
import settings
from services.claim_result_services import ClaimResult, CheckEventPercentage, OneEvent
from custom_errors import KnownError
from discord_messages import MessageChannel, MessageUser, Error
from output_builder import BuildTableOutput
from services.input_services import ConvertInput

#TODO: As a user, I want to discern from claiming a limited deck and a constructed dec
class ClaimArchetype(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @app_commands.command(name='claim',
  description='Enter the deck archetype for a player and their last played event')
  @app_commands.guild_only()
  async def Claim(self, interaction: Interaction,
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
    try:
      archetype_submitted, event = await ClaimResult(interaction, player_name, archetype, date)
      if archetype_submitted is None:
        await interaction.followup.send('Unable to submit the archetype. Please try again later.')
      else:
        message = f'''
        Submitter: {interaction.user.display_name}
        Archetype submitted: {archetype_submitted[3].title()}
        Player: {archetype_submitted[2].title()}
        Date: {date}  
        Store Discord Name: {interaction.guild.name}
        Format channel name: {interaction.channel.name}
        Format channel id: {interaction.channel_id}
        '''
        await MessageChannel(self.bot,
                             message,
                             settings.BOTGUILD.id,
                             settings.CLAIMCHANNEL)
        await interaction.followup.send(f"Thank you for submitting the archetype for {event.EventDate.strftime('%B %d')}'s event!",ephemeral=True)
        followup = CheckEventPercentage(event)
        if followup:
          if followup[1]:
            title, headers, data = OneEvent(event)
            output = BuildTableOutput(title, headers, data)
            await MessageChannel(self.bot,
                                 output,
                                 interaction.guild_id,
                                 interaction.channel_id)
          else:
            await MessageChannel(self.bot,
                                 followup[0],
                                 interaction.guild_id,
                                 interaction.channel_id)
    except ValueError:
      await interaction.followup.send("The date provided doesn't match the MM/DD/YYYY formatting. Please try again", ephemeral=True)
    except KnownError as exception:
      phil_message = f'''
      Error in Claim: {exception.message}
      player_name = {player_name}
      user_name = {interaction.user.display_name}
      archetype = {archetype}
      date = {date}
      Discord guild name = {interaction.guild.name}
      Discord channel name = {interaction.channel.name}
      '''
      await interaction.followup.send(exception.message, ephemeral=True)
      await MessageUser(self.bot, phil_message, settings.PHILID)
    except Exception as exception:  
      await interaction.followup.send("Something unexpected went wrong. It's been reported. Please try again in a few hours.", ephemeral=True)
      await Error(self.bot, exception)

async def setup(bot):
  await bot.add_cog(ClaimArchetype(bot))