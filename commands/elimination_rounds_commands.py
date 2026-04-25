from checks import IsStore
from discord import app_commands, Interaction
from discord.ext import commands
from interaction_objects import GetObjectsFromInteraction
from input_modals.event_selector import EventSelector
from services.command_error_service import KnownError
from services.elimination_rounds_services import GetEliminationRoundData
from services.command_error_service import Error
from tuple_conversions import EventType

class EliminationRoundsCommands(commands.GroupCog, name='elimination_rounds'):
  """A group of commands to view elimination rounds"""
  def __init__(self, bot):
    self.bot = bot

  @app_commands.command(name="view",
                        description="View the elimination rounds for an event")
  @app_commands.guild_only()
  @app_commands.checks.cooldown(1, 60.0, key=lambda i: (i.guild_id, i.user.id))
  @IsStore()
  async def EliminationRounds(self,
                              interaction:Interaction):
    #Get the tournaments
    objects = GetObjectsFromInteraction(interaction)
    if not objects.store or not objects.game or not objects.format:
      raise KnownError('No store, game, or format found.')

    modal = EventSelector(objects.store, objects.game, objects.format, event_type=EventType.Tournament.value)

    await interaction.response.send_modal(modal)
    await modal.wait()

    if not modal.is_submitted:
      await interaction.followup.send('Modal not submitted')

    output = GetEliminationRoundData(modal.event)
    
    #Return output to the user
    await interaction.followup.send(output)

  @EliminationRounds.error
  async def Errors(self,
                   interaction: Interaction,
                    error: app_commands.AppCommandError):
     await Error(self.bot, interaction, error)

async def setup(bot):
   await bot.add_cog(EliminationRoundsCommands(bot))